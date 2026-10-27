"""Offline transport and actual UI flow tests; all model responses/reviews are fixtures."""
import json
from pathlib import Path
import pytest
import requests
from streamlit.testing.v1 import AppTest

from frontierlab import pipeline, research_backend
from frontierlab.models import Paper
from frontierlab.openweight import OpenWeightClient
from frontierlab.reporting import export_json
from frontierlab.review import review_packet, save_review
from frontierlab.research_backend import CallBudget, NvidiaResearchClient

APP = Path(__file__).resolve().parents[1] / "app.py"


class Response:
    status_code = 200
    def __init__(self, body): self.body = body
    def json(self): return self.body


class Transport:
    def __init__(self):
        self.calls = []
        self.roles = []
        self.override = None
        self.finish = "stop"
        self.model = "meta/muse-glimmer-30b"
        self.trust_env = True

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        text = kwargs["json"]["messages"][-1]["content"]
        role = text.split("\nROLE: ", 1)[1].split("\nTASK:", 1)[0]
        payload = json.loads(text.split("\nSOURCE DATA:\n", 1)[1])
        self.roles.append(role)
        if role == "Evidence Extraction Agent":
            answer = {"claims": [{"paper_id": payload["paper"]["paper_id"],
                "claim_key": "assay-conditions", "stance": "supports",
                "statement": "A fictional assay response depends on conditions.",
                "limitation": "Artificial fixture only.",
                "evidence_quote": payload["paper"]["abstract"]}]}
        elif role == "Adversarial Skeptic Agent":
            answer = {"explanation": "Mock uncertainty.", "uncertainties": ["No experiment."]}
        elif role == "Hypothesis Agent":
            answer = {"hypotheses": [{"text": "Mock condition-dependence test.",
                "evidence_ids": ["PMID:1", "PMID:2"], "rationale": "Mock rationale."}]}
        elif role == "Method Evaluation Agent":
            answer = {"candidates": [{"name": f"Mock strategy {i}", "evidence_ids": [f"PMID:{i}"],
                "scope": "Mock assay context.",
                "comparison": {k: "Unknown; inspect original methods."
                 for k in ("expected_value", "resources", "validation", "limitations", "novelty")}}
                for i in (1, 2)]}
        elif role == "Scientific Planning Agent":
            answer = {"objective": "Mock objective", "steps": ["Inspect missing documentation."],
                "controls": ["Mock negative control"], "metrics": ["Mock assay metric"],
                "replication": ["Independent repeats"], "falsification": ["Effect disappears."],
                "evidence_ids": ["PMID:1"], "limitations": "Not executed."}
        else:
            raise AssertionError(role)
        content = self.override if self.override is not None else json.dumps(answer)
        return Response({"model": self.model, "choices": [{"finish_reason": self.finish,
            "message": {"content": content}}], "usage": {"prompt_tokens": 10,
            "completion_tokens": 20, "total_tokens": 30}})


def papers():
    return [Paper(f"PMID:{i}", f"Artificial paper {i}", "2026", "Mock author",
        "A fictional assay response depended on the experimental conditions.",
        f"https://example.org/{i}") for i in (1, 2)]


def client(monkeypatch, transport=None, budget=None):
    monkeypatch.setenv("FRONTIERLAB_NIM_RESEARCH", "YES")
    return NvidiaResearchClient(authorized=True, key="DUMMY-PRIVATE-KEY",
        session=transport or Transport(), budget=budget or CallBudget(8))


def test_backend_requires_server_opt_in_and_session_authorization(monkeypatch):
    monkeypatch.delenv("FRONTIERLAB_NIM_RESEARCH", raising=False)
    with pytest.raises(PermissionError):
        NvidiaResearchClient(authorized=True, key="DUMMY")
    monkeypatch.setenv("FRONTIERLAB_NIM_RESEARCH", "YES")
    with pytest.raises(PermissionError):
        NvidiaResearchClient(authorized=False, key="DUMMY")


def test_budget_is_shared_across_clients_and_blocks_before_http(monkeypatch):
    budget = CallBudget(2)
    t1, t2 = Transport(), Transport()
    a, b = client(monkeypatch, t1, budget), client(monkeypatch, t2, budget)
    a.json("Hypothesis Agent", "Mock task", {})
    b.json("Hypothesis Agent", "Mock task", {})
    with pytest.raises(PermissionError, match="budget"):
        a.json("Hypothesis Agent", "Mock task", {})
    assert len(t1.calls) == len(t2.calls) == 1
    assert budget.remaining == 0


@pytest.mark.parametrize("text", ['[]', '{"a":1,"a":2}', '{"a":NaN}', 'not JSON'])
def test_invalid_json_consumes_one_call_without_retry_or_body_leak(monkeypatch, text):
    transport = Transport()
    transport.override = text
    obj = client(monkeypatch, transport)
    with pytest.raises(RuntimeError, match="no automatic retry"):
        obj.json("Hypothesis Agent", "Mock task", {})
    assert len(transport.calls) == 1
    assert obj.provenance["receipts"][0]["status"] == "FAILED_NO_RETRY"
    assert "DUMMY-PRIVATE-KEY" not in json.dumps(obj.provenance)


@pytest.mark.parametrize("finish,model", [("length", "meta/muse-glimmer-30b"), ("stop", None)])
def test_truncation_or_missing_identity_is_not_a_success(monkeypatch, finish, model):
    transport = Transport()
    transport.finish, transport.model = finish, model
    obj = client(monkeypatch, transport)
    with pytest.raises(RuntimeError):
        obj.json("Hypothesis Agent", "Mock task", {})
    assert len(transport.calls) == 1


def test_unknown_role_is_rejected_before_budget_or_request(monkeypatch):
    transport = Transport()
    obj = client(monkeypatch, transport)
    with pytest.raises(ValueError, match="role"):
        obj.json("Arbitrary remote task", "Mock task", {})
    assert not transport.calls and obj.provenance["attempted_calls"] == 0


def test_live_run_preserves_backend_and_stops_before_human_review(monkeypatch):
    transport = Transport()
    obj = client(monkeypatch, transport)
    run = pipeline.run_research("Mock question", "x", mode="live", model_client=obj,
                               retrieve=lambda q,n: papers())
    assert run.backend == "nvidia-nim" and run.inference is obj.provenance
    assert transport.roles == ["Evidence Extraction Agent"] * 2
    assert run.skeptic["decision"] == "HUMAN_CLAIM_REVIEW_REQUIRED"
    assert not run.hypotheses and run.plan is None
    assert "DUMMY-PRIVATE-KEY" not in export_json(run)
    cases = review_packet(run)["cases"]
    save_review(run, [{"case_id": c["case_id"], "review_label": "SUPPORTED"} for c in cases])
    with pytest.raises(PermissionError, match="original"):
        pipeline.continue_after_review(run, model_client=OpenWeightClient(session=Transport()))
    assert len(transport.calls) == 2


def configure_ui(monkeypatch):
    transport = Transport()
    created = []
    monkeypatch.setenv("FRONTIERLAB_NIM_RESEARCH", "YES")
    monkeypatch.setenv("NVIDIA_API_KEY", "DUMMY-PRIVATE-KEY")
    original_class = NvidiaResearchClient
    def factory(*, authorized=False):
        obj = original_class(authorized=authorized, session=transport, budget=CallBudget(8))
        created.append(obj)
        return obj
    monkeypatch.setattr(research_backend, "NvidiaResearchClient", factory)
    original_run = pipeline.run_research
    def run(*args, **kwargs):
        return original_run(*args, **kwargs, retrieve=lambda q,n: papers())
    monkeypatch.setattr(pipeline, "run_research", run)
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    app.radio[0].set_value("Live Europe PMC + Meta via NVIDIA").run()
    return app, transport, created


def btn(app, label):
    return next(b for b in app.button if b.label == label)


def test_nim_ui_reuses_one_client_through_all_five_stages(monkeypatch):
    app, transport, created = configure_ui(monkeypatch)
    assert btn(app, "Run research audit").disabled
    app.checkbox[0].check().run()
    btn(app, "Run research audit").click().run()
    assert not app.exception and transport.roles == ["Evidence Extraction Agent"] * 2
    for choice in app.selectbox:
        if choice.label == "Reviewer judgment": choice.select("SUPPORTED")
    btn(app, "Save human review judgments").click().run()
    btn(app, "Resume model synthesis after human review").click().run()
    btn(app, "Suggest methods with this run's Meta backend").click().run()
    next(x for x in app.selectbox if x.label == "Researcher decision").select("M1")
    next(x for x in app.text_area if x.label.startswith("Why select")).set_value(
        "Mock selection for an offline UI integration test.")
    btn(app, "Save method evaluation").click().run()
    next(x for x in app.checkbox if x.label.startswith("I have reviewed")).check().run()
    btn(app, "Generate cited plan").click().run()
    assert not app.exception and len(created) == 1
    assert len(transport.calls) == 6
    run = app.session_state["frontier_result"]
    assert run.backend == "nvidia-nim" and run.plan["status"] == "DRAFT_FOR_RESEARCHER_REVIEW"
    assert run.inference["attempted_calls"] == 6
    assert "DUMMY-PRIVATE-KEY" not in export_json(run)


def test_nim_ui_revoking_consent_blocks_continuation(monkeypatch):
    app, transport, _ = configure_ui(monkeypatch)
    app.checkbox[0].check().run()
    btn(app, "Run research audit").click().run()
    for choice in app.selectbox:
        if choice.label == "Reviewer judgment": choice.select("SUPPORTED")
    btn(app, "Save human review judgments").click().run()
    next(c for c in app.checkbox if c.key == "nim_research_consent").uncheck().run()
    assert btn(app, "Resume model synthesis after human review").disabled
    assert len(transport.calls) == 2


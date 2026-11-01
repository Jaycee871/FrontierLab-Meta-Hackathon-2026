"""Live Meta Muse via Hugging Face Inference Providers: fully mocked, no network.

The OpenAI client is replaced by an in-memory fake in every test; no real model
API call is made. The dummy token below is not a real credential.
"""
import json
from pathlib import Path
from types import SimpleNamespace

import httpx
import openai
import pytest
from streamlit.testing.v1 import AppTest

from frontierlab import hf_providers, pipeline
from frontierlab.hf_providers import (
    FALLBACK_MODEL, PRIMARY_MODEL, ROUTER_URL, DailyBudget, HFMuseResearchClient,
    HFProvidersUnavailable, SessionBudget,
)
from frontierlab.models import Paper
from frontierlab.reporting import export_json
from frontierlab.review import review_packet, save_review

APP = Path(__file__).resolve().parents[1] / "app.py"
DUMMY_TOKEN = "hf_DUMMY_TEST_TOKEN_never_real_0123456789"
TOKEN_VARS = ("HF_TOKEN", "HF_INFERENCE_TOKEN", "HUGGINGFACEHUB_API_TOKEN")
ABSTRACT = "A fictional assay response depended on the experimental conditions."


def papers():
    return [Paper(f"PMID:{i}", f"Artificial paper {i}", "2026", "Mock author", ABSTRACT,
                  f"https://example.org/{i}") for i in (1, 2)]


def _answer(role, payload, quote=None):
    if role == "Evidence Extraction Agent":
        return {"claims": [{"paper_id": payload["paper"]["paper_id"], "claim_key": "assay-conditions",
                            "stance": "supports", "statement": "A fictional response depends on conditions.",
                            "limitation": "Artificial fixture only.",
                            "evidence_quote": quote if quote is not None else payload["paper"]["abstract"]}]}
    if role == "Adversarial Skeptic Agent":
        return {"explanation": "Mock uncertainty.", "uncertainties": ["No experiment."]}
    if role == "Hypothesis Agent":
        return {"hypotheses": [{"text": "Mock condition-dependence test.",
                                "evidence_ids": ["PMID:1", "PMID:2"], "rationale": "Mock rationale."}]}
    raise AssertionError(role)


class FakeOpenAI:
    """Mimics client.chat.completions.with_raw_response.create(...).parse()."""

    def __init__(self, fail_models=(), quote=None, reported=None, finish="stop", provider_header=None):
        self.calls = []
        self.fail_models = set(fail_models)
        self.quote = quote
        self.reported = reported
        self.finish = finish
        self.provider_header = provider_header
        self.chat = SimpleNamespace(completions=SimpleNamespace(
            with_raw_response=SimpleNamespace(create=self._create)))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        base = kwargs["model"].split(":", 1)[0]
        if base in self.fail_models:
            raise openai.APITimeoutError(request=httpx.Request("POST", ROUTER_URL + "/chat/completions"))
        text = kwargs["messages"][-1]["content"]
        role = text.split("\nROLE: ", 1)[1].split("\nTASK:", 1)[0]
        payload = json.loads(text.split("\nSOURCE DATA:\n", 1)[1])
        content = json.dumps(_answer(role, payload, self.quote))
        completion = SimpleNamespace(
            model=self.reported if self.reported is not None else base,
            choices=[SimpleNamespace(finish_reason=self.finish, message=SimpleNamespace(content=content))],
            usage=SimpleNamespace(prompt_tokens=11, completion_tokens=22, total_tokens=33),
        )
        headers = {"x-inference-provider": self.provider_header} if self.provider_header else {}
        return SimpleNamespace(headers=headers, parse=lambda: completion)

    def models(self):
        return [c["model"] for c in self.calls]


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    for name in TOKEN_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv(hf_providers.DAILY_CAP_ENV, raising=False)
    monkeypatch.setattr(hf_providers, "_DAILY_BUDGET", DailyBudget())

    def no_network(**kwargs):
        raise AssertionError("A real OpenAI client must never be built in tests")
    monkeypatch.setattr(hf_providers, "OpenAI", no_network)


def make(fake=None, session=None, daily=None):
    return HFMuseResearchClient(authorized=True, token=DUMMY_TOKEN, client=fake or FakeOpenAI(),
                                session_budget=session or SessionBudget(), daily=daily or DailyBudget(60))


def test_router_url_and_model_ids_are_exact():
    assert ROUTER_URL == "https://router.huggingface.co/v1"
    assert PRIMARY_MODEL == "meta-models/Muse-Spark-Open-816B-A42B"
    assert FALLBACK_MODEL == "meta-models/Muse-Glimmer-30B"


def test_default_client_targets_hf_router_without_sdk_retries(monkeypatch):
    seen = {}
    monkeypatch.setattr(hf_providers, "OpenAI", lambda **kw: seen.update(kw) or FakeOpenAI())
    monkeypatch.setenv("HF_INFERENCE_TOKEN", DUMMY_TOKEN)
    HFMuseResearchClient(authorized=True)
    assert seen["base_url"] == ROUTER_URL and seen["max_retries"] == 0 and seen["api_key"] == DUMMY_TOKEN


def test_token_resolution_order_and_absence(monkeypatch):
    assert hf_providers.hf_token() is None
    available, reason = hf_providers.live_status()
    assert not available and "HF_TOKEN" in reason
    monkeypatch.setenv("HUGGINGFACEHUB_API_TOKEN", "third")
    monkeypatch.setenv("HF_TOKEN", "  ")
    assert hf_providers.hf_token() == "third"
    monkeypatch.setenv("HF_INFERENCE_TOKEN", "second")
    assert hf_providers.hf_token() == "second"
    monkeypatch.setenv("HF_TOKEN", "first")
    assert hf_providers.hf_token() == "first"
    assert hf_providers.live_status()[0]
    assert "first" not in hf_providers.live_status()[1]


def test_client_requires_consent_and_token():
    with pytest.raises(PermissionError, match="consent"):
        HFMuseResearchClient(authorized=False, token=DUMMY_TOKEN, client=FakeOpenAI())
    with pytest.raises(PermissionError, match="token"):
        HFMuseResearchClient(authorized=True, client=FakeOpenAI())


def test_success_path_uses_spark_and_records_receipt():
    fake = FakeOpenAI(provider_header="baseten")
    obj = make(fake)
    answer = obj.json("Hypothesis Agent", "Mock task", {"question": "q"})
    assert answer["hypotheses"]
    call = fake.calls[0]
    assert call["model"] == PRIMARY_MODEL + ":baseten"
    assert call["max_tokens"] == hf_providers.MAX_TOKENS <= 2048
    assert call["temperature"] <= 0.3 and call["timeout"] == 60.0 and call["stream"] is False
    receipt = obj.provenance["receipts"][0]
    assert receipt["status"] == "JSON_OBJECT_RETURNED"
    assert receipt["requested_model"] == PRIMARY_MODEL and receipt["provider_reported"] == "baseten"
    assert receipt["usage"] == {"prompt_tokens": 11, "completion_tokens": 22, "total_tokens": 33}
    assert receipt["started_at_utc"] and receipt["finished_at_utc"] and receipt["elapsed_seconds"] >= 0
    assert receipt["model_identity"] == "MATCHED"
    assert obj.model == PRIMARY_MODEL and obj.provenance["attempted_calls"] == 1


def test_spark_failure_falls_back_to_glimmer():
    fake = FakeOpenAI(fail_models={PRIMARY_MODEL})
    obj = make(fake)
    obj.json("Hypothesis Agent", "Mock task", {})
    assert fake.models() == [PRIMARY_MODEL + ":baseten", FALLBACK_MODEL]
    first, second = obj.provenance["receipts"]
    assert first["status"] == "FAILED_FALLBACK_NEXT" and first["error"] == "APITimeoutError"
    assert second["status"] == "JSON_OBJECT_RETURNED" and second["requested_model"] == FALLBACK_MODEL
    assert obj.model == FALLBACK_MODEL and obj.provenance["attempted_calls"] == 2


@pytest.mark.parametrize("kwargs", [{"reported": "some-other/model-7b"}, {"finish": "length"}])
def test_identity_mismatch_or_truncation_is_not_success(kwargs):
    fake = FakeOpenAI(**kwargs)
    obj = make(fake)
    with pytest.raises(HFProvidersUnavailable):
        obj.json("Hypothesis Agent", "Mock task", {})
    assert len(fake.calls) == 2
    assert all(r["status"].startswith("FAILED") for r in obj.provenance["receipts"])


def test_both_fail_raises_plain_message_pointing_to_replay():
    obj = make(FakeOpenAI(fail_models={PRIMARY_MODEL, FALLBACK_MODEL}))
    with pytest.raises(HFProvidersUnavailable) as info:
        obj.json("Hypothesis Agent", "Mock task", {})
    message = str(info.value)
    assert "Replay recorded real M2 case" in message and "No model output was used" in message
    assert [r["status"] for r in obj.provenance["receipts"]] == ["FAILED_FALLBACK_NEXT", "FAILED"]


def test_session_cap_blocks_before_any_request_and_counts_fallbacks():
    fake = FakeOpenAI(fail_models={PRIMARY_MODEL})
    session = SessionBudget(hf_providers.SESSION_CALL_CAP)
    obj = make(fake, session=session)
    for _ in range(3):
        obj.json("Hypothesis Agent", "Mock task", {})
    assert session.remaining == 0 and len(fake.calls) == 6
    with pytest.raises(PermissionError, match="session cap"):
        obj.json("Hypothesis Agent", "Mock task", {})
    assert len(fake.calls) == 6
    # A fresh client in the same session shares the cap.
    with pytest.raises(PermissionError, match="session cap"):
        make(fake, session=session).json("Hypothesis Agent", "Mock task", {})
    assert len(fake.calls) == 6
    with pytest.raises(ValueError):
        SessionBudget(hf_providers.SESSION_CALL_CAP + 1)


def test_daily_cap_from_env_is_shared_and_rolls_over(monkeypatch):
    monkeypatch.setenv(hf_providers.DAILY_CAP_ENV, "2")
    day = {"v": "2026-11-01"}
    daily = DailyBudget(clock=lambda: day["v"])
    fake = FakeOpenAI()
    a, b = make(fake, daily=daily), make(fake, daily=daily)
    a.json("Hypothesis Agent", "Mock task", {})
    b.json("Hypothesis Agent", "Mock task", {})
    with pytest.raises(PermissionError, match="daily cap"):
        a.json("Hypothesis Agent", "Mock task", {})
    assert len(fake.calls) == 2
    day["v"] = "2026-11-02"
    assert daily.remaining == 2
    monkeypatch.setenv(hf_providers.DAILY_CAP_ENV, "not-a-number")
    assert hf_providers.daily_cap() == hf_providers.DEFAULT_DAILY_CALL_CAP


def test_unknown_role_and_oversized_input_rejected_before_budget():
    fake = FakeOpenAI()
    session = SessionBudget()
    obj = make(fake, session=session)
    with pytest.raises(ValueError, match="role"):
        obj.json("Arbitrary remote task", "Mock task", {})
    with pytest.raises(ValueError, match="too long"):
        obj.json("Hypothesis Agent", "Mock task", {"claims": ["x" * 20000]})
    assert not fake.calls and session.remaining == session.limit


def test_long_abstract_is_truncated_but_quotes_checked_against_full_abstract():
    long_abstract = ABSTRACT + " " + ("Filler sentence about unrelated details. " * 200)
    fake = FakeOpenAI()
    obj = make(fake)
    paper = Paper("PMID:9", "Long", "2026", "Mock", long_abstract, "https://example.org/9")
    obj.json("Evidence Extraction Agent", "Mock task",
             {"question": "q", "paper": {"paper_id": "PMID:9", "abstract": long_abstract}})
    sent = json.loads(fake.calls[0]["messages"][-1]["content"].split("\nSOURCE DATA:\n", 1)[1])
    assert len(sent["paper"]["abstract"]) == hf_providers.MAX_ABSTRACT_CHARS
    assert long_abstract.startswith(sent["paper"]["abstract"])
    assert obj.provenance["receipts"][0]["input_abstract_truncated"] is True
    assert paper.abstract == long_abstract  # caller data untouched


def test_evidence_gate_still_rejects_non_verbatim_quotes():
    fake = FakeOpenAI(quote="This sentence was never written in the abstract at all.")
    run = pipeline.run_research("Mock question", "x", mode="live", model_client=make(fake),
                                retrieve=lambda q, n: papers())
    assert not run.audit.verified_claims and len(run.audit.rejected_claims) == 2
    assert all("verbatim" in r["reason"] for r in run.audit.rejected_claims)
    assert run.skeptic["decision"] == "INSUFFICIENT_EVIDENCE" and not run.hypotheses


def test_live_run_is_human_gated_and_token_never_exported():
    fake = FakeOpenAI(fail_models={PRIMARY_MODEL})
    obj = make(fake)
    run = pipeline.run_research("Mock question", "x", mode="live", model_client=obj,
                                retrieve=lambda q, n: papers())
    assert run.backend == hf_providers.BACKEND and run.inference is obj.provenance
    assert len(run.audit.verified_claims) == 2
    assert run.skeptic["decision"] == "HUMAN_CLAIM_REVIEW_REQUIRED" and not run.hypotheses
    with pytest.raises(PermissionError):
        pipeline.continue_after_review(run, model_client=obj)  # review still pending
    save_review(run, [{"case_id": c["case_id"], "review_label": "SUPPORTED"}
                      for c in review_packet(run)["cases"]])
    assert obj.session_remaining == 2  # 2 extractions x (Spark fail + Glimmer) = 4 attempts
    obj.json("Hypothesis Agent", "x", {})
    with pytest.raises(PermissionError, match="session cap"):
        obj.json("Hypothesis Agent", "x", {})
    exported = export_json(run)
    assert DUMMY_TOKEN not in exported and DUMMY_TOKEN not in json.dumps(obj.provenance)
    assert DUMMY_TOKEN not in repr(obj)
    assert json.loads(exported)["inference"]["receipts"][0]["requested_model"] == PRIMARY_MODEL


def test_reviewed_continuation_runs_skeptic_and_hypothesis_on_spark():
    fake = FakeOpenAI()
    obj = make(fake)
    run = pipeline.run_research("Mock question", "x", mode="live", model_client=obj,
                                retrieve=lambda q, n: papers())
    save_review(run, [{"case_id": c["case_id"], "review_label": "SUPPORTED"}
                      for c in review_packet(run)["cases"]])
    pipeline.continue_after_review(run, model_client=obj)
    assert len(fake.calls) == 4 and run.hypotheses
    roles = [r["role"] for r in run.inference["receipts"]]
    assert roles[-2:] == ["Adversarial Skeptic Agent", "Hypothesis Agent"]


# ---------------------------------------------------------------- Streamlit UI

def configure_ui(monkeypatch, fake, token=True):
    if token:
        monkeypatch.setenv("HF_TOKEN", DUMMY_TOKEN)
    monkeypatch.setattr(hf_providers, "OpenAI", lambda **kw: fake)
    original_run = pipeline.run_research

    def run(*args, **kwargs):
        return original_run(*args, **kwargs, retrieve=lambda q, n: papers())
    monkeypatch.setattr(pipeline, "run_research", run)
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.radio[0].set_value(hf_providers.MODE_LABEL).run()
    return app


def btn(app, label):
    return next(b for b in app.button if b.label == label)


def all_text(app):
    parts = []
    for group in (app.markdown, app.caption, app.info, app.warning, app.error, app.success, app.json,
                  app.sidebar.markdown, app.sidebar.caption, app.sidebar.info, app.sidebar.warning):
        parts.extend(str(e.value) for e in group)
    return "\n".join(parts)


def test_ui_without_token_shows_mode_unavailable(monkeypatch):
    fake = FakeOpenAI()
    app = configure_ui(monkeypatch, fake, token=False)
    assert not app.exception
    assert any("Live Meta Muse (via Hugging Face) · unavailable" in o for o in app.radio[0].options)
    consent = next(c for c in app.checkbox if c.key == "hf_live_consent")
    assert consent.disabled and btn(app, "Run research audit").disabled
    assert any("no Hugging Face token" in w.value for w in app.sidebar.warning)
    assert not fake.calls


def test_ui_consent_gates_run_and_full_reviewed_flow(monkeypatch):
    fake = FakeOpenAI(provider_header="baseten")
    app = configure_ui(monkeypatch, fake)
    assert app.radio[0].value == hf_providers.MODE_LABEL
    assert btn(app, "Run research audit").disabled  # consent not given yet
    consent = next(c for c in app.checkbox if c.key == "hf_live_consent")
    assert consent.label == hf_providers.CONSENT_LABEL
    consent.check().run()
    assert not btn(app, "Run research audit").disabled
    btn(app, "Run research audit").click().run()
    assert not app.exception and len(fake.calls) == 2
    for choice in app.selectbox:
        if choice.label == "Reviewer judgment":
            choice.select("SUPPORTED")
    btn(app, "Save human review judgments").click().run()
    btn(app, "Resume model synthesis after human review").click().run()
    assert not app.exception and len(fake.calls) == 4
    run = app.session_state["frontier_result"]
    assert run.backend == hf_providers.BACKEND and run.hypotheses
    assert app.session_state["hf_session_budget"].remaining == 2
    assert DUMMY_TOKEN not in all_text(app) and DUMMY_TOKEN not in export_json(run)
    # Revoking consent removes the live client from every later step.
    next(c for c in app.checkbox if c.key == "hf_live_consent").uncheck().run()
    assert btn(app, "Suggest methods with this run's Meta backend").disabled


def test_ui_both_models_fail_shows_plain_message(monkeypatch):
    fake = FakeOpenAI(fail_models={PRIMARY_MODEL, FALLBACK_MODEL})
    app = configure_ui(monkeypatch, fake)
    next(c for c in app.checkbox if c.key == "hf_live_consent").check().run()
    btn(app, "Run research audit").click().run()
    assert not app.exception
    assert any(e.value == hf_providers.BOTH_FAILED_MESSAGE for e in app.error)
    assert "frontier_result" not in app.session_state
    assert len(fake.calls) == 2 and DUMMY_TOKEN not in all_text(app)


def test_ui_session_cap_disables_run(monkeypatch):
    fake = FakeOpenAI(fail_models={PRIMARY_MODEL, FALLBACK_MODEL})
    app = configure_ui(monkeypatch, fake)
    next(c for c in app.checkbox if c.key == "hf_live_consent").check().run()
    for _ in range(3):
        btn(app, "Run research audit").click().run()
    assert len(fake.calls) == 6
    assert app.session_state["hf_session_budget"].remaining == 0
    app.run()  # next rerun after the cap was hit
    assert btn(app, "Run research audit").disabled
    assert any("Session calls left: 0 / 6" in c.value for c in app.sidebar.caption)
    assert not app.exception

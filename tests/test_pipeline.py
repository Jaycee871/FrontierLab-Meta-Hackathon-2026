from frontierlab.audit import enforce_citations, validate_claims
from frontierlab.demo_data import DEMO_CLAIMS, DEMO_PAPERS, QUESTION
from frontierlab.models import Paper
from frontierlab.pipeline import make_plan, run_research
from frontierlab.meta import parse_json_response
import pytest


def test_demo_conflict_is_detected_and_labeled():
    run = run_research(QUESTION, "not used", mode="demo")
    assert run.audit.conflicts
    assert run.skeptic["decision"] == "REVIEW_CONFLICT"
    assert all(x.synthetic for x in run.papers)
    assert not run.plan


def test_human_approval_is_required():
    run = run_research(QUESTION, "not used", mode="demo")
    with pytest.raises(PermissionError):
        make_plan(run)
    make_plan(run, approved=True)
    assert run.plan["status"] == "SYNTHETIC_TEST_ONLY"


def test_hallucinated_paper_ids_are_rejected():
    claims = [dict(DEMO_CLAIMS[0]), {**DEMO_CLAIMS[1], "paper_id": "DOI:FAKE"}]
    audit = validate_claims(DEMO_PAPERS, claims)
    assert len(audit.rejected_claims) == 1
    assert not audit.conflicts


def test_uncited_hypothesis_does_not_pass():
    okay, blocked = enforce_citations([{"text": "X", "evidence_ids": ["invented"]}], DEMO_PAPERS)
    assert not okay and len(blocked) == 1


def test_json_parser_handles_code_fence():
    fence = chr(96) * 3
    assert parse_json_response(fence + 'json\n{"claims": []}\n' + fence) == {"claims": []}


def test_no_meta_key_does_not_fake_agent_run():
    paper = Paper("PMCID:PMC0", "Demo real metadata placeholder", "2026", "A", "Test abstract", "https://example.org")
    def fake_retrieve(q, n):
        return [paper]
    run = run_research("A scientific question", "a query", mode="live", retrieve=fake_retrieve)
    assert run.skeptic["decision"] == "MODEL_NOT_CONNECTED"
    assert not run.hypotheses
    assert run.papers[0].synthetic is False


class StubMuse:
    model = "mock-muse"
    def json(self, role, task, payload):
        if role == "Evidence Extraction Agent":
            pid = payload["paper"]["paper_id"]
            stance = "supports" if pid == "PMID:1" else "contradicts"
            return {"claims": [{"paper_id": pid, "claim_key": "pH response", "stance": stance,
                      "statement": "Context-specific outcome", "limitation": "Abstract-only"}]}
        if role == "Adversarial Skeptic Agent":
            return {"explanation": "Results differ", "uncertainties": ["Confounding"]}
        if role == "Hypothesis Agent":
            return {"hypotheses": [{"text": "Control buffer variation", "evidence_ids": ["PMID:1", "PMID:2"], "rationale": "Tension"}]}
        if role == "Scientific Planning Agent":
            return {"objective": "Test replicability", "steps": ["Include controls"], "evidence_ids": ["PMID:1"], "limitations": "Pending human review"}
        raise ValueError(role)


def test_full_multiagent_pipeline_with_stub_not_live_api():
    ps = [Paper(f"PMID:{i}", f"Title{i}", "2026", "Authors", "Abstract", f"https://example.org/{i}") for i in [1, 2]]
    run = run_research("Test the role of buffer", "search", mode="live", model_client=StubMuse(),
                       retrieve=lambda q,n: ps)
    assert len(run.audit.conflicts) == 1
    assert run.hypotheses
    assert run.plan is None
    make_plan(run, model_client=StubMuse(), approved=True)
    assert run.plan["status"] == "DRAFT_FOR_RESEARCHER_REVIEW"


def test_single_sourced_abstract_blocks_hypotheses_even_with_meta_stub():
    paper = Paper("PMID:1", "Single abstract", "2026", "Author", "Abstract", "https://example.org/1")
    run = run_research("Question about pH", "query", mode="live", model_client=StubMuse(),
                       retrieve=lambda q, n: [paper])
    assert run.skeptic["decision"] == "INSUFFICIENT_EVIDENCE"
    assert run.hypotheses == []
    with pytest.raises(ValueError, match="supported hypothesis"):
        make_plan(run, model_client=StubMuse(), approved=True)

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
                      "statement": "Context-specific outcome", "limitation": "Abstract-only",
                      "evidence_quote": "The tested response depends on experimental buffer conditions."}]}
        if role == "Adversarial Skeptic Agent":
            return {"explanation": "Results differ", "uncertainties": ["Confounding"]}
        if role == "Hypothesis Agent":
            return {"hypotheses": [{"text": "Control buffer variation", "evidence_ids": ["PMID:1", "PMID:2"], "rationale": "Tension"}]}
        if role == "Scientific Planning Agent":
            return {"objective": "Test replicability", "steps": ["Include controls"], "evidence_ids": ["PMID:1"], "limitations": "Pending human review"}
        raise ValueError(role)


def test_full_multiagent_pipeline_with_stub_not_live_api():
    ps = [Paper(f"PMID:{i}", f"Title{i}", "2026", "Authors",
                "The tested response depends on experimental buffer conditions.",
                f"https://example.org/{i}") for i in [1, 2]]
    run = run_research("Test the role of buffer", "search", mode="live", model_client=StubMuse(),
                       retrieve=lambda q,n: ps)
    assert len(run.audit.conflicts) == 1
    assert run.hypotheses
    assert run.plan is None
    make_plan(run, model_client=StubMuse(), approved=True)
    assert run.plan["status"] == "DRAFT_FOR_RESEARCHER_REVIEW"


def test_single_sourced_abstract_blocks_hypotheses_even_with_meta_stub():
    paper = Paper("PMID:1", "Single abstract", "2026", "Author",
                  "The tested response depends on experimental buffer conditions.",
                  "https://example.org/1")
    run = run_research("Question about pH", "query", mode="live", model_client=StubMuse(),
                       retrieve=lambda q, n: [paper])
    assert run.skeptic["decision"] == "INSUFFICIENT_EVIDENCE"
    assert run.hypotheses == []
    with pytest.raises(ValueError, match="supported hypothesis"):
        make_plan(run, model_client=StubMuse(), approved=True)

def test_real_extraction_requires_quote_from_exact_cited_abstract():
    ps = [Paper("DOI:10.1234/one", "Paper A", "2026", "A",
                "Binding was measured in an acidic buffer under controlled conditions.",
                "https://doi.org/10.1234/one"),
          Paper("DOI:10.1234/two", "Paper B", "2026", "B",
                "Binding was measured at neutral pH with a separate protocol.",
                "https://doi.org/10.1234/two")]
    base = {"paper_id": ps[0].paper_id, "claim_key": "binding", "stance": "supports",
            "statement": "Binding increases", "limitation": "Abstract only"}
    valid = {**base, "evidence_quote": "Binding was measured in an acidic buffer under controlled conditions."}
    borrowed = {**base, "evidence_quote": ps[1].abstract}
    missing = dict(base)
    tiny = {**base, "evidence_quote": "Binding"}
    bad_type = {**base, "evidence_quote": ["Binding", "buffer"]}
    audited = validate_claims(ps, [valid, borrowed, missing, tiny, bad_type], require_quote=True)
    assert len(audited.verified_claims) == 1
    assert len(audited.rejected_claims) == 4
    assert audited.verified_claims[0].passage_matched is True
    assert "semantic entailment" in " ".join(audited.warnings)
    assert audited.verified_claims[0].evidence_quote == valid["evidence_quote"]

def test_real_mode_bad_quote_blocks_hypothesis_even_with_valid_doi():
    class Unfounded:
        model = "synthetic-model"
        def json(self, role, task, payload):
            return {"claims": [{"paper_id": payload["paper"]["paper_id"],
                   "claim_key": "binding", "stance": "supports",
                   "statement": "This abstract proves broad clinical utility",
                   "limitation": "None", "evidence_quote": "This quote is not in the abstract at all"}]}
    papers = [Paper(f"DOI:10.1234/{i}", "Study", "2026", "A",
                   "The binding assay was conducted under controlled conditions.",
                   f"https://doi.org/10.1234/{i}") for i in (1, 2)]
    run = run_research("Test reliability", "binding", mode="live",
                       retrieve=lambda q,n:papers, model_client=Unfounded())
    assert len(run.audit.rejected_claims) == 2
    assert run.audit.verified_claims == []
    assert run.hypotheses == []
    assert run.skeptic["decision"] == "INSUFFICIENT_EVIDENCE"

def test_quote_match_is_not_entailment_and_rejection_is_explicit():
    paper = Paper("DOI:10.1/x", "Paper", "2026", "A",
                  "No benefit was demonstrated in the tested cohort.",
                  "https://doi.org/10.1/x")
    candidate = {"paper_id": paper.paper_id, "stance": "supports", "claim_key": "benefit",
                 "statement": "The treatment is effective", "limitation": "None",
                 "evidence_quote": "No benefit was demonstrated in the tested cohort."}
    outcome = validate_claims([paper], [candidate], require_quote=True)
    assert len(outcome.verified_claims) == 1
    assert outcome.verified_claims[0].passage_matched
    assert not any("semantic entailment is verified" in s.lower() for s in outcome.warnings)
    # A textual citation exists, but the human reviewer must reject its semantics.

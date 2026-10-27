import pytest
from frontierlab.models import Paper
from frontierlab.pipeline import run_research
from frontierlab.review import review_packet, save_review, approved_claims

class TwoPaperModel:
    model="offline-mock-not-real-inference"
    def json(self,role,task,payload):
        if role=="Evidence Extraction Agent":
            return {"claims":[{
                "paper_id":payload["paper"]["paper_id"],
                "claim_key":"assay-response","stance":"supports",
                "statement":"Binding depends on test conditions.",
                "limitation":"Abstract evidence only",
                "evidence_quote":"The experimental assay showed a dependence on buffer conditions."
            }]}
        if role=="Adversarial Skeptic Agent":
            return {"explanation":"Review pending", "uncertainties":["Generalization"]}
        if role=="Hypothesis Agent":
            return {"hypotheses":[{"text":"Test assay controls",
                    "evidence_ids":["PMID:1","PMID:2"],
                    "rationale":"Experiment"}]}
        if role=="Scientific Planning Agent":
            return {"objective":"Design controls","steps":["Replicate"],
                    "evidence_ids":["PMID:1"],"limitations":"Human review"}
        raise AssertionError(role)

def run_two():
    ps=[Paper(f"PMID:{i}",f"Test article {i}","2026","A",
              "The experimental assay showed a dependence on buffer conditions.",
              f"https://example.org/{i}") for i in [1,2]]
    return run_research("Study assay conditions","assay",mode="live",
                        model_client=TwoPaperModel(),retrieve=lambda q,n:ps)

def test_packet_has_deterministic_source_bound_claim_ids_and_initial_status():
    run=run_two()
    first=review_packet(run)
    second=review_packet(run)
    assert first["dataset_id"]==second["dataset_id"]
    assert len(first["cases"])==2
    assert all(c["review_label"]=="PENDING" and c["verbatim_quote_matched"]
               for c in first["cases"])
    assert first["cases"][0]["case_id"]!=first["cases"][1]["case_id"]
    assert run.hypotheses==[]
    assert run.skeptic["decision"]=="HUMAN_CLAIM_REVIEW_REQUIRED"

def test_annotations_remain_explicit_and_gated_by_two_distinct_sources():
    run=run_two()
    cs=review_packet(run)["cases"]
    partial=save_review(run,[{"case_id":cs[0]["case_id"],"review_label":"SUPPORTED"}])
    assert partial["review_stats"]["pending"]==1
    assert partial["status"]=="REVIEW_INCOMPLETE_OR_INSUFFICIENT"
    assert len(approved_claims(run))==1
    full=save_review(run,[{"case_id":c["case_id"],"review_label":"SUPPORTED"} for c in cs])
    assert full["review_stats"]["human_label_coverage"]==1
    assert full["review_stats"]["supported_distinct_sources"]==2
    assert full["status"]=="READY_FOR_HUMAN_GATED_SYNTHESIS"
    assert full["independent_expert_adjudication_verified"] is False
    assert len(approved_claims(run))==2

def test_invalid_and_duplicate_annotations_cannot_pass():
    run=run_two()
    cid=review_packet(run)["cases"][0]["case_id"]
    with pytest.raises(ValueError,match="Duplicate"):
        save_review(run,[{"case_id":cid,"review_label":"SUPPORTED"},
                         {"case_id":cid,"review_label":"SUPPORTED"}])
    with pytest.raises(ValueError,match="unrecognized"):
        save_review(run,[{"case_id":"C00-FAKE","review_label":"SUPPORTED"}])
    with pytest.raises(ValueError,match="rationale"):
        save_review(run,[{"case_id":cid,"review_label":"INSUFFICIENT","review_note":"bad"}])
    with pytest.raises(ValueError):
        save_review(run,[{"case_id":cid,"review_label":"ACCEPT"}])

def test_review_not_available_for_synthetic_demo():
    from frontierlab.demo_data import QUESTION
    with pytest.raises(ValueError):
        review_packet(run_research(QUESTION,"x",mode="demo"))

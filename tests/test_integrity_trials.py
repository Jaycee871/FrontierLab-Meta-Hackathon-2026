import dataclasses
import pytest
from frontierlab.models import Paper, Claim
from frontierlab.review import review_packet, save_review, approved_claims, source_fingerprint
from frontierlab.pipeline import run_research, continue_after_review
from frontierlab.integrity_trials import (
    check_evidence, check_peptide_split, check_tool_handoff,
    check_transfer, failure_cases, suite_report
)

class Fake:
    model="FAKE-MODEL"
    def json(self,role,task,payload):
        if role=="Evidence Extraction Agent":
            return {"claims":[{
                "paper_id":payload["paper"]["paper_id"],
                "claim_key":"binding", "stance":"supports",
                "statement":"Experimental binding is condition dependent.",
                "limitation":"Abstract only",
                "evidence_quote":"Binding varied across experimental conditions."
            }]}
        raise AssertionError("No model continuation is expected in this test")

def make_run():
    papers=[Paper(f"PMID:{i}", "Same paper title", "2026", "A",
                  "Binding varied across experimental conditions.",
                  f"https://example.org/{i}") for i in (1,2)]
    run=run_research("Does binding depend on conditions?", "binding",
                     mode="live", retrieve=lambda q,n:papers,model_client=Fake())
    assert len(run.audit.verified_claims)==2
    return run

def test_review_packet_rebinds_when_abstract_revision_changes():
    run=make_run()
    cases=review_packet(run)["cases"]
    old_dataset=review_packet(run)["dataset_id"]
    save_review(run,[{"case_id":c["case_id"],"review_label":"SUPPORTED"} for c in cases])
    assert len(approved_claims(run))==2
    run.papers[0] = dataclasses.replace(run.papers[0],
                      abstract=run.papers[0].abstract+" Corrected version.")
    assert review_packet(run)["dataset_id"]!=old_dataset
    assert approved_claims(run)==[]
    with pytest.raises(PermissionError, match="source-bound"):
        continue_after_review(run,model_client=Fake())

def test_review_packet_rebinds_even_if_same_quote_and_doi_but_new_year():
    run=make_run()
    prev=review_packet(run)["dataset_id"]
    run.papers[1]=dataclasses.replace(run.papers[1],year="2027")
    assert review_packet(run)["dataset_id"]!=prev

def test_review_packet_rebinds_to_question_and_paper_url():
    run=make_run()
    prior=review_packet(run)["dataset_id"]
    run.question="Different scope question"
    assert review_packet(run)["dataset_id"]!=prior
    run.question="Does binding depend on conditions?"
    run.papers[0]=dataclasses.replace(run.papers[0],url="https://example.org/revised")
    assert review_packet(run)["dataset_id"]!=prior

def test_full_suite_expected_checks_are_not_model_accuracy():
    r=suite_report()
    assert r["total"]==12 and r["matched_expectations"]==12
    assert r["model_calls"]==0 and r["actual_scientific_experiments"]==0
    assert r["is_model_accuracy_benchmark"] is False
    assert all(x["data_origin"]=="FICTIONAL_HAND_AUTHORED" for x in r["cases"])

def test_human_supported_quote_is_not_semantic_truth():
    p=Paper("PMID:9","Toy","2026","Researcher",
            "No improvement was observed for this toy intervention.",
            "https://example.org")
    c=Claim(p.paper_id,"outcome","supports","Treatment works",
            "synthetic only",p.abstract,True)
    decision=check_evidence(p,c,source_snapshot_sha256=source_fingerprint(p),
                            reviewer_label="SUPPORTED")
    assert decision["status"]=="PASS_HUMAN_REVIEWED_ONLY"
    assert decision["meaning_verified_by_independent_experts"] is False

def test_tool_origin_cannot_be_self_certified():
    p={"status":"PREPARED_NOT_EXECUTED","request_sha256":"abc"}
    result={"status":"LIVE_EXECUTED","request_sha256":"abc","authenticated":True}
    record=check_tool_handoff(tool_manifest=p,result_manifest=result)
    assert record["status"]=="BLOCK_UNVERIFIED_ORIGIN"
    assert not record["origin_authentication_implemented"]

def test_tool_failure_is_not_silently_accepted():
    p={"status":"PREPARED_NOT_EXECUTED","request_sha256":"abc"}
    result={"status":"FAILED","request_sha256":"abc"}
    assert check_tool_handoff(tool_manifest=p,result_manifest=result)["status"]=="BLOCK_TOOL_FAILURE"

def test_group_holdout_and_nonidentical_normalization():
    bad=check_peptide_split(train_peptides=["pep1"],test_peptides=["PEP1"],
                            unseen_peptides=["pep2"])
    assert bad["status"]=="BLOCK_PEPTIDE_LEAKAGE"
    good=check_peptide_split(train_peptides=["PEP1"],test_peptides=["PEP2"],
                             unseen_peptides=["PEP3"])
    assert good["status"]=="PASS_DISJOINT_IDS_ONLY"
    assert not good["ood_generalization_established"]

def test_causal_transfer_never_claimed_from_prepost():
    d=check_transfer(pre_scores={"a":25.0,"b":40.0},
                     post_scores={"a":50.0,"b":75.0},
                     heldout_problems=True,intervention_documented=True)
    assert d["changes_in_percentage_points"]=={"a":25.0,"b":35.0}
    assert d["status"]=="DESCRIPTIVE_ONLY_NO_CAUSAL_CLAIM"
    assert d["knowledge_transfer_proven"] is False

@pytest.mark.parametrize("before,after",[
    ({"p":float("nan")},{"p":50}),
    ({"p":-1},{"p":50}),
    ({"p":50},{"different":70}),
    ({},{}),
])
def test_bad_transfer_inputs_stop(before,after):
    assert check_transfer(pre_scores=before,post_scores=after,
                          heldout_problems=True,intervention_documented=True
                         )["status"]=="BLOCK_NO_TRANSFER_EVIDENCE"

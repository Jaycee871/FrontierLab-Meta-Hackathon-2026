import pytest
from frontierlab.claim_verification import audit_predictions, conflict_transparency
from frontierlab.claim_benchmark import benchmark, annotated_conflicts
from frontierlab.models import Paper

def test_source_and_quote_gates_with_synthetic_gold_labels():
    papers, rows = benchmark()
    result = audit_predictions(papers, rows)
    assert result["total"] == 10
    assert result["mode"] == "ANNOTATED_BENCHMARK_ONLY"
    assert result["semantic_entailment_automatically_verified"] is False
    assert result["source_id_coverage"] == .9
    assert result["verbatim_passage_coverage"] == .7
    assert result["label_accuracy_vs_independent_gold"] == .8
    by_id = {r["id"]:r for r in result["cases"]}
    assert by_id["C03"]["gate_output"] == "SUPPORTED"  # anchored, but semantically wrong!
    assert not by_id["C03"]["gold_agrees_with_gate"]
    assert by_id["C08"]["gate_output"] == "INSUFFICIENT"
    assert by_id["C10"]["reason"] == "NO_MATCHING_SOURCE_PASSAGE"
    assert result["by_label"]["SUPPORTED"]["precision"] < 1

def test_quote_may_exist_without_entailing_claim():
    papers, rows = benchmark()
    r = audit_predictions(papers, rows)
    case = next(c for c in r["cases"] if c["id"]=="C03")
    assert case["quote_in_abstract"] and not case["scientific_entailment_verified"]
    assert case["gold"]=="CONTRADICTED"

def test_gold_cannot_be_missing_or_claim_id_duplicated():
    papers, rows=benchmark()
    with pytest.raises(ValueError):
        audit_predictions(papers,[{**rows[0],"gold":"UNKNOWN"}])
    with pytest.raises(ValueError):
        audit_predictions(papers,[rows[0],rows[0]])

def test_conflict_recall_not_implicitly_100_percent():
    gold=annotated_conflicts()
    result=conflict_transparency([],gold)
    assert result["recall"]==0
    assert conflict_transparency(gold,gold)["recall"]==1
    assert conflict_transparency([],[])["recall"] is None

def test_empty_cases_no_inflated_accuracy():
    assert audit_predictions([],[])["label_accuracy_vs_independent_gold"] is None

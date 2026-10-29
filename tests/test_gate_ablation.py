import pytest

from frontierlab.gate_ablation import PENDING, compare_gates

CASES = [
    {"case_id": "A", "source_id": "S1"},
    {"case_id": "B", "source_id": "S2"},
    {"case_id": "C", "source_id": "S3"},
]
SOURCES = {
    "S1": "alpha evidence phrase",
    "S2": "beta evidence phrase",
    "S3": "gamma evidence phrase",
}


def predictions():
    return [
        {"case_id": "A", "source_id": "S1", "label": "SUPPORTED",
         "evidence_quote": "alpha evidence phrase"},
        {"case_id": "B", "source_id": "S2", "label": "CONTRADICTED",
         "evidence_quote": "wrong quote"},
        {"case_id": "C", "source_id": "S3", "label": "INSUFFICIENT",
         "evidence_quote": ""},
    ]


def test_source_quote_gate_fails_closed_on_unanchored_affirmative_output():
    result = compare_gates(CASES, predictions(), SOURCES)
    assert result["arm_a_raw_model"]["affirmative"] == 2
    assert result["arm_b_source_quote_gate"]["outputs"] == {
        "A": "SUPPORTED", "B": "INSUFFICIENT", "C": "INSUFFICIENT"
    }
    assert result["arm_b_source_quote_gate"]["affirmative"] == 1
    assert result["arm_b_source_quote_gate"]["abstained"] == 2


def test_reviewer_gate_leaves_surviving_affirmative_output_pending():
    result = compare_gates(CASES, predictions(), SOURCES)
    arm = result["arm_c_reviewer_gate"]
    assert arm["outputs"]["A"] == PENDING
    assert arm["reviews_required"] == 1
    assert arm["reviews_completed"] == 0
    assert arm["pending_review"] == 1
    assert arm["gold_metrics"]["accuracy"] is None


def test_wrong_source_id_downgrades_to_insufficient():
    rows = predictions()
    rows[0]["source_id"] = "S2"
    result = compare_gates(CASES, rows, SOURCES)
    assert result["arm_b_source_quote_gate"]["outputs"]["A"] == "INSUFFICIENT"
    assert result["anchor_checks"]["A"]["source_matches_case"] is False


def test_complete_gold_unlocks_accuracy_only_after_outputs_are_final():
    gold = {"A": "SUPPORTED", "B": "INSUFFICIENT", "C": "INSUFFICIENT"}
    result = compare_gates(
        CASES, predictions(), SOURCES,
        reviews={"A": "SUPPORTED"},
        independent_gold=gold,
    )
    assert result["accuracy_reportable"] is True
    assert result["arm_a_raw_model"]["gold_metrics"]["accuracy"] == pytest.approx(2 / 3, abs=1e-4)
    assert result["arm_b_source_quote_gate"]["gold_metrics"]["accuracy"] == 1.0
    assert result["arm_c_reviewer_gate"]["gold_metrics"]["accuracy"] == 1.0


def test_partial_gold_never_reports_accuracy():
    result = compare_gates(
        CASES, predictions(), SOURCES,
        reviews={"A": "SUPPORTED"},
        independent_gold={"A": "SUPPORTED"},
    )
    assert result["independent_gold_complete"] is False
    assert result["accuracy_reportable"] is False
    assert result["arm_b_source_quote_gate"]["gold_metrics"]["accuracy"] is None

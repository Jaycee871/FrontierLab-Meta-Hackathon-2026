import copy
import pytest

from frontierlab.gate_ablation import (
    PENDING,
    compare_post_generation_gates,
    compare_prompt_arms,
)
from frontierlab.literature_pilot import load_dataset, public_cases
from frontierlab.recorded_gate_ablation import run_recorded_pilot
from scripts.nim_gate_ablation_trial import run_with_client


CASES = [
    {"case_id": "A", "source_id": "S1"},
    {"case_id": "B", "source_id": "S2"},
    {"case_id": "C", "source_id": "S3"},
]
SOURCES = {
    "S1": "alpha evidence phrase with enough characters to satisfy the source gate",
    "S2": "beta evidence phrase with enough characters to satisfy the source gate",
    "S3": "gamma evidence phrase with enough characters to satisfy the source gate",
}


def predictions():
    return [
        {
            "case_id": "A",
            "source_id": "S1",
            "label": "SUPPORTED",
            "evidence_quote": SOURCES["S1"],
        },
        {
            "case_id": "B",
            "source_id": "S2",
            "label": "CONTRADICTED",
            "evidence_quote": "wrong quote that is long enough but is not in the source text",
        },
        {
            "case_id": "C",
            "source_id": "S3",
            "label": "INSUFFICIENT",
            "evidence_quote": "",
        },
    ]


def test_post_generation_gate_fails_closed_on_unanchored_decisive_output():
    result = compare_post_generation_gates(CASES, predictions(), SOURCES)
    assert result["comparison_type"] == "POST_GENERATION_GATE_ABLATION"
    assert result["prompt_effect_isolated"] is False
    assert result["arm_a_fixed_model_outputs"]["decisive"] == 2
    assert result["arm_b_source_quote_post_gate"]["outputs"] == {
        "A": "SUPPORTED",
        "B": "INSUFFICIENT",
        "C": "INSUFFICIENT",
    }
    assert result["effects"]["quote_gate_new_abstentions"] == 1
    assert result["effects"]["quote_gate_decisive_retention_rate"] == 0.5


def test_reviewer_gate_only_reviews_decisions_that_survived_quote_gate():
    result = compare_post_generation_gates(
        CASES,
        predictions(),
        SOURCES,
        reviews={"A": "INSUFFICIENT", "B": "CONTRADICTED", "C": "SUPPORTED"},
    )
    arm = result["arm_c_source_quote_plus_human_review"]
    assert arm["reviews_required"] == 1
    assert arm["reviews_completed"] == 1
    assert arm["outputs"]["A"] == "INSUFFICIENT"
    assert arm["outputs"]["B"] == "INSUFFICIENT"
    assert arm["outputs"]["C"] == "INSUFFICIENT"
    assert arm["review_corrections_to_surviving_decisions"] == 1
    assert arm["reviewer_abstentions_from_surviving_decisions"] == 1


def test_complete_reference_is_not_accuracy_without_independent_verification():
    gold = {"A": "SUPPORTED", "B": "INSUFFICIENT", "C": "INSUFFICIENT"}
    result = compare_post_generation_gates(
        CASES,
        predictions(),
        SOURCES,
        independent_gold=gold,
        independent_gold_verified=False,
    )
    assert result["independent_gold_complete"] is True
    assert result["independent_gold_verified"] is False
    assert result["accuracy_reportable"] is False
    assert result["arm_b_source_quote_post_gate"]["gold_metrics"]["accuracy"] is None


def test_verified_independent_gold_can_unlock_accuracy():
    gold = {"A": "SUPPORTED", "B": "INSUFFICIENT", "C": "INSUFFICIENT"}
    result = compare_post_generation_gates(
        CASES,
        predictions(),
        SOURCES,
        independent_gold=gold,
        independent_gold_verified=True,
    )
    assert result["accuracy_reportable"] is True
    assert result["arm_b_source_quote_post_gate"]["gold_metrics"]["accuracy"] == 1.0


def test_prompt_level_ablation_separates_prompt_shift_from_post_gate_shift():
    raw = [
        {"case_id": "A", "source_id": "S1", "label": "SUPPORTED"},
        {"case_id": "B", "source_id": "S2", "label": "SUPPORTED"},
        {"case_id": "C", "source_id": "S3", "label": "INSUFFICIENT"},
    ]
    grounded = predictions()
    result = compare_prompt_arms(CASES, raw, grounded, SOURCES)
    assert result["comparison_type"] == "PROMPT_AND_POSTPROCESS_ABLATION"
    assert result["prompt_effect_isolated"] is True
    assert result["effects"]["prompt_label_changes"] == 1
    assert result["effects"]["quote_gate_new_abstentions_after_grounded_prompt"] == 1
    assert result["effects"]["arm_a_to_arm_b_output_changes"] == 1


def test_recorded_glimmer_pilot_is_zero_call_post_generation_ablation():
    result = run_recorded_pilot()
    assert result["case_count"] == 12
    assert result["new_model_calls"] == 0
    assert result["model_id"] == "meta/muse-glimmer-30b"
    assert result["arm_a_fixed_model_outputs"]["decisive"] == 8
    assert result["arm_a_fixed_model_outputs"]["abstained"] == 4
    assert result["arm_b_source_quote_post_gate"]["decisive"] == 8
    assert result["arm_b_source_quote_post_gate"]["abstained"] == 4
    assert result["effects"]["quote_gate_new_abstentions"] == 0
    assert result["effects"]["quote_gate_decisive_retention_rate"] == 1.0
    arm_c = result["arm_c_source_quote_plus_human_review"]
    assert arm_c["reviews_required"] == 8
    assert arm_c["reviews_completed"] == 0
    assert arm_c["pending_review"] == 8
    assert result["accuracy_reportable"] is False
    assert result["recorded_model_call"]["usage"]["total_tokens"] == 1794
    assert result["recorded_model_call"]["elapsed_seconds"] == 11.168
    assert sum(v["source_matches_case"] for v in result["anchor_checks"].values()) == 12
    assert sum(v["quote_anchored"] for v in result["anchor_checks"].values()) == 8


class FakeClient:
    model = "meta/muse-glimmer-30b"
    backend = "nvidia-nim"

    def __init__(self):
        self.calls = []
        self.provenance = {"attempted_calls": 0, "receipts": []}

    def json(self, role, task, payload):
        self.calls.append({"role": role, "task": task, "payload": copy.deepcopy(payload)})
        self.provenance["attempted_calls"] += 1
        rows = []
        grounded = "evidence_quote" in task
        for index, case in enumerate(payload["cases"]):
            source = next(s for s in payload["sources"] if s["source_id"] == case["source_id"])
            label = "SUPPORTED" if index == 0 else "INSUFFICIENT"
            row = {
                "case_id": case["case_id"],
                "source_id": case["source_id"],
                "label": label,
            }
            if grounded:
                row["evidence_quote"] = source["source_text"] if label == "SUPPORTED" else ""
            rows.append(row)
        return {"cases": rows}


def test_live_trial_runner_uses_two_calls_and_identical_case_payload():
    data = load_dataset()
    client = FakeClient()
    result = run_with_client(client, data=data)
    assert len(client.calls) == 2
    assert client.provenance["attempted_calls"] == 2
    assert client.calls[0]["payload"] == client.calls[1]["payload"] == public_cases(data)
    assert client.calls[0]["role"] == client.calls[1]["role"] == "Evidence Extraction Agent"
    assert "evidence_quote" not in client.calls[0]["task"]
    assert "evidence_quote" in client.calls[1]["task"]
    assert result["same_model_required"] is True
    assert result["new_model_calls"] == 2
    assert result["accuracy_reportable"] is False
    assert result["arm_c_quote_gate_plus_human_review"]["pending_review"] == 1

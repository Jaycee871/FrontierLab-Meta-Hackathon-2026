import copy
import pytest

from scripts.validate_nim_continuation import validate_record


def good_record():
    sha = "a" * 64
    return {
        "record_type": "nim_research_human_reviewed_continuation",
        "status": "REAL_RESEARCH_SYNTHESIS_COMPLETED_METHOD_REVIEW_REQUIRED",
        "maximum_new_model_calls": 2,
        "automatic_method_selection": False,
        "automatic_planning": False,
        "continuation_inference": {
            "provider": "nvidia-nim",
            "model": "meta/muse-glimmer-30b",
            "attempted_calls": 2,
            "receipts": [
                {
                    "role": "Adversarial Skeptic Agent",
                    "reported_model": "meta/muse-glimmer-30b",
                    "finish_reason": "stop",
                    "status": "JSON_OBJECT_RETURNED",
                    "input_sha256": sha,
                    "output_sha256": sha,
                },
                {
                    "role": "Hypothesis Agent",
                    "reported_model": "meta/muse-glimmer-30b",
                    "finish_reason": "stop",
                    "status": "JSON_OBJECT_RETURNED",
                    "input_sha256": sha,
                    "output_sha256": sha,
                },
            ],
        },
        "run": {
            "backend": "nvidia-nim",
            "model": "meta/muse-glimmer-30b",
            "evaluation": None,
            "plan": None,
            "review": {
                "status": "READY_FOR_HUMAN_GATED_SYNTHESIS",
                "dataset_id": "dataset-1",
                "review_stats": {
                    "supported_distinct_sources": 2,
                    "pending": 0,
                },
                "cases": [
                    {"paper_id": "P1", "review_label": "SUPPORTED"},
                    {"paper_id": "P2", "review_label": "SUPPORTED"},
                ],
            },
            "hypotheses": [
                {
                    "text": "A falsifiable, source-bounded hypothesis.",
                    "evidence_ids": ["P1", "P2"],
                    "rationale": "Both reviewed sources motivate a direct comparison.",
                }
            ],
            "skeptic": {
                "decision": "HUMAN_REVIEWED_DRAFT",
                "uncertainties": ["Generalization is not established."],
            },
        },
    }


def test_valid_record_prepares_method_handoff():
    handoff = validate_record(good_record())
    assert handoff["status"] == "READY_FOR_RESEARCHER_METHOD_EVALUATION"
    assert handoff["verified_call_count"] == 2
    assert handoff["verified_role_order"] == [
        "Adversarial Skeptic Agent",
        "Hypothesis Agent",
    ]
    assert handoff["supported_source_ids"] == ["P1", "P2"]
    assert handoff["method_selection_automated"] is False
    assert handoff["planning_automated"] is False


def test_rejects_wrong_role_order():
    record = good_record()
    record["continuation_inference"]["receipts"].reverse()
    with pytest.raises(ValueError, match="role order"):
        validate_record(record)


def test_rejects_crossing_into_plan():
    record = good_record()
    record["run"]["plan"] = {"status": "DRAFT"}
    with pytest.raises(ValueError, match="method/planning"):
        validate_record(record)


def test_rejects_hypothesis_from_unreviewed_source():
    record = good_record()
    record["run"]["hypotheses"][0]["evidence_ids"] = ["P1", "P3"]
    with pytest.raises(ValueError, match="human-supported"):
        validate_record(record)


def test_accepts_completed_run_with_no_hypothesis_but_blocks_method_handoff():
    record = good_record()
    record["status"] = "REAL_RESEARCH_SYNTHESIS_COMPLETED_NO_HYPOTHESIS"
    record["run"]["hypotheses"] = []
    handoff = validate_record(record)
    assert handoff["status"] == "NO_HYPOTHESIS_TO_EVALUATE"

from frontierlab.models import Audit, Run
from frontierlab.process_metrics import (
    human_interventions,
    nim_efficiency,
    process_metrics,
    stage_completion,
)


def _run(**updates):
    base = dict(
        question="Does method M improve pH selectivity?",
        mode="live",
        model="meta/muse-glimmer-30b",
        papers=[],
        audit=Audit(),
        hypotheses=[],
        skeptic={},
        log=[
            {"role": "Retriever", "status": "COMPLETE", "note": "done"},
            {"role": "Human Claim Review", "status": "BLOCKED", "note": "review required"},
        ],
        backend="none",
    )
    base.update(updates)
    return Run(**base)


def test_scr_is_milestone_completion_not_accuracy():
    run = _run(hypotheses=[{"text": "h", "evidence_ids": []}])
    result = stage_completion(run)
    assert result["stages"] == {
        "research": True,
        "evidence": True,
        "hypothesis": True,
        "evaluation": False,
        "planning": False,
    }
    assert result["completed"] == 3
    assert result["scr"] == 0.6
    assert "not a quality" in result["definition"]


def test_hic_like_count_is_explicitly_derived():
    run = _run(
        review={"review_stats": {"reviewed": 2}},
        evaluation={"evaluation_id": "E1"},
        plan={"status": "DRAFT_FOR_RESEARCHER_REVIEW"},
        evidence_graph={
            "approvals": {
                "step:1": {"reviewer": "A"},
                "step:2": {"reviewer": "A"},
            }
        },
    )
    result = human_interventions(run)
    assert result["observed_total"] == 6
    assert result["observed"]["claim_review_decisions"] == 2
    assert result["observed"]["method_evaluation_saved"] == 1
    assert result["observed"]["plan_authorization_proxy"] == 1
    assert result["observed"]["plan_step_approvals"] == 2
    assert result["complete_event_log"] is False


def test_nim_aerr_is_na_when_no_runtime_errors():
    run = _run(
        backend="nvidia-nim",
        inference={
            "attempted_calls": 2,
            "receipts": [
                {
                    "status": "JSON_OBJECT_RETURNED",
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                    "elapsed_seconds": 1.25,
                },
                {
                    "status": "JSON_OBJECT_RETURNED",
                    "usage": {"prompt_tokens": 20, "completion_tokens": 7, "total_tokens": 27},
                    "elapsed_seconds": 2.5,
                },
            ],
        },
    )
    result = nim_efficiency(run)
    assert result["aerr"] is None
    assert result["aerr_status"] == "N_A_NO_RUNTIME_ERRORS"
    assert result["total_tokens"] == 42
    assert result["elapsed_seconds"] == 3.75


def test_nim_aerr_zero_when_errors_occur_and_no_retry_exists():
    run = _run(
        backend="nvidia-nim",
        inference={
            "attempted_calls": 2,
            "receipts": [
                {"status": "FAILED_NO_RETRY", "elapsed_seconds": 0.4},
                {"status": "JSON_OBJECT_RETURNED", "elapsed_seconds": 0.6},
            ],
        },
    )
    result = nim_efficiency(run)
    assert result["failed_calls"] == 1
    assert result["autonomous_recoveries"] == 0
    assert result["aerr"] == 0.0
    assert result["aerr_status"] == "ZERO_RECOVERY_NO_RETRY_POLICY"


def test_non_nim_backend_does_not_invent_aerr():
    result = nim_efficiency(_run(backend="none", inference=None))
    assert result["applicable"] is False
    assert result["aerr"] is None
    assert result["aerr_status"] == "NOT_APPLICABLE"


def test_process_metrics_never_claims_scientific_accuracy():
    result = process_metrics(_run())
    assert result["schema"] == "frontierlab.process-metrics.v1"
    assert result["scientific_accuracy_measured"] is False
    assert result["scientific_validity_verified"] is False

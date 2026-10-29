"""Deterministic process metrics derived from a FrontierLab Run.

These metrics describe workflow progress and recorded process evidence. They are
not model-accuracy metrics and do not establish scientific validity.
"""
from __future__ import annotations

from typing import Any

from .models import Run

SCHEMA = "frontierlab.process-metrics.v1"
STAGES = ("research", "evidence", "hypothesis", "evaluation", "planning")


def _terminal_evidence_event(log: list[dict]) -> bool:
    roles = {"Evidence Auditor", "Extraction Agent", "Audit Gate", "Human Claim Review"}
    states = {
        "COMPLETE", "SIMULATED", "PASS_WITH_WARNING", "BLOCKED",
    }
    return any(
        isinstance(item, dict)
        and item.get("role") in roles
        and item.get("status") in states
        for item in log
    )


def stage_completion(run: Run) -> dict:
    """Return milestone completion, not scientific success."""
    stages = {
        "research": bool(isinstance(run.question, str) and run.question.strip()),
        "evidence": _terminal_evidence_event(run.log),
        "hypothesis": bool(run.hypotheses),
        "evaluation": isinstance(run.evaluation, dict),
        "planning": isinstance(run.plan, dict),
    }
    completed = sum(stages.values())
    return {
        "stages": stages,
        "completed": completed,
        "total": len(STAGES),
        "scr": round(completed / len(STAGES), 4),
        "definition": "Completed workflow milestones / 5; not a quality or success score.",
    }


def human_interventions(run: Run) -> dict:
    """Conservative HIC-like count from artifacts already present in Run.

    This is derived from current artifacts, not an authoritative event stream.
    """
    review_stats = run.review.get("review_stats", {}) if isinstance(run.review, dict) else {}
    claim_reviews = review_stats.get("reviewed", 0)
    if not isinstance(claim_reviews, int) or claim_reviews < 0:
        claim_reviews = 0

    method_evaluation = int(isinstance(run.evaluation, dict))
    plan_authorization_proxy = int(isinstance(run.plan, dict))
    approvals = {}
    if isinstance(run.evidence_graph, dict):
        raw = run.evidence_graph.get("approvals", {})
        if isinstance(raw, dict):
            approvals = raw
    plan_step_approvals = len(approvals)

    observed = {
        "claim_review_decisions": claim_reviews,
        "method_evaluation_saved": method_evaluation,
        "plan_authorization_proxy": plan_authorization_proxy,
        "plan_step_approvals": plan_step_approvals,
    }
    return {
        "observed_total": sum(observed.values()),
        "observed": observed,
        "status": "DERIVED_FROM_CURRENT_ARTIFACTS",
        "complete_event_log": False,
        "note": (
            "This is a conservative HIC-like observable count, not a complete "
            "or identity-verified Human Intervention Count. Plan generation is "
            "used only as a proxy that explicit planning approval occurred."
        ),
    }


def nim_efficiency(run: Run) -> dict:
    """Summarize the verified NVIDIA-NIM provenance shape when present."""
    if run.backend != "nvidia-nim" or not isinstance(run.inference, dict):
        return {
            "applicable": False,
            "attempted_calls": None,
            "failed_calls": None,
            "autonomous_recoveries": None,
            "aerr": None,
            "aerr_status": "NOT_APPLICABLE",
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "elapsed_seconds": None,
        }

    receipts = run.inference.get("receipts", [])
    if not isinstance(receipts, list):
        receipts = []

    attempted = run.inference.get("attempted_calls", len(receipts))
    if not isinstance(attempted, int) or attempted < 0:
        attempted = len(receipts)

    failed = sum(
        1 for receipt in receipts
        if isinstance(receipt, dict) and receipt.get("status") == "FAILED_NO_RETRY"
    )

    prompt_tokens = completion_tokens = total_tokens = 0
    elapsed = 0.0
    for receipt in receipts:
        if not isinstance(receipt, dict):
            continue
        usage = receipt.get("usage", {})
        if isinstance(usage, dict):
            for key, target in (
                ("prompt_tokens", "prompt"),
                ("completion_tokens", "completion"),
                ("total_tokens", "total"),
            ):
                value = usage.get(key)
                if isinstance(value, int) and value >= 0:
                    if target == "prompt":
                        prompt_tokens += value
                    elif target == "completion":
                        completion_tokens += value
                    else:
                        total_tokens += value
        seconds = receipt.get("elapsed_seconds")
        if isinstance(seconds, (int, float)) and not isinstance(seconds, bool) and seconds >= 0:
            elapsed += float(seconds)

    if failed == 0:
        aerr = None
        aerr_status = "N_A_NO_RUNTIME_ERRORS"
    else:
        # The verified NIM backend deliberately has no automatic retry/recovery.
        aerr = 0.0
        aerr_status = "ZERO_RECOVERY_NO_RETRY_POLICY"

    return {
        "applicable": True,
        "attempted_calls": attempted,
        "failed_calls": failed,
        "autonomous_recoveries": 0,
        "aerr": aerr,
        "aerr_status": aerr_status,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "elapsed_seconds": round(elapsed, 3),
    }


def process_metrics(run: Run) -> dict:
    stages = stage_completion(run)
    interventions = human_interventions(run)
    nim = nim_efficiency(run)
    return {
        "schema": SCHEMA,
        "scr": stages["scr"],
        "stage_completion": stages,
        "human_interventions": interventions,
        "nim": nim,
        "scientific_accuracy_measured": False,
        "scientific_validity_verified": False,
    }

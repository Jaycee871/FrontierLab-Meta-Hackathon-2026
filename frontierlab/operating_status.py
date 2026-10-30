"""Research Operating Interface status derived from current Run state."""
from __future__ import annotations

from .evidence_graph import build_evidence_graph
from .process_metrics import process_metrics, stage_completion
from .traceability import source_audit_summary, trace_coverage
from .version import __version__


def research_operating_status(run) -> dict:
    graph = build_evidence_graph(run, previous=getattr(run, "evidence_graph", None))
    stages = stage_completion(run)
    metrics = process_metrics(run)
    trace = trace_coverage(graph)
    audit = source_audit_summary(graph)

    next_stage = next(
        (stage for stage, completed in stages["stages"].items() if not completed),
        "complete",
    )

    human_events = getattr(run, "human_events", []) or []
    planning_authorized = any(
        isinstance(event, dict) and event.get("kind") == "PLANNING_APPROVED"
        for event in human_events
    )

    return {
        "schema": "frontierlab.research-operating-status.v1",
        "frontierlab_version": __version__,
        "current_activity": {
            "next_required_stage": next_stage,
            "stage_completion": stages["stages"],
            "scr": stages["scr"],
        },
        "active_sources": [
            {
                "paper_id": paper.paper_id,
                "title": paper.title,
                "url": paper.url,
            }
            for paper in run.papers
        ],
        "source_audit": audit,
        "traceability": trace,
        "governance": {
            "human_events_recorded": metrics["human_interventions"]["observed_total"],
            "claim_review_status": (
                run.review.get("status")
                if isinstance(run.review, dict)
                else "NOT_RECORDED"
            ),
            "method_evaluation_saved": isinstance(run.evaluation, dict),
            "planning_authorized_recorded": planning_authorized,
            "plan_generated": isinstance(run.plan, dict),
        },
        "maintainability": {
            "central_version_metadata": True,
            "process_error_taxonomy": True,
            "maintenance_canary_configured": True,
            "scheduled_dependency_canary": True,
            "last_canary_status_embedded_in_runtime": False,
            "automatic_repair_enabled": False,
            "automatic_environment_rebuild_enabled": False,
            "verified_nim_automatic_retry": False if run.backend == "nvidia-nim" else None,
            "status": "CANARY_MONITORED_MANUAL_REPAIR",
        },
        "scientific_accuracy_measured": False,
        "note": (
            "Operational status exposes process/provenance/governance state, not private "
            "chain-of-thought and not scientific truth."
        ),
    }

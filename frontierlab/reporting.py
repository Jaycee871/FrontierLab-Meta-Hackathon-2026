"""Portable audit export: preserve warnings, source provenance and process metrics."""
import json

from .models import Run
from .process_metrics import process_metrics
from .trajectory_graph import build_trajectory_graph


def export_json(run: Run) -> str:
    payload = run.as_dict()
    payload["process_metrics"] = process_metrics(run)
    payload["trajectory_graph"] = build_trajectory_graph(run)
    return json.dumps(payload, indent=2, ensure_ascii=False)


def summary(run: Run) -> dict:
    metrics = process_metrics(run)
    return {
        "sources": len(run.papers),
        "claims": len(run.audit.verified_claims),
        "rejected": len(run.audit.rejected_claims),
        "conflicts": len(run.audit.conflicts),
        "hypotheses": len(run.hypotheses),
        "decision": run.skeptic.get("decision", "UNKNOWN"),
        "plan_status": (run.plan or {}).get("status", "NOT_GENERATED"),
        "scr": metrics["scr"],
        "observed_human_interventions": metrics["human_interventions"]["observed_total"],
    }

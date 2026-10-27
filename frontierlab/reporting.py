"""Portable audit export: preserve all warnings and source provenance."""
import json
from .models import Run


def export_json(run: Run) -> str:
    return json.dumps(run.as_dict(), indent=2, ensure_ascii=False)


def summary(run: Run) -> dict:
    return {
        "sources": len(run.papers),
        "claims": len(run.audit.verified_claims),
        "rejected": len(run.audit.rejected_claims),
        "conflicts": len(run.audit.conflicts),
        "hypotheses": len(run.hypotheses),
        "decision": run.skeptic.get("decision", "UNKNOWN"),
        "plan_status": (run.plan or {}).get("status", "NOT_GENERATED"),
    }

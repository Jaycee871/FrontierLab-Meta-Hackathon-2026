"""Deterministic taxonomy for FrontierLab blocking and failure signals.

The taxonomy separates expected governance gates from runtime failures so that a
human review requirement is never counted as a software/model error.
"""
from __future__ import annotations

from collections import Counter

from .models import Run

SCHEMA = "frontierlab.error-taxonomy.v1"

GOVERNANCE = "GOVERNANCE_GATE"
EVIDENCE = "EVIDENCE_INSUFFICIENT"
CITATION = "CITATION_OR_SOURCE_FAILURE"
RESOURCE = "RESOURCE_NOT_CONNECTED"
MODEL_RUNTIME = "MODEL_RUNTIME_FAILURE"
MODEL_OUTPUT = "MODEL_OUTPUT_FAILURE"
CLAIM_REJECTED = "CLAIM_REJECTED"
SCIENTIFIC_TENSION = "SCIENTIFIC_TENSION"


def _classify_log(item: dict) -> str | None:
    if not isinstance(item, dict):
        return None
    role = str(item.get("role", ""))
    status = str(item.get("status", ""))
    note = str(item.get("note", "")).lower()

    if role == "Human Claim Review" and status == "BLOCKED":
        return GOVERNANCE
    if role == "Audit Gate" and status == "BLOCKED":
        return EVIDENCE
    if role == "Citation Gate" and status == "BLOCKED":
        return CITATION
    if role == "Meta AI" and status == "BLOCKED":
        return RESOURCE
    if status == "FAILED_NO_RETRY":
        return MODEL_RUNTIME
    if status == "BLOCKED" and ("model" in note or "backend" in note):
        return RESOURCE
    return None


def classify_run(run: Run) -> dict:
    events: list[dict] = []

    for index, item in enumerate(run.log):
        category = _classify_log(item)
        if category:
            events.append({
                "source": "run.log",
                "index": index,
                "category": category,
                "role": item.get("role"),
                "status": item.get("status"),
                "note": item.get("note", ""),
            })

    for index, rejected in enumerate(run.audit.rejected_claims):
        if not isinstance(rejected, dict):
            continue
        reason = str(rejected.get("reason", "")).lower()
        category = CITATION if ("citation" in reason or "source" in reason or "passage" in reason) else CLAIM_REJECTED
        events.append({
            "source": "audit.rejected_claims",
            "index": index,
            "category": category,
            "reason": rejected.get("reason", ""),
        })

    for index, conflict in enumerate(run.audit.conflicts):
        events.append({
            "source": "audit.conflicts",
            "index": index,
            "category": SCIENTIFIC_TENSION,
            "claim_key": conflict.get("claim_key") if isinstance(conflict, dict) else None,
        })

    if run.backend == "nvidia-nim" and isinstance(run.inference, dict):
        receipts = run.inference.get("receipts", [])
        if isinstance(receipts, list):
            for index, receipt in enumerate(receipts):
                if not isinstance(receipt, dict):
                    continue
                if receipt.get("status") == "FAILED_NO_RETRY":
                    # Avoid double counting only if the same failure was already explicitly
                    # represented in run.log; current pipeline usually does not log it.
                    events.append({
                        "source": "inference.receipts",
                        "index": index,
                        "category": MODEL_RUNTIME,
                        "role": receipt.get("role"),
                        "status": "FAILED_NO_RETRY",
                    })

    counts = Counter(event["category"] for event in events)
    runtime_failures = counts[MODEL_RUNTIME] + counts[MODEL_OUTPUT]
    governance_blocks = counts[GOVERNANCE] + counts[EVIDENCE] + counts[CITATION] + counts[RESOURCE]

    return {
        "schema": SCHEMA,
        "events": events,
        "counts": dict(sorted(counts.items())),
        "runtime_failures": runtime_failures,
        "governance_or_evidence_blocks": governance_blocks,
        "scientific_tensions": counts[SCIENTIFIC_TENSION],
        "note": (
            "Governance/evidence blocks are expected safety workflow outcomes and are "
            "reported separately from runtime/model-output failures."
        ),
    }

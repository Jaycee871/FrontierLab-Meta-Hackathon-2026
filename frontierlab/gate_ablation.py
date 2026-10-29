"""Controlled comparison helpers for FrontierLab gates."""
from __future__ import annotations

SCHEMA = "frontierlab.gate-ablation.v1"
PENDING = "PENDING_REVIEW"

from .claim_verification import LABELS, quote_anchored


def _prediction_map(rows: list[dict]) -> dict[str, dict]:
    out = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Prediction rows must be objects")
        cid = str(row.get("case_id", "")).strip()
        label = str(row.get("label", "")).upper()
        if not cid or cid in out:
            raise ValueError("Predictions require distinct case IDs")
        if label not in LABELS:
            raise ValueError("Unrecognized prediction label")
        out[cid] = row
    return out


def _label_map(values: dict | None, known: set[str]) -> dict[str, str]:
    if values is None:
        return {}
    if not isinstance(values, dict):
        raise ValueError("Labels must be a mapping")
    out = {}
    for cid, value in values.items():
        if cid not in known:
            raise ValueError("Label supplied for an unknown case")
        label = str(value).upper()
        if label not in LABELS:
            raise ValueError("Unrecognized label")
        out[cid] = label
    return out


def _summary(outputs: dict[str, str]) -> dict:
    values = list(outputs.values())
    return {
        "outputs": outputs,
        "affirmative": sum(x in {"SUPPORTED", "CONTRADICTED"} for x in values),
        "abstained": values.count("INSUFFICIENT"),
        "pending_review": values.count(PENDING),
    }

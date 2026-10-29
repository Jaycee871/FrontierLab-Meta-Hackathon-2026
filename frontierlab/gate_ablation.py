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


def source_quote_arm(cases: list[dict], predictions: list[dict], source_texts: dict[str, str]) -> dict:
    pred = _prediction_map(predictions)
    case_sources = {}
    for case in cases:
        cid = str(case.get("case_id", "")).strip()
        sid = str(case.get("source_id", "")).strip()
        if not cid or not sid or cid in case_sources:
            raise ValueError("Invalid fixed case set")
        case_sources[cid] = sid
    if set(pred) != set(case_sources):
        raise ValueError("Predictions must cover the exact fixed case set")

    raw, gated, checks = {}, {}, {}
    for cid, expected_sid in case_sources.items():
        row = pred[cid]
        label = str(row["label"]).upper()
        raw[cid] = label
        sid = str(row.get("source_id", "")).strip()
        source_matches = sid == expected_sid and sid in source_texts
        quote = str(row.get("evidence_quote", ""))
        anchored = bool(source_matches and quote and quote_anchored(source_texts[sid], quote))
        checks[cid] = {"source_matches_case": source_matches, "quote_anchored": anchored}
        gated[cid] = label if label == "INSUFFICIENT" or anchored else "INSUFFICIENT"

    return {"raw": raw, "gated": gated, "anchor_checks": checks}

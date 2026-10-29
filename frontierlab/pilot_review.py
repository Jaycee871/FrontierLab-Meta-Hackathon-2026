"""Source-bound researcher review packets for the 12-case literature pilot.

These helpers canonicalize a reviewer-edited packet without treating the
reviewer labels as independent scientific gold.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from .literature_pilot import LABELS, dataset_id, public_cases

SCHEMA = "frontierlab.real-excerpt-review.v1"
PENDING = "PENDING"


def canonicalize_review_upload(
    data: dict,
    upload: dict,
    *,
    reviewer: str,
    recorded_at_utc: str | None = None,
) -> dict:
    if not isinstance(upload, dict) or upload.get("schema") != SCHEMA:
        raise ValueError("Unexpected reviewer packet schema")
    did = dataset_id(data)
    if upload.get("dataset_id") != did:
        raise ValueError("Reviewer packet is not bound to the fixed dataset")

    public = public_cases(data)
    if upload.get("sources") != public["sources"]:
        raise ValueError("Reviewer packet source snapshot changed")
    rows = upload.get("cases")
    if not isinstance(rows, list):
        raise ValueError("Reviewer packet cases required")

    expected = {row["case_id"]: row for row in public["cases"]}
    if len(rows) != len(expected):
        raise ValueError("Reviewer packet must contain every case exactly once")

    seen = set()
    clean_cases = []
    reviewed = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Reviewer case must be an object")
        cid = row.get("case_id")
        if cid not in expected or cid in seen:
            raise ValueError("Reviewer packet has an unknown or duplicate case")
        seen.add(cid)
        reference = expected[cid]
        if row.get("source_id") != reference["source_id"] or row.get("claim") != reference["claim"]:
            raise ValueError("Reviewer packet case/source binding changed")

        label = str(row.get("label", PENDING)).upper()
        if label not in LABELS | {PENDING}:
            raise ValueError("Reviewer label must be SUPPORTED, CONTRADICTED, INSUFFICIENT or PENDING")
        rationale = row.get("rationale", "")
        if not isinstance(rationale, str):
            raise ValueError("Reviewer rationale must be text")
        rationale = rationale.strip()
        if label != PENDING:
            if len(rationale) < 8:
                raise ValueError("Reviewed cases require a rationale of at least eight characters")
            reviewed += 1
        clean_cases.append({
            **deepcopy(reference),
            "label": label,
            "rationale": rationale,
        })

    if set(seen) != set(expected):
        raise ValueError("Reviewer packet case set is incomplete")

    reviewer = reviewer.strip() if isinstance(reviewer, str) else ""
    if reviewed and not reviewer:
        raise ValueError("Reviewer name required when judgments are supplied")

    if recorded_at_utc is None:
        recorded_at_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
    if not isinstance(recorded_at_utc, str) or not recorded_at_utc.endswith("+00:00"):
        raise ValueError("recorded_at_utc must be an ISO-8601 UTC timestamp")

    total = len(clean_cases)
    pending = total - reviewed
    return {
        **public,
        "schema": SCHEMA,
        "dataset_id": did,
        "annotation_origin": (
            "RESEARCHER_SUPPLIED" if reviewed else "PENDING_RESEARCHER_ANNOTATION"
        ),
        "independence_verified": False,
        "reviewer": reviewer or None,
        "recorded_at_utc": recorded_at_utc,
        "status": (
            "COMPLETE_RESEARCHER_REVIEW"
            if reviewed == total
            else "PARTIAL_RESEARCHER_REVIEW"
            if reviewed
            else "PENDING_RESEARCHER_REVIEW"
        ),
        "review_stats": {
            "total": total,
            "reviewed": reviewed,
            "pending": pending,
            "coverage": round(reviewed / total, 4) if total else None,
        },
        "cases": clean_cases,
        "note": (
            "Researcher-supplied excerpt judgments are process evidence, not independently "
            "adjudicated scientific gold. independence_verified remains false."
        ),
    }


def labels_from_review_packet(data: dict, packet: dict) -> dict[str, str]:
    if not isinstance(packet, dict) or packet.get("schema") != SCHEMA:
        raise ValueError("Unexpected reviewer packet schema")
    if packet.get("dataset_id") != dataset_id(data):
        raise ValueError("Reviewer packet is not bound to the fixed dataset")
    labels = {}
    for row in packet.get("cases", []):
        if not isinstance(row, dict):
            raise ValueError("Reviewer packet cases must be objects")
        label = str(row.get("label", PENDING)).upper()
        if label in LABELS:
            labels[row["case_id"]] = label
        elif label != PENDING:
            raise ValueError("Invalid reviewer label")
    return labels

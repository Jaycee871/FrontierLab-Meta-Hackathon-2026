"""Normalized human-intervention events for process auditing.

Events record consequential researcher actions. They do not authenticate identity
and do not establish scientific correctness.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json

from .models import Run

SCHEMA = "frontierlab.human-intervention.v1"
KINDS = {
    "CLAIM_REVIEW_SAVED": "review",
    "METHOD_EVALUATION_SAVED": "decision",
    "PLANNING_APPROVED": "approval",
    "PLAN_STEP_APPROVED": "approval",
}


def record_human_event(
    run: Run,
    kind: str,
    artifact_id: str,
    *,
    actor_label: str = "unspecified_researcher",
    note: str = "",
    metadata: dict | None = None,
) -> dict:
    if kind not in KINDS:
        raise ValueError("Unsupported human-intervention event kind")
    if not isinstance(artifact_id, str) or not artifact_id.strip():
        raise ValueError("Human-intervention event requires an artifact ID")
    if not isinstance(actor_label, str):
        raise ValueError("actor_label must be text")
    if not isinstance(note, str) or len(note) > 1500:
        raise ValueError("Human-intervention note must be <= 1500 characters")
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("Human-intervention metadata must be an object")

    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    index = len(run.human_events)
    digest_input = {
        "kind": kind,
        "artifact_id": artifact_id.strip(),
        "time_utc": stamp,
        "index": index,
        "actor_label": actor_label.strip(),
    }
    event_id = sha256(
        json.dumps(digest_input, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:20]

    event = {
        "schema": SCHEMA,
        "event_id": event_id,
        "time_utc": stamp,
        "kind": kind,
        "severity": KINDS[kind],
        "artifact_id": artifact_id.strip(),
        "actor_label": actor_label.strip() or "unspecified_researcher",
        "identity_verified": False,
        "note": note.strip(),
        "metadata": metadata,
    }
    run.human_events.append(event)
    return event

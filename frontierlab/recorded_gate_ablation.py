"""Recorded 12-case Glimmer gate-ablation replay.

This module is safe to use in the public app: it only reads bundled static
records and performs deterministic calculations. It never calls a model.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .gate_ablation import compare_post_generation_gates
from .literature_pilot import LABELS, dataset_id, load_dataset

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "real_ph_excerpt_cases_v1.json"
PREDICTIONS = ROOT / "docs" / "runs" / "meta_pilot_predictions_20261028.json"
RECEIPT = ROOT / "docs" / "runs" / "meta_nim_pilot_20261028.json"


def _review_labels(path: str | Path | None, expected_dataset_id: str) -> dict[str, str]:
    if path is None:
        return {}
    review_path = Path(path)
    if not review_path.exists():
        raise ValueError("Supplied review path does not exist")
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("schema") != "frontierlab.real-excerpt-review.v1":
        raise ValueError("Unexpected review schema")
    if review.get("dataset_id") != expected_dataset_id:
        raise ValueError("Review is not bound to the fixed ablation dataset")
    if review.get("annotation_origin") != "RESEARCHER_SUPPLIED":
        raise ValueError("Only explicitly researcher-supplied review labels may be used")
    rows = review.get("cases")
    if not isinstance(rows, list):
        raise ValueError("Review cases required")

    labels = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Review rows must be objects")
        cid = row.get("case_id")
        label = str(row.get("label", "")).upper()
        if not isinstance(cid, str) or label not in LABELS or cid in labels:
            raise ValueError("Review rows require unique valid case IDs and labels")
        labels[cid] = label
    return labels


def run_recorded_pilot(*, review_path: str | Path | None = None, review_labels: dict[str, str] | None = None) -> dict:
    data = load_dataset(DATASET)
    packet = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    recorded = json.loads(RECEIPT.read_text(encoding="utf-8"))
    receipt = recorded["receipt"]

    did = dataset_id(data)
    if packet.get("dataset_id") != did or receipt.get("dataset_id") != did:
        raise ValueError("Recorded predictions / receipt do not match the fixed dataset")
    if receipt.get("predictions") != packet:
        raise ValueError("Prediction snapshot differs from the recorded NIM receipt")

    cases = [
        {"case_id": row["case_id"], "source_id": row["source_id"]}
        for row in data["cases"]
    ]
    source_texts = {
        row["source_id"]: row["source_text"]
        for row in data["sources"]
    }
    if review_path is not None and review_labels is not None:
        raise ValueError("Use review_path or review_labels, not both")
    reviews = _review_labels(review_path, did)
    if review_labels is not None:
        if not isinstance(review_labels, dict):
            raise ValueError("review_labels must be a mapping")
        valid_case_ids = {row["case_id"] for row in data["cases"]}
        reviews = {}
        for cid, label in review_labels.items():
            label = str(label).upper()
            if cid not in valid_case_ids or label not in LABELS:
                raise ValueError("Direct review label does not match the fixed case set")
            reviews[cid] = label

    result = compare_post_generation_gates(
        cases,
        packet["cases"],
        source_texts,
        reviews=reviews,
        independent_gold=None,
        independent_gold_verified=False,
    )
    experiment_id = hashlib.sha256(
        json.dumps(
            {
                "dataset_id": did,
                "model_id": packet["model_id"],
                "recorded_output_sha256": receipt["output_sha256"],
                "comparison_type": result["comparison_type"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()

    result.update({
        "record_type": "frontierlab_recorded_gate_ablation",
        "experiment_id": experiment_id,
        "dataset_id": did,
        "model_id": packet["model_id"],
        "execution_origin": packet["execution_origin"],
        "new_model_calls": 0,
        "recorded_model_call": {
            "github_run_url": recorded["github_run_url"],
            "input_scope": receipt["input_scope"],
            "requested_model": receipt["requested_model"],
            "reported_model": receipt["reported_model"],
            "input_sha256": receipt["input_sha256"],
            "output_sha256": receipt["output_sha256"],
            "elapsed_seconds": receipt["elapsed_seconds"],
            "usage": receipt["usage"],
        },
        "human_review_status": (
            "REVIEW_LABELS_SUPPLIED" if reviews else "PENDING_12_CASE_RESEARCHER_REVIEW"
        ),
        "accuracy_status": "UNAVAILABLE_NO_INDEPENDENT_GOLD",
        "draft_reference_labels_used_as_gold": False,
        "scientific_accuracy_measured": False,
    })
    return result

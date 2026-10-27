"""Validate a recorded reviewed-continuation result without making any network calls.

This module does not call models, read secrets or mutate a research run. It checks
that a saved continuation artifact stayed within FrontierLab's two-call boundary
and prepares a researcher-facing method-evaluation handoff packet.
"""
from __future__ import annotations

import json
from pathlib import Path

EXPECTED_ROLES = ["Adversarial Skeptic Agent", "Hypothesis Agent"]
EXPECTED_MODEL = "meta/muse-glimmer-30b"
SUCCESS = {
    "REAL_RESEARCH_SYNTHESIS_COMPLETED_METHOD_REVIEW_REQUIRED",
    "REAL_RESEARCH_SYNTHESIS_COMPLETED_NO_HYPOTHESIS",
}


def validate_record(record: dict) -> dict:
    if not isinstance(record, dict):
        raise ValueError("Continuation record must be a JSON object")
    if record.get("record_type") != "nim_research_human_reviewed_continuation":
        raise ValueError("Unexpected continuation record type")
    if record.get("status") not in SUCCESS:
        raise ValueError("Continuation did not complete successfully")
    if record.get("maximum_new_model_calls") != 2:
        raise ValueError("Continuation call boundary changed")
    if record.get("automatic_method_selection") is not False:
        raise ValueError("Automatic method selection must remain disabled")
    if record.get("automatic_planning") is not False:
        raise ValueError("Automatic planning must remain disabled")

    inference = record.get("continuation_inference")
    if not isinstance(inference, dict):
        raise ValueError("Missing continuation inference provenance")
    if inference.get("provider") != "nvidia-nim":
        raise ValueError("Unexpected inference provider")
    if inference.get("model") != EXPECTED_MODEL:
        raise ValueError("Unexpected model identity")
    if inference.get("attempted_calls") != 2:
        raise ValueError("Expected exactly two attempted model calls")

    receipts = inference.get("receipts")
    if not isinstance(receipts, list) or len(receipts) != 2:
        raise ValueError("Expected exactly two call receipts")
    roles = [item.get("role") for item in receipts if isinstance(item, dict)]
    if roles != EXPECTED_ROLES:
        raise ValueError("Unexpected continuation role order")
    for receipt in receipts:
        if receipt.get("reported_model") != EXPECTED_MODEL:
            raise ValueError("Receipt model identity mismatch")
        if receipt.get("finish_reason") != "stop":
            raise ValueError("Continuation contains an incomplete model response")
        if receipt.get("status") != "JSON_OBJECT_RETURNED":
            raise ValueError("Continuation call did not return a validated JSON object")
        if not isinstance(receipt.get("input_sha256"), str) or len(receipt["input_sha256"]) != 64:
            raise ValueError("Missing input hash")
        if not isinstance(receipt.get("output_sha256"), str) or len(receipt["output_sha256"]) != 64:
            raise ValueError("Missing output hash")

    run = record.get("run")
    if not isinstance(run, dict):
        raise ValueError("Missing research run")
    if run.get("backend") != "nvidia-nim" or run.get("model") != EXPECTED_MODEL:
        raise ValueError("Run backend/model mismatch")
    if run.get("evaluation") is not None or run.get("plan") is not None:
        raise ValueError("Continuation crossed the human method/planning boundary")

    review = run.get("review")
    if not isinstance(review, dict) or review.get("status") != "READY_FOR_HUMAN_GATED_SYNTHESIS":
        raise ValueError("Completed source-bound human review is missing")
    stats = review.get("review_stats", {})
    if stats.get("supported_distinct_sources", 0) < 2 or stats.get("pending", 1) != 0:
        raise ValueError("Human review is incomplete or lacks two supported sources")

    allowed = {
        case.get("paper_id")
        for case in review.get("cases", [])
        if isinstance(case, dict) and case.get("review_label") == "SUPPORTED"
    }
    hypotheses = run.get("hypotheses")
    if not isinstance(hypotheses, list):
        raise ValueError("Hypotheses must be a list")
    for item in hypotheses:
        if not isinstance(item, dict):
            raise ValueError("Invalid hypothesis object")
        ids = item.get("evidence_ids")
        if not isinstance(ids, list) or not ids or any(source not in allowed for source in ids):
            raise ValueError("Hypothesis cites a source outside the human-supported set")
        if not isinstance(item.get("text"), str) or not item["text"].strip():
            raise ValueError("Hypothesis text is missing")
        if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
            raise ValueError("Hypothesis rationale is missing")

    return {
        "schema": "frontierlab.method-handoff.v1",
        "status": "READY_FOR_RESEARCHER_METHOD_EVALUATION" if hypotheses else "NO_HYPOTHESIS_TO_EVALUATE",
        "source_continuation_status": record["status"],
        "model": EXPECTED_MODEL,
        "provider": "nvidia-nim",
        "verified_call_count": 2,
        "verified_role_order": EXPECTED_ROLES,
        "human_review_dataset_id": review.get("dataset_id"),
        "supported_source_ids": sorted(allowed),
        "hypotheses": hypotheses,
        "skeptic": run.get("skeptic"),
        "method_selection_automated": False,
        "planning_automated": False,
        "scientific_accuracy_verified": False,
        "note": (
            "This packet verifies execution boundaries and provenance only. "
            "A researcher must still compare candidate methods and decide whether to proceed."
        ),
    }


def validate_file(path: str | Path) -> dict:
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_record(record)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("record")
    parser.add_argument("--output", default="nim_method_handoff.json")
    args = parser.parse_args()
    handoff = validate_file(args.record)
    Path(args.output).write_text(
        json.dumps(handoff, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(handoff, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

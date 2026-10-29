"""Two-call, same-model/same-cases prompt-level gate ablation on NVIDIA NIM.

Call 1: label-only task (no evidence-quote requirement).
Call 2: quote-grounded task; deterministic source/quote gate is then applied.

Human review is a later offline step. No automatic retry is permitted.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os

from frontierlab.gate_ablation import compare_prompt_arms
from frontierlab.literature_pilot import dataset_id, load_dataset, public_cases
from frontierlab.research_backend import CallBudget, NvidiaResearchClient
from scripts.smoke_nvidia_muse import _run_context

ROLE = "Evidence Extraction Agent"


def _payload(data: dict) -> dict:
    return public_cases(data)


def _payload_hash(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _validate_predictions(answer: dict, data: dict, *, require_quote: bool) -> list[dict]:
    rows = answer.get("cases") if isinstance(answer, dict) else None
    if not isinstance(rows, list):
        raise ValueError("Ablation response requires a cases list")

    expected = {row["case_id"]: row["source_id"] for row in data["cases"]}
    seen = set()
    clean = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Ablation case output must be an object")
        cid = row.get("case_id")
        sid = row.get("source_id")
        label = str(row.get("label", "")).upper()
        if cid not in expected or cid in seen or sid != expected[cid]:
            raise ValueError("Ablation output changed the fixed case/source mapping")
        if label not in {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT"}:
            raise ValueError("Ablation output has an invalid label")
        item = {"case_id": cid, "source_id": sid, "label": label}
        if require_quote:
            quote = row.get("evidence_quote")
            if not isinstance(quote, str):
                raise ValueError("Quote-grounded arm requires evidence_quote text")
            item["evidence_quote"] = quote
        clean.append(item)
        seen.add(cid)
    if set(expected) != seen:
        raise ValueError("Ablation output must contain every fixed case exactly once")
    return clean


def run_with_client(model_client, *, data: dict | None = None) -> dict:
    data = load_dataset() if data is None else data
    payload = _payload(data)
    payload_sha = _payload_hash(payload)

    raw_answer = model_client.json(
        ROLE,
        (
            "For every supplied case, judge only SUPPORTED, CONTRADICTED or INSUFFICIENT "
            "from the supplied short source excerpt. Return "
            '{"cases":[{"case_id":"...","source_id":"...","label":"..."}]}. '
            "Return only those three fields for each case; do not add extra fields."
        ),
        payload,
    )
    raw_rows = _validate_predictions(raw_answer, data, require_quote=False)

    grounded_answer = model_client.json(
        ROLE,
        (
            "For every supplied case, judge only SUPPORTED, CONTRADICTED or INSUFFICIENT "
            "from the same supplied short source excerpt. Return "
            '{"cases":[{"case_id":"...","source_id":"...","label":"...",'
            '"evidence_quote":"..."}]}. For SUPPORTED or CONTRADICTED, evidence_quote '
            "must be one exact contiguous 24-500 character quote from that case's source. "
            "For INSUFFICIENT, use an empty evidence_quote."
        ),
        payload,
    )
    grounded_rows = _validate_predictions(grounded_answer, data, require_quote=True)

    cases = [
        {"case_id": row["case_id"], "source_id": row["source_id"]}
        for row in data["cases"]
    ]
    source_texts = {
        row["source_id"]: row["source_text"]
        for row in data["sources"]
    }
    comparison = compare_prompt_arms(
        cases,
        raw_rows,
        grounded_rows,
        source_texts,
        reviews=None,
        independent_gold=None,
        independent_gold_verified=False,
    )
    comparison.update({
        "record_type": "frontierlab_nim_gate_ablation_trial",
        "dataset_id": dataset_id(data),
        "same_case_payload_sha256": payload_sha,
        "same_model_required": True,
        "new_model_calls": 2,
        "human_review_status": "PENDING_12_CASE_RESEARCHER_REVIEW",
        "accuracy_status": "UNAVAILABLE_NO_INDEPENDENT_GOLD",
        "draft_reference_labels_used_as_gold": False,
        "scientific_accuracy_measured": False,
    })
    return comparison


def main() -> None:
    if os.getenv("FRONTIERLAB_GATE_ABLATION_TRIAL") != "YES":
        raise PermissionError("Gate-ablation trial disabled; explicit opt-in required")
    if os.getenv("FRONTIERLAB_NIM_RESEARCH") != "YES":
        raise PermissionError("NVIDIA research backend is not enabled")

    client = NvidiaResearchClient(
        authorized=True,
        budget=CallBudget(limit=2),
    )
    record = {
        "record_type": "frontierlab_nim_gate_ablation_wrapper",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "maximum_model_calls": 2,
        "automatic_retry": False,
        "human_review_automated": False,
        "independent_gold_supplied": False,
        **_run_context(),
    }
    try:
        result = run_with_client(client)
        if client.provenance.get("attempted_calls") != 2:
            raise RuntimeError("Gate-ablation trial did not use exactly two model calls")
        record.update(
            status="PROMPT_LEVEL_ABLATION_COMPLETED_HUMAN_REVIEW_PENDING",
            comparison=result,
            inference=client.provenance,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False))
    except Exception:
        record.update(
            status="PROMPT_LEVEL_ABLATION_FAILED_NO_RETRY",
            inference=client.provenance,
        )
        print(json.dumps(record, ensure_ascii=False, indent=2, allow_nan=False))
        raise


if __name__ == "__main__":
    main()

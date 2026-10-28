"""Optional edge structured worker for Muse Research Muse2-230M.

This module intentionally limits Muse2 to low-risk preprocessing:
metadata normalization, log-to-JSON extraction, schema formatting and routing.

It must not be used as a scientific truth/entailment/medical decision engine.
The core FrontierLab installation never downloads or initializes the model.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import time
from typing import Any

MODEL_ID = "Muse-research/Muse2-230M"
BACKEND = "muse2-edge-local"
SCHEMA = "frontierlab.edge-structured-worker.v1"

ALLOWED_TASKS = {
    "metadata_normalization",
    "log_to_json",
    "schema_formatting",
    "routing",
}

FORBIDDEN_FIELDS = {
    "supported",
    "contradicted",
    "entailment",
    "truth",
    "diagnosis",
    "treatment",
    "efficacy",
    "safety",
    "medical_advice",
    "clinical_decision",
}

TYPE_NAMES = {"string", "number", "integer", "boolean", "array", "object"}


def _digest(value: Any) -> str:
    return sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _validate_schema(schema: dict) -> dict:
    if not isinstance(schema, dict) or not schema:
        raise ValueError("A nonempty output schema is required")
    if len(schema) > 32:
        raise ValueError("Edge schema is limited to 32 fields")
    clean = {}
    for key, type_name in schema.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Schema field names must be nonempty strings")
        normalized_key = key.strip()
        if normalized_key.lower() in FORBIDDEN_FIELDS:
            raise PermissionError(
                "Muse2 edge worker cannot emit scientific/medical truth-decision fields"
            )
        if type_name not in TYPE_NAMES:
            raise ValueError("Unsupported schema type: " + str(type_name))
        clean[normalized_key] = type_name
    return clean


def _validate_value(value: Any, type_name: str, field: str) -> None:
    ok = {
        "string": isinstance(value, str),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "array": isinstance(value, list),
        "object": isinstance(value, dict),
    }[type_name]
    if not ok:
        raise ValueError(f"Field {field} does not match declared type {type_name}")


def validate_output(raw: Any, schema: dict) -> dict:
    schema = _validate_schema(schema)
    if not isinstance(raw, dict):
        raise ValueError("Muse2 edge worker output must be a JSON object")
    if set(raw) != set(schema):
        raise ValueError("Muse2 output fields must exactly match the requested schema")
    for field, type_name in schema.items():
        _validate_value(raw[field], type_name, field)
    return raw


@dataclass(frozen=True)
class EdgeWorkerRecord:
    schema: str
    backend: str
    model: str
    task: str
    input_sha256: str
    schema_sha256: str
    output_sha256: str
    elapsed_seconds: float
    scientific_entailment_verified: bool
    researcher_review_required_for_scientific_use: bool
    note: str

    def as_dict(self) -> dict:
        return asdict(self)


class Muse2EdgeWorker:
    """Adapter around an already-loaded local Muse2 runtime.

    The injected runtime must expose:

        complete(messages=[...], max_new_tokens=..., temperature=..., top_k=...)

    and return the generated assistant text.
    """

    model = MODEL_ID
    backend = BACKEND

    def __init__(self, runtime: Any):
        if runtime is None or not callable(getattr(runtime, "complete", None)):
            raise TypeError("Muse2 edge worker requires a runtime exposing complete()")
        self._runtime = runtime
        self.receipts: list[dict] = []

    def extract(self, *, raw_text: str, schema: dict, task: str) -> tuple[dict, EdgeWorkerRecord]:
        if task not in ALLOWED_TASKS:
            raise PermissionError("Task is outside the Muse2 edge preprocessing boundary")
        if not isinstance(raw_text, str) or not raw_text.strip():
            raise ValueError("Nonempty input text is required")
        if len(raw_text) > 200_000:
            raise ValueError("Edge preprocessing input is too large")
        clean_schema = _validate_schema(schema)

        system = (
            "You are a silent structured-data compiler. "
            "Return exactly one JSON object matching the requested schema. "
            "Do not add commentary, infer missing scientific facts, judge whether a claim is true, "
            "or provide medical/scientific conclusions. Use only the supplied text."
        )
        user = (
            "TASK: " + task +
            "\nOUTPUT_SCHEMA: " + json.dumps(clean_schema, ensure_ascii=False, allow_nan=False) +
            "\nRAW_TEXT:\n" + raw_text.strip()
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        started = time.perf_counter()
        text = self._runtime.complete(
            messages=messages,
            max_new_tokens=256,
            temperature=0.2,
            top_k=50,
        )
        elapsed = round(time.perf_counter() - started, 3)
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Muse2 edge runtime returned no output")

        try:
            parsed = json.loads(text)
        except (TypeError, ValueError):
            raise ValueError("Muse2 edge output is not valid JSON") from None
        parsed = validate_output(parsed, clean_schema)

        record = EdgeWorkerRecord(
            schema=SCHEMA,
            backend=self.backend,
            model=self.model,
            task=task,
            input_sha256=sha256(raw_text.strip().encode("utf-8")).hexdigest(),
            schema_sha256=_digest(clean_schema),
            output_sha256=_digest(parsed),
            elapsed_seconds=elapsed,
            scientific_entailment_verified=False,
            researcher_review_required_for_scientific_use=True,
            note=(
                "Muse2-230M is used only for low-risk preprocessing and formatting. "
                "Its output is not evidence that a scientific claim is correct."
            ),
        )
        self.receipts.append(record.as_dict())
        return parsed, record

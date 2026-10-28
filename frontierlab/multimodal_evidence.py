"""Optional multimodal evidence gate for Liquid AI d1-2B.

The core FrontierLab package does not download or initialize d1-2B.  Instead,
this module defines a strict adapter around an already-loaded object exposing
Liquid AI's documented `system_one(state, questions, media=...)` interface.

d1 decisions are model signals, not scientific entailment or ground truth.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any

MODEL_ID = "LiquidAI/d1-2B"
BACKEND = "liquid-d1-local"
SCHEMA = "frontierlab.multimodal-evidence.v1"

QUESTION_TYPES = {
    "noul", "choice", "score", "text", "number", "date", "box", "boxes"
}


def scientific_figure_questions(claim: str) -> dict:
    """Typed questions for one scientific figure/table image.

    These intentionally separate visual relevance, support and contradiction.
    No hard decision threshold is embedded because d1 probabilities must be
    calibrated on the user's own validation data.
    """
    if not isinstance(claim, str) or not claim.strip():
        raise ValueError("A nonempty scientific claim is required")
    claim = claim.strip()
    return {
        "relevant": {
            "type": "noul",
            "instructions": (
                "Does this image contain visual evidence relevant to the following scientific claim? "
                "Use only what is visibly present in the image. Claim: " + claim
            ),
        },
        "supports": {
            "type": "noul",
            "instructions": (
                "Does the visible figure/table evidence directly support this scientific claim? "
                "Do not infer missing methods or results. Claim: " + claim
            ),
        },
        "contradicts": {
            "type": "noul",
            "instructions": (
                "Does the visible figure/table evidence directly contradict this scientific claim? "
                "Do not infer missing methods or results. Claim: " + claim
            ),
        },
        "evidence_region": {
            "type": "box",
            "instructions": (
                "If one region of the image is most relevant to evaluating the claim, locate it. "
                "Claim: " + claim
            ),
        },
        "visible_value": {
            "type": "text",
            "instructions": (
                "Read the single most relevant visible numeric value, statistic, axis label or short "
                "text span for evaluating the claim. Return not found if none is visible. Claim: " + claim
            ),
        },
    }


def _hash_json(value: Any) -> str:
    return sha256(json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def validate_question_schema(questions: dict) -> None:
    if not isinstance(questions, dict) or not questions:
        raise ValueError("Questions must be a nonempty object")
    for name, question in questions.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(question, dict):
            raise ValueError("Invalid named d1 question")
        qtype = question.get("type")
        if qtype not in QUESTION_TYPES:
            raise ValueError("Unsupported d1 question type: " + str(qtype))
        instructions = question.get("instructions")
        if not isinstance(instructions, str) or not instructions.strip():
            raise ValueError("Each d1 question requires instructions")


def _probability(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(label + " must be a probability")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(label + " must be between 0 and 1")
    return value


def validate_d1_output(raw: dict, questions: dict) -> dict:
    """Validate only the fields FrontierLab depends on.

    The output is kept intact for auditability; this function does not convert a
    model probability into a scientific truth label.
    """
    validate_question_schema(questions)
    if not isinstance(raw, dict):
        raise ValueError("d1 output must be a JSON-like object")
    answers = raw.get("answers")
    usage = raw.get("usage")
    if not isinstance(answers, dict) or not isinstance(usage, dict):
        raise ValueError("d1 output requires answers and usage")
    if set(answers) != set(questions):
        raise ValueError("d1 answer names must exactly match requested questions")
    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if not isinstance(input_tokens, int) or input_tokens < 0:
        raise ValueError("Invalid d1 input token count")
    if output_tokens != 0:
        raise ValueError("d1 decision output is expected to report zero output tokens")

    for name, question in questions.items():
        answer = answers[name]
        if not isinstance(answer, dict):
            raise ValueError("Each d1 answer must be an object")
        qtype = question["type"]
        if qtype == "noul":
            _probability(answer.get("noul"), name + ".noul")
        elif qtype == "box":
            found = _probability(answer.get("found"), name + ".found")
            box = answer.get("box")
            if found >= 0.5:
                if not isinstance(box, dict) or set(box) != {"top", "bottom", "left", "right"}:
                    raise ValueError("Found box requires top/bottom/left/right coordinates")
                for key, value in box.items():
                    _probability(value, name + ".box." + key)
        elif qtype == "text":
            found = _probability(answer.get("found"), name + ".found")
            text = answer.get("text")
            if found >= 0.5 and (not isinstance(text, str) or not text.strip()):
                raise ValueError("Found text answer requires nonempty text")
    return raw


def decision_view(raw: dict, *, threshold: float | None = None) -> dict:
    """Create a researcher-facing view without claiming entailment.

    If no calibrated threshold is supplied, all yes/no outputs remain numeric
    signals.  If supplied, the threshold must be explicitly user-calibrated.
    """
    if threshold is not None:
        threshold = _probability(threshold, "threshold")
    answers = raw["answers"]
    result = {
        "calibration_status": (
            "USER_CALIBRATED_THRESHOLD_SUPPLIED"
            if threshold is not None else "REQUIRES_LOCAL_CALIBRATION"
        ),
        "threshold": threshold,
        "signals": {},
    }
    for key in ("relevant", "supports", "contradicts"):
        if key in answers:
            p = float(answers[key]["noul"])
            result["signals"][key] = {
                "probability_yes": p,
                "thresholded": (p >= threshold) if threshold is not None else None,
            }
    if "evidence_region" in answers:
        result["evidence_region"] = answers["evidence_region"]
    if "visible_value" in answers:
        result["visible_value"] = answers["visible_value"]
    return result


@dataclass(frozen=True)
class MultimodalEvidenceRecord:
    schema: str
    backend: str
    model: str
    claim: str
    questions_sha256: str
    answers_sha256: str
    usage: dict
    decision: dict
    scientific_entailment_verified: bool
    researcher_review_required: bool
    note: str

    def as_dict(self) -> dict:
        return asdict(self)


class D1EvidenceGate:
    """Adapter for an already-loaded local d1-2B object."""

    backend = BACKEND
    model = MODEL_ID

    def __init__(self, model: Any):
        if model is None or not callable(getattr(model, "system_one", None)):
            raise TypeError("d1 adapter requires an object exposing system_one()")
        self._model = model

    def inspect(self, *, claim: str, media: list, state: Any = None,
                threshold: float | None = None) -> MultimodalEvidenceRecord:
        if not isinstance(media, list) or not media:
            raise ValueError("At least one image or video media item is required")
        questions = scientific_figure_questions(claim)
        raw = self._model.system_one(state, questions, media=media)
        validate_d1_output(raw, questions)
        view = decision_view(raw, threshold=threshold)
        return MultimodalEvidenceRecord(
            schema=SCHEMA,
            backend=self.backend,
            model=self.model,
            claim=claim.strip(),
            questions_sha256=_hash_json(questions),
            answers_sha256=_hash_json(raw["answers"]),
            usage=dict(raw["usage"]),
            decision=view,
            scientific_entailment_verified=False,
            researcher_review_required=True,
            note=(
                "d1-2B provides multimodal decision signals only. A probability, extracted value "
                "or localized image region does not establish scientific support. Thresholds require "
                "local calibration and a researcher must review the original figure/table and methods."
            ),
        )

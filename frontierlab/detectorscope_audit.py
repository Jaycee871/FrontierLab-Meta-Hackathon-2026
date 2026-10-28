"""Optional DetectorScope explainability / output-audit lens.

DetectorScope is used only as a diagnostic instrument for inspecting linguistic
features associated with an AI-text detector decision. It must never be used as
the basis for academic-integrity, hiring, publication, or scientific-truth
decisions.

The core FrontierLab installation does not import or download DetectorScope.
A caller injects an already-loaded callable detector.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json
from typing import Any

SCHEMA = "frontierlab.detectorscope-audit.v1"
BACKEND = "detectorscope-local"
DEFAULT_TAU = 0.85
ALLOWED_HEADS = {"logreg", "xgboost"}

FORBIDDEN_USES = {
    "academic_integrity",
    "student_discipline",
    "hiring",
    "publication_decision",
    "authorship_attribution",
    "scientific_truth",
}


def _probability(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(name + " must be numeric")
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(name + " must be between 0 and 1")
    return value


def validate_tau(tau: float) -> float:
    tau = _probability(tau, "tau")
    if round(tau * 20) != tau * 20:
        raise ValueError("tau must use DetectorScope's 0.05 increments")
    if tau > 0.95:
        raise ValueError("tau must be <= 0.95")
    return tau


def _hash_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _normalize_feature(feature: Any, tokens: list[str] | None) -> dict:
    description = getattr(feature, "description", None)
    importance = getattr(feature, "importance", None)
    if not isinstance(description, str) or not description.strip():
        raise ValueError("DetectorScope feature requires a description")
    if not isinstance(importance, (int, float)) or isinstance(importance, bool):
        raise ValueError("DetectorScope feature requires numeric importance")

    normalized = {
        "description": description.strip(),
        "importance": float(importance),
    }

    highlights = getattr(feature, "highlights", None)
    if highlights is not None:
        if not isinstance(highlights, list):
            raise ValueError("DetectorScope highlights must be a list")
        safe = []
        for pair in highlights:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError("Each DetectorScope highlight must be (token_index, activation)")
            index, activation = pair
            if not isinstance(index, int) or index < 0:
                raise ValueError("Invalid highlight token index")
            if not isinstance(activation, (int, float)) or isinstance(activation, bool):
                raise ValueError("Invalid highlight activation")
            item = {"token_index": index, "activation": float(activation)}
            if tokens is not None and index < len(tokens):
                item["token"] = tokens[index]
            safe.append(item)
        normalized["highlights"] = safe
    return normalized


@dataclass(frozen=True)
class DetectorAuditRecord:
    schema: str
    backend: str
    detector_id: str
    tau: float
    head: str
    input_sha256: str
    label: str
    p_ai: float
    logit: float
    bias: float
    features: list[dict]
    feature_count: int
    diagnostic_only: bool
    individual_decision_forbidden: bool
    scientific_truth_verified: bool
    note: str

    def as_dict(self) -> dict:
        return asdict(self)


class DetectorScopeAuditLens:
    """Adapter around an already-loaded DetectorScope AuditableDetector-like object."""

    backend = BACKEND

    def __init__(
        self,
        detector: Any,
        *,
        detector_id: str,
        tau: float = DEFAULT_TAU,
        head: str = "logreg",
    ):
        if detector is None or not callable(detector):
            raise TypeError("DetectorScope audit lens requires a callable detector")
        if not isinstance(detector_id, str) or not detector_id.strip():
            raise ValueError("DetectorScope detector_id is required")
        if head not in ALLOWED_HEADS:
            raise ValueError("Unsupported DetectorScope head")
        self._detector = detector
        self.detector_id = detector_id.strip()
        self.tau = validate_tau(tau)
        self.head = head

    def inspect(self, text: str, *, intended_use: str = "model_output_audit") -> DetectorAuditRecord:
        if intended_use in FORBIDDEN_USES:
            raise PermissionError("DetectorScope use is forbidden for individual/high-stakes decisions")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Nonempty text is required")
        if len(text) > 200_000:
            raise ValueError("DetectorScope audit input is too large")

        output = self._detector(
            text,
            tau=self.tau,
            head=self.head,
            return_highlights=True,
        )

        label = getattr(output, "label", None)
        p_ai = getattr(output, "p_ai", None)
        logit = getattr(output, "logit", None)
        bias = getattr(output, "bias", None)
        features = getattr(output, "features", None)
        tokens = getattr(output, "tokens", None)

        if not isinstance(label, str) or not label.strip():
            raise ValueError("DetectorScope output requires a label")
        p_ai = _probability(p_ai, "p_ai")
        if not isinstance(logit, (int, float)) or isinstance(logit, bool):
            raise ValueError("DetectorScope output requires numeric logit")
        if not isinstance(bias, (int, float)) or isinstance(bias, bool):
            raise ValueError("DetectorScope output requires numeric bias")
        if not isinstance(features, list):
            raise ValueError("DetectorScope output requires a feature list")
        if tokens is not None and not isinstance(tokens, list):
            raise ValueError("DetectorScope tokens must be a list when present")

        normalized_features = [_normalize_feature(feature, tokens) for feature in features]

        return DetectorAuditRecord(
            schema=SCHEMA,
            backend=self.backend,
            detector_id=self.detector_id,
            tau=self.tau,
            head=self.head,
            input_sha256=_hash_text(text.strip()),
            label=label.strip(),
            p_ai=p_ai,
            logit=float(logit),
            bias=float(bias),
            features=normalized_features,
            feature_count=len(normalized_features),
            diagnostic_only=True,
            individual_decision_forbidden=True,
            scientific_truth_verified=False,
            note=(
                "DetectorScope is a research diagnostic for interpretable detector features. "
                "Its label and p_ai can be wrong, especially out of domain, and must not be used "
                "for academic-integrity, hiring, publication, authorship, or scientific-truth decisions."
            ),
        )


def comparison_dimensions() -> list[str]:
    return [
        "p_ai",
        "feature_count",
        "positive_feature_importance_sum",
        "negative_feature_importance_sum",
        "top_positive_feature",
        "top_negative_feature",
    ]


def summarize_record(record: DetectorAuditRecord) -> dict:
    positives = [f for f in record.features if f["importance"] > 0]
    negatives = [f for f in record.features if f["importance"] < 0]
    positives.sort(key=lambda x: x["importance"], reverse=True)
    negatives.sort(key=lambda x: x["importance"])
    return {
        "p_ai": record.p_ai,
        "feature_count": record.feature_count,
        "positive_feature_importance_sum": round(sum(f["importance"] for f in positives), 6),
        "negative_feature_importance_sum": round(sum(f["importance"] for f in negatives), 6),
        "top_positive_feature": positives[0]["description"] if positives else None,
        "top_negative_feature": negatives[0]["description"] if negatives else None,
    }

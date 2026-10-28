import pytest

from frontierlab.multimodal_evidence import (
    D1EvidenceGate,
    decision_view,
    scientific_figure_questions,
    validate_d1_output,
)


class FakeD1:
    def __init__(self):
        self.calls = []

    def system_one(self, state, questions, media=None):
        self.calls.append((state, questions, media))
        return {
            "answers": {
                "relevant": {"noul": 0.98},
                "supports": {"noul": 0.81},
                "contradicts": {"noul": 0.07},
                "evidence_region": {
                    "found": 0.91,
                    "confidence": 0.88,
                    "box": {"top": 0.1, "bottom": 0.5, "left": 0.2, "right": 0.8},
                },
                "visible_value": {
                    "found": 0.93,
                    "text": "25-fold",
                    "span": [12, 19],
                },
            },
            "usage": {"input_tokens": 412, "output_tokens": 0},
        }


def test_scientific_questions_are_typed_and_claim_bound():
    q = scientific_figure_questions("Acidic-pH selectivity improved 25-fold.")
    assert set(q) == {"relevant", "supports", "contradicts", "evidence_region", "visible_value"}
    assert q["supports"]["type"] == "noul"
    assert q["evidence_region"]["type"] == "box"
    assert "25-fold" in q["supports"]["instructions"]


def test_gate_keeps_d1_as_signal_not_entailment():
    model = FakeD1()
    record = D1EvidenceGate(model).inspect(
        claim="Acidic-pH selectivity improved 25-fold.",
        media=[object()],
    )
    assert len(model.calls) == 1
    assert record.model == "LiquidAI/d1-2B"
    assert record.backend == "liquid-d1-local"
    assert record.usage == {"input_tokens": 412, "output_tokens": 0}
    assert record.decision["calibration_status"] == "REQUIRES_LOCAL_CALIBRATION"
    assert record.decision["signals"]["supports"]["probability_yes"] == 0.81
    assert record.decision["signals"]["supports"]["thresholded"] is None
    assert record.scientific_entailment_verified is False
    assert record.researcher_review_required is True
    assert len(record.questions_sha256) == 64
    assert len(record.answers_sha256) == 64


def test_explicit_calibrated_threshold_can_create_thresholded_view():
    raw = FakeD1().system_one(None, scientific_figure_questions("x"), media=[object()])
    view = decision_view(raw, threshold=0.8)
    assert view["calibration_status"] == "USER_CALIBRATED_THRESHOLD_SUPPLIED"
    assert view["signals"]["supports"]["thresholded"] is True
    assert view["signals"]["contradicts"]["thresholded"] is False


def test_validator_rejects_wrong_answer_names():
    q = scientific_figure_questions("x")
    raw = FakeD1().system_one(None, q, media=[object()])
    raw["answers"].pop("visible_value")
    with pytest.raises(ValueError, match="exactly match"):
        validate_d1_output(raw, q)


def test_validator_rejects_generative_output_tokens():
    q = scientific_figure_questions("x")
    raw = FakeD1().system_one(None, q, media=[object()])
    raw["usage"]["output_tokens"] = 3
    with pytest.raises(ValueError, match="zero output tokens"):
        validate_d1_output(raw, q)


def test_gate_requires_media_and_system_one_interface():
    with pytest.raises(TypeError, match="system_one"):
        D1EvidenceGate(object())
    with pytest.raises(ValueError, match="media"):
        D1EvidenceGate(FakeD1()).inspect(claim="x", media=[])

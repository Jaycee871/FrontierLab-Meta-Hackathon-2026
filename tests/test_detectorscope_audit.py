from types import SimpleNamespace
import pytest

from frontierlab.detectorscope_audit import (
    DetectorScopeAuditLens,
    comparison_dimensions,
    summarize_record,
    validate_tau,
)


class FakeDetector:
    def __init__(self):
        self.calls = []

    def __call__(self, text, **kwargs):
        self.calls.append((text, kwargs))
        return SimpleNamespace(
            label="ai",
            p_ai=0.88,
            logit=1.3,
            bias=0.2,
            tokens=["Like", "I", "said", ",", "about"],
            features=[
                SimpleNamespace(
                    description="repeated phrases or sequences in text",
                    importance=0.23,
                    highlights=[(4, 1.7)],
                ),
                SimpleNamespace(
                    description="conversational filler phrase",
                    importance=-0.05,
                    highlights=[(0, 0.4), (2, 0.8)],
                ),
            ],
        )


def test_audit_lens_preserves_interpretable_feature_contributions():
    detector = FakeDetector()
    lens = DetectorScopeAuditLens(
        detector,
        detector_id="liamdugan/detector-scope",
        tau=0.85,
    )
    record = lens.inspect("Like I said, about this.")
    assert record.label == "ai"
    assert record.p_ai == 0.88
    assert record.feature_count == 2
    assert record.features[0]["description"] == "repeated phrases or sequences in text"
    assert record.features[0]["highlights"][0]["token"] == "about"
    assert record.diagnostic_only is True
    assert record.individual_decision_forbidden is True
    assert record.scientific_truth_verified is False
    assert len(record.input_sha256) == 64
    assert detector.calls[0][1] == {
        "tau": 0.85,
        "head": "logreg",
        "return_highlights": True,
    }


def test_forbidden_high_stakes_uses_are_rejected_before_detector_call():
    detector = FakeDetector()
    lens = DetectorScopeAuditLens(detector, detector_id="x")
    for use in (
        "academic_integrity", "student_discipline", "hiring",
        "publication_decision", "authorship_attribution", "scientific_truth",
    ):
        with pytest.raises(PermissionError, match="forbidden"):
            lens.inspect("text", intended_use=use)
    assert detector.calls == []


def test_tau_matches_released_detector_grid():
    assert validate_tau(0.0) == 0.0
    assert validate_tau(0.85) == 0.85
    assert validate_tau(0.95) == 0.95
    with pytest.raises(ValueError, match="0.05"):
        validate_tau(0.83)
    with pytest.raises(ValueError, match="<= 0.95"):
        validate_tau(1.0)


def test_summary_supports_cross_model_output_audits():
    record = DetectorScopeAuditLens(FakeDetector(), detector_id="x").inspect("text")
    summary = summarize_record(record)
    assert summary["p_ai"] == 0.88
    assert summary["feature_count"] == 2
    assert summary["positive_feature_importance_sum"] == 0.23
    assert summary["negative_feature_importance_sum"] == -0.05
    assert summary["top_positive_feature"] == "repeated phrases or sequences in text"
    assert summary["top_negative_feature"] == "conversational filler phrase"
    assert "p_ai" in comparison_dimensions()


def test_invalid_detector_outputs_are_rejected():
    class BadDetector:
        def __call__(self, *args, **kwargs):
            return SimpleNamespace(
                label="ai", p_ai=1.5, logit=0.0, bias=0.0, features=[]
            )
    with pytest.raises(ValueError, match="between 0 and 1"):
        DetectorScopeAuditLens(BadDetector(), detector_id="x").inspect("text")


def test_detector_and_input_must_be_bounded():
    with pytest.raises(TypeError, match="callable"):
        DetectorScopeAuditLens(object(), detector_id="x")
    lens = DetectorScopeAuditLens(FakeDetector(), detector_id="x")
    with pytest.raises(ValueError, match="too large"):
        lens.inspect("x" * 200_001)

import json
import pytest

from frontierlab.muse2_edge import (
    ALLOWED_TASKS,
    Muse2EdgeWorker,
    validate_output,
)


class FakeRuntime:
    def __init__(self, output=None):
        self.output = output or {"title": "Paper", "doi": "10.1000/x"}
        self.calls = []

    def complete(self, **kwargs):
        self.calls.append(kwargs)
        return json.dumps(self.output)


def test_metadata_normalization_returns_strict_json_and_receipt():
    runtime = FakeRuntime()
    worker = Muse2EdgeWorker(runtime)
    out, receipt = worker.extract(
        raw_text="Title: Paper\nDOI: 10.1000/x",
        schema={"title": "string", "doi": "string"},
        task="metadata_normalization",
    )
    assert out == {"title": "Paper", "doi": "10.1000/x"}
    assert receipt.model == "Muse-research/Muse2-230M"
    assert receipt.scientific_entailment_verified is False
    assert receipt.researcher_review_required_for_scientific_use is True
    assert len(receipt.input_sha256) == 64
    assert len(worker.receipts) == 1
    call = runtime.calls[0]
    assert call["temperature"] == 0.2
    assert call["top_k"] == 50
    assert call["max_new_tokens"] == 256


def test_only_low_risk_preprocessing_tasks_are_allowed():
    assert {"metadata_normalization", "log_to_json", "schema_formatting", "routing"} == ALLOWED_TASKS
    worker = Muse2EdgeWorker(FakeRuntime())
    with pytest.raises(PermissionError, match="outside"):
        worker.extract(
            raw_text="claim",
            schema={"label": "string"},
            task="scientific_entailment",
        )


@pytest.mark.parametrize("field", [
    "supported", "contradicted", "entailment", "truth", "diagnosis",
    "treatment", "efficacy", "safety", "medical_advice", "clinical_decision",
])
def test_scientific_or_medical_truth_fields_are_forbidden(field):
    worker = Muse2EdgeWorker(FakeRuntime())
    with pytest.raises(PermissionError, match="truth-decision"):
        worker.extract(
            raw_text="some scientific text",
            schema={field: "boolean"},
            task="schema_formatting",
        )


def test_output_fields_and_types_must_match_exactly():
    with pytest.raises(ValueError, match="exactly match"):
        validate_output({"title": "x", "extra": "y"}, {"title": "string"})
    with pytest.raises(ValueError, match="declared type"):
        validate_output({"count": "2"}, {"count": "integer"})


def test_invalid_json_is_rejected_without_becoming_evidence():
    class BadRuntime:
        def complete(self, **kwargs):
            return "not json"
    worker = Muse2EdgeWorker(BadRuntime())
    with pytest.raises(ValueError, match="not valid JSON"):
        worker.extract(
            raw_text="x",
            schema={"value": "string"},
            task="log_to_json",
        )


def test_runtime_must_be_injected_and_input_is_bounded():
    with pytest.raises(TypeError, match="complete"):
        Muse2EdgeWorker(object())
    worker = Muse2EdgeWorker(FakeRuntime({"value": "x"}))
    with pytest.raises(ValueError, match="too large"):
        worker.extract(
            raw_text="x" * 200_001,
            schema={"value": "string"},
            task="schema_formatting",
        )

"""Real texts + synthetic predictions: software behavior, not measured model accuracy."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import pytest
from frontierlab.literature_pilot import (
    dataset_id, evaluate_imported, load_dataset, predictions_template,
    public_cases, reviewer_packet,
)


def predictions(data):
    packet = predictions_template(data)
    packet["model_id"] = "HAND_AUTHORED_TEST_OUTPUT_NOT_A_MODEL"
    texts = {s["source_id"]: s["source_text"] for s in data["sources"]}
    for row in packet["cases"]:
        row.update(label="SUPPORTED", evidence_quote=texts[row["source_id"]])
    return packet


def completed_review(data):
    packet = reviewer_packet(data)
    packet["annotation_origin"] = "RESEARCHER_SUPPLIED"
    # Test fixture only: these are not actual human judgments.
    for row in packet["cases"]:
        row.update(label="CONTRADICTED", rationale="Artificial reviewer fixture for a software test.")
    return packet


def test_dataset_contains_four_real_sources_and_twelve_provisional_cases():
    data = load_dataset()
    assert len(data["sources"]) == 4 and len(data["cases"]) == 12
    assert Counter(c["draft_reference_label"] for c in data["cases"]) == {
        "SUPPORTED": 4, "CONTRADICTED": 4, "INSUFFICIENT": 4}
    assert all(s["source_id"].startswith("PMC") and s["doi"] for s in data["sources"])
    assert all(len(s["source_text"].split()) <= 25 for s in data["sources"])
    assert all(c["reference_origin"] == "AI_AUTHORED_PROVISIONAL_NOT_HUMAN_GOLD" for c in data["cases"])


def test_blind_packets_exclude_draft_labels_and_rationales():
    data = load_dataset()
    for packet in (public_cases(data), reviewer_packet(data), predictions_template(data)):
        text = json.dumps(packet)
        assert "draft_reference_label" not in text and "draft_rationale" not in text
    packet = reviewer_packet(data)
    assert all(c["label"] == "PENDING" for c in packet["cases"])
    assert packet["independence_verified"] is False


def test_provisional_labels_never_produce_accuracy_metrics():
    data = load_dataset()
    result = evaluate_imported(data, predictions(data))
    assert result["metrics"] is None and result["reviewed"] == 0
    assert result["status"] == "AWAITING_RESEARCHER_ANNOTATION"
    assert result["quote_anchor_count"] == 12
    assert result["real_model_execution_verified"] is False


def test_valid_quote_does_not_fix_a_wrong_semantic_label():
    data = load_dataset()
    result = evaluate_imported(data, predictions(data), completed_review(data))
    assert result["metrics"]["raw_label_agreement_with_supplied_review"] == 0
    assert result["metrics"]["gate_label_agreement_with_supplied_review"] == 0
    assert result["metrics"]["reviewer_corrections_to_gate"] == 12
    assert not result["independent_reference_labels_verified"]


@pytest.mark.parametrize("fault", ["wrong_source", "wrong_quote"])
def test_citation_or_quote_mismatch_abstains_without_overwriting_raw_prediction(fault):
    data = load_dataset()
    packet = predictions(data)
    if fault == "wrong_source":
        packet["cases"][0]["source_id"] = data["sources"][1]["source_id"]
    else:
        packet["cases"][0]["evidence_quote"] = "This text is fabricated and does not occur in the source."
    result = evaluate_imported(data, packet)
    assert result["cases"][0]["raw_label"] == "SUPPORTED"
    assert result["cases"][0]["gate_label"] == "INSUFFICIENT"
    assert result["gate_abstentions"] == 1


def test_changed_excerpt_snapshot_rejects_old_predictions():
    data = load_dataset()
    packet = predictions(data)
    changed = deepcopy(data)
    changed["sources"][0]["source_text"] += " A revision."
    with pytest.raises(ValueError, match="snapshot"):
        evaluate_imported(changed, packet)


def test_draft_label_changes_cannot_change_model_input_or_human_reference_context():
    data = load_dataset()
    changed = deepcopy(data)
    changed["cases"][0]["draft_reference_label"] = "INSUFFICIENT"
    assert dataset_id(changed) == dataset_id(data)
    assert public_cases(changed) == public_cases(data)


@pytest.mark.parametrize("fault", ["missing", "duplicate", "unknown"])
def test_predictions_must_cover_each_case_once(fault):
    data = load_dataset()
    packet = predictions(data)
    if fault == "missing":
        packet["cases"].pop()
    elif fault == "duplicate":
        packet["cases"][-1] = deepcopy(packet["cases"][0])
    else:
        packet["cases"][-1]["case_id"] = "R-UNKNOWN"
    with pytest.raises(ValueError, match="exactly once"):
        evaluate_imported(data, packet)


def test_partial_or_undeclared_review_cannot_enable_summary_agreement():
    data = load_dataset()
    review = completed_review(data)
    review["cases"][0].update(label="PENDING", rationale="")
    assert evaluate_imported(data, predictions(data), review)["metrics"] is None
    review = completed_review(data)
    review["annotation_origin"] = "AI_AUTHORED_PROVISIONAL"
    assert evaluate_imported(data, predictions(data), review)["metrics"] is None


def test_review_needs_explicit_reason_for_every_annotated_case():
    data = load_dataset()
    review = completed_review(data)
    review["cases"][0]["rationale"] = ""
    with pytest.raises(ValueError, match="rationale"):
        evaluate_imported(data, predictions(data), review)


def test_corrupted_source_snapshot_is_not_loaded(tmp_path):
    data = load_dataset()
    data["sources"][0]["source_text"] = "A replaced excerpt."
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="hash mismatch"):
        load_dataset(path)


def test_unfinished_prediction_template_is_not_scored():
    data = load_dataset()
    with pytest.raises(ValueError, match="Complete model"):
        evaluate_imported(data, predictions_template(data))


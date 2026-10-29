import copy
import json

import pytest

from frontierlab.literature_pilot import load_dataset, reviewer_packet
from frontierlab.pilot_review import canonicalize_review_upload, labels_from_review_packet
from frontierlab.recorded_gate_ablation import run_recorded_pilot


def _edited_packet(labels: dict[str, str]):
    data = load_dataset()
    packet = reviewer_packet(data)
    for row in packet["cases"]:
        if row["case_id"] in labels:
            row["label"] = labels[row["case_id"]]
            row["rationale"] = "Reviewed against the supplied short excerpt only."
    return data, packet


def test_partial_review_is_canonicalized_and_source_bound():
    data, packet = _edited_packet({"R01": "SUPPORTED", "R02": "CONTRADICTED"})
    result = canonicalize_review_upload(
        data,
        packet,
        reviewer="Jaycee",
        recorded_at_utc="2026-10-29T17:00:00+00:00",
    )
    assert result["status"] == "PARTIAL_RESEARCHER_REVIEW"
    assert result["annotation_origin"] == "RESEARCHER_SUPPLIED"
    assert result["independence_verified"] is False
    assert result["reviewer"] == "Jaycee"
    assert result["review_stats"] == {
        "total": 12,
        "reviewed": 2,
        "pending": 10,
        "coverage": pytest.approx(2 / 12, abs=1e-4),
    }
    assert labels_from_review_packet(data, result) == {
        "R01": "SUPPORTED",
        "R02": "CONTRADICTED",
    }


def test_review_rejects_tampered_source_or_claim_binding():
    data, packet = _edited_packet({"R01": "SUPPORTED"})
    forged = copy.deepcopy(packet)
    forged["cases"][0]["claim"] = "A different claim"
    with pytest.raises(ValueError, match="case/source binding changed"):
        canonicalize_review_upload(data, forged, reviewer="Jaycee")

    forged = copy.deepcopy(packet)
    forged["sources"][0]["source_text"] = "tampered source"
    with pytest.raises(ValueError, match="source snapshot changed"):
        canonicalize_review_upload(data, forged, reviewer="Jaycee")


def test_review_requires_reviewer_and_rationale_for_completed_judgments():
    data, packet = _edited_packet({"R01": "SUPPORTED"})
    with pytest.raises(ValueError, match="Reviewer name required"):
        canonicalize_review_upload(data, packet, reviewer="")

    packet["cases"][0]["rationale"] = "short"
    with pytest.raises(ValueError, match="at least eight"):
        canonicalize_review_upload(data, packet, reviewer="Jaycee")


def test_complete_researcher_review_can_finish_arm_c_but_not_create_accuracy():
    data, packet = _edited_packet({
        row["case_id"]: "INSUFFICIENT" for row in load_dataset()["cases"]
    })
    canonical = canonicalize_review_upload(
        data,
        packet,
        reviewer="Jaycee",
        recorded_at_utc="2026-10-29T17:00:00+00:00",
    )
    assert canonical["status"] == "COMPLETE_RESEARCHER_REVIEW"
    labels = labels_from_review_packet(data, canonical)
    assert len(labels) == 12

    ablation = run_recorded_pilot(review_labels=labels)
    arm_c = ablation["arm_c_source_quote_plus_human_review"]
    assert arm_c["reviews_required"] == 8
    assert arm_c["reviews_completed"] == 8
    assert arm_c["pending_review"] == 0
    assert arm_c["review_corrections_to_surviving_decisions"] == 8
    assert ablation["accuracy_reportable"] is False
    assert ablation["scientific_accuracy_measured"] is False


def test_canonical_review_round_trips_as_json():
    data, packet = _edited_packet({"R01": "SUPPORTED"})
    canonical = canonicalize_review_upload(
        data,
        packet,
        reviewer="Jaycee",
        recorded_at_utc="2026-10-29T17:00:00+00:00",
    )
    restored = json.loads(json.dumps(canonical, ensure_ascii=False))
    assert labels_from_review_packet(data, restored) == {"R01": "SUPPORTED"}

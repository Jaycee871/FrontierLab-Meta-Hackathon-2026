import json
from pathlib import Path

import pytest

from scripts import nim_research_continue_trial as trial


class FakeContinuationClient:
    backend = "nvidia-nim"
    model = "meta/muse-glimmer-30b"

    def __init__(self):
        self.roles = []
        self.provenance = {
            "provider": self.backend,
            "model": self.model,
            "process_call_limit": 2,
            "attempted_calls": 0,
            "receipts": [],
            "scientific_outputs_independently_verified": False,
        }

    def json(self, role, task, payload):
        self.roles.append(role)
        self.provenance["attempted_calls"] += 1
        if role == "Adversarial Skeptic Agent":
            return {
                "explanation": "Both excerpts support narrow study-specific observations, not generalization.",
                "uncertainties": [
                    "Only abstract excerpts are available.",
                    "The studies use different antibody formats and engineering strategies.",
                ],
                "recommended_checks": [
                    "Inspect full methods and assay conditions before comparing mechanisms."
                ],
            }
        if role == "Hypothesis Agent":
            return {
                "hypotheses": [{
                    "text": "pH-dependent binding can arise through more than one engineering mechanism, but transfer across antibody formats requires direct testing.",
                    "evidence_ids": ["PMC4314675", "PMC6927761"],
                    "rationale": "The reviewed excerpts establish two study-specific outcomes while leaving generalization unresolved.",
                }]
            }
        raise AssertionError("unexpected role: " + role)


def test_recorded_review_rehydrates_and_stops_at_method_boundary():
    run = trial.load_recorded_context()
    assert run.review["status"] == "READY_FOR_HUMAN_GATED_SYNTHESIS"
    assert run.review["review_stats"]["supported_distinct_sources"] == 2
    assert run.hypotheses == []
    assert run.evaluation is None and run.plan is None

    client = FakeContinuationClient()
    out = trial.continue_recorded_context(client)

    assert client.roles == ["Adversarial Skeptic Agent", "Hypothesis Agent"]
    assert client.provenance["attempted_calls"] == 2
    assert len(out.hypotheses) == 1
    assert out.skeptic["decision"] == "HUMAN_REVIEWED_DRAFT"
    assert out.evaluation is None and out.plan is None


def test_tampered_completed_review_is_rejected(tmp_path):
    completed = json.loads(trial.DEFAULT_REVIEW.read_text(encoding="utf-8"))
    completed["dataset_id"] = "tampered"
    path = tmp_path / "review.json"
    path.write_text(json.dumps(completed), encoding="utf-8")

    with pytest.raises(ValueError, match="not bound"):
        trial.load_recorded_context(review_path=path)


def test_pending_label_in_completed_review_is_rejected(tmp_path):
    completed = json.loads(trial.DEFAULT_REVIEW.read_text(encoding="utf-8"))
    completed["cases"][0]["review_label"] = "PENDING"
    path = tmp_path / "review.json"
    path.write_text(json.dumps(completed), encoding="utf-8")

    with pytest.raises(ValueError, match="pending"):
        trial.load_recorded_context(review_path=path)

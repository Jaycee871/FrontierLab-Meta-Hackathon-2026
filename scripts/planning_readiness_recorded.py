"""Build the recorded M2 Stage-5 readiness packet with zero model calls."""
from __future__ import annotations

import json
from pathlib import Path

from frontierlab.planning_readiness import build_planning_readiness
from scripts.nim_research_continue_trial import _rehydrate_run

ROOT = Path(__file__).resolve().parents[1]
EXTRACTION = ROOT / "docs" / "runs" / "nim_research_extraction_20261028.json"
REVIEW = ROOT / "docs" / "runs" / "nim_claim_review_completed_20261028.json"
CONTINUATION = ROOT / "docs" / "runs" / "nim_reviewed_continuation_20261028.json"
EVALUATION = ROOT / "docs" / "runs" / "method_evaluation_20261028.json"
SELECTION = ROOT / "docs" / "runs" / "researcher_method_selection_20261028.json"


def load_recorded_m2_run():
    extraction = json.loads(EXTRACTION.read_text(encoding="utf-8"))
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    continuation = json.loads(CONTINUATION.read_text(encoding="utf-8"))
    evaluation = json.loads(EVALUATION.read_text(encoding="utf-8"))
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))

    run = _rehydrate_run(extraction["receipt"]["run"])
    run.review = review
    run.hypotheses = continuation["hypotheses"]
    run.evaluation = evaluation
    run.plan = None

    if selection.get("evaluation_id") != evaluation.get("evaluation_id"):
        raise ValueError("Researcher selection is not bound to this evaluation")
    if selection.get("selected_candidate_id") != evaluation.get("selected_candidate_id"):
        raise ValueError("Researcher selection and canonical evaluation disagree")
    if selection.get("planning_approved") is not False:
        raise PermissionError("Recorded selection unexpectedly authorizes planning")
    return run, selection


def run() -> dict:
    recorded_run, selection = load_recorded_m2_run()
    packet = build_planning_readiness(recorded_run)
    packet["researcher_selection_provenance"] = {
        "schema": selection["schema"],
        "reviewer": selection["reviewer"],
        "decision": selection["decision"],
        "selected_candidate_id": selection["selected_candidate_id"],
        "recorded_date_taipei": selection["recorded_date_taipei"],
        "planning_approved": selection["planning_approved"],
        "downstream_validation_requirement": selection["downstream_validation_requirement"],
    }
    packet["source_artifacts"] = [
        "docs/runs/nim_research_extraction_20261028.json",
        "docs/runs/nim_claim_review_completed_20261028.json",
        "docs/runs/nim_reviewed_continuation_20261028.json",
        "docs/runs/method_evaluation_20261028.json",
        "docs/runs/researcher_method_selection_20261028.json",
    ]
    return packet


def main() -> None:
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

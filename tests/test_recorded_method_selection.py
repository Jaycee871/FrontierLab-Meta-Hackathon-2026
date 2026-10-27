import json
from pathlib import Path

from frontierlab.evaluation import require_evaluation, selected_method
from scripts.nim_research_continue_trial import _rehydrate_run

ROOT = Path(__file__).resolve().parents[1]


def load_selected_run():
    extraction = json.loads(
        (ROOT / "docs/runs/nim_research_extraction_20261028.json").read_text(encoding="utf-8")
    )
    review = json.loads(
        (ROOT / "docs/runs/nim_claim_review_completed_20261028.json").read_text(encoding="utf-8")
    )
    continuation = json.loads(
        (ROOT / "docs/runs/nim_reviewed_continuation_20261028.json").read_text(encoding="utf-8")
    )
    evaluation = json.loads(
        (ROOT / "docs/runs/method_evaluation_20261028.json").read_text(encoding="utf-8")
    )

    run = _rehydrate_run(extraction["receipt"]["run"])
    run.review = review
    run.hypotheses = continuation["hypotheses"]
    run.evaluation = evaluation
    run.plan = None
    return run


def test_recorded_m2_evaluation_is_current_and_planning_eligible():
    run = load_selected_run()
    evaluation = require_evaluation(run)

    assert evaluation["status"] == "READY_FOR_DRAFT_PLANNING"
    assert evaluation["selected_candidate_id"] == "M2"
    assert evaluation["context_id"] == "ee7f790ba48474bb63a935f6108f1e698121a404d93a5bf0389946ba2932dcf8"
    assert evaluation["evaluation_id"] == "00c440f3a78a95a1703725ea261b992ab51551d1dedd9cf41ba481dd0954f231"

    selected = selected_method(evaluation)
    assert selected["candidate_id"] == "M2"
    assert selected["evidence_ids"] == ["PMC6927761"]
    assert selected["reproducibility_status"] == "INCOMPLETE_DOCUMENTATION"
    assert {item["item"] for item in selected["open_checks"]} == {"data", "code", "environment"}
    assert run.plan is None


def test_researcher_selection_provenance_stays_separate_from_canonical_evaluation():
    evaluation = json.loads(
        (ROOT / "docs/runs/method_evaluation_20261028.json").read_text(encoding="utf-8")
    )
    provenance = json.loads(
        (ROOT / "docs/runs/researcher_method_selection_20261028.json").read_text(encoding="utf-8")
    )

    assert "researcher_decision" not in evaluation
    assert provenance["decision"] == "SELECT_M2"
    assert provenance["selected_candidate_id"] == evaluation["selected_candidate_id"]
    assert provenance["evaluation_id"] == evaluation["evaluation_id"]
    assert provenance["planning_approved"] is False

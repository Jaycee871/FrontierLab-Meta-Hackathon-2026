from copy import deepcopy

import pytest

from frontierlab.planning_readiness import build_planning_readiness, readiness_summary
from scripts.planning_readiness_recorded import load_recorded_m2_run, run as recorded_packet


def test_recorded_m2_is_ready_for_explicit_approval_but_not_authorized():
    packet = recorded_packet()
    assert packet["status"] == "READY_FOR_EXPLICIT_PLANNING_APPROVAL"
    assert packet["planning_approved"] is False
    assert packet["model_call_authorized"] is False
    assert packet["planning_model_called"] is False
    assert packet["plan_generated"] is False
    assert packet["selected_candidate_id"] == "M2"
    assert packet["evaluation_id"] == (
        "00c440f3a78a95a1703725ea261b992ab51551d1dedd9cf41ba481dd0954f231"
    )
    assert packet["context_id"] == (
        "ee7f790ba48474bb63a935f6108f1e698121a404d93a5bf0389946ba2932dcf8"
    )


def test_recorded_m2_open_checks_and_evidence_sets_are_exact():
    packet = recorded_packet()
    assert {item["item"] for item in packet["open_reproducibility_checks"]} == {
        "data", "code", "environment"
    }
    assert set(packet["documented_reproducibility_checks"]) == {
        "parameters", "protocol", "metrics"
    }
    assert packet["required_method_evidence_ids"] == ["PMC6927761"]
    assert packet["permitted_reviewed_evidence_ids"] == ["PMC4314675", "PMC6927761"]
    assert {item for h in packet["hypotheses"] for item in h["evidence_ids"]} == {
        "PMC4314675", "PMC6927761"
    }


def test_readiness_preserves_spr_avidity_and_search_bias_requirements():
    packet = recorded_packet()
    obligations = {item["obligation_id"]: item for item in packet["planning_obligations"]}
    assert "SPR on monomeric Fab" in obligations["orthogonal-spr"]["requirement"]
    assert "avidity" in obligations["avidity-stoichiometry-caveat"]["requirement"]
    assert "histidine-centered" in obligations["structure-and-search-bias"]["requirement"]
    assert "M1 remains a comparator" in obligations["structure-and-search-bias"]["requirement"]
    assert obligations["replication-and-falsification"]["required"] is True


def test_readiness_summary_is_small_and_explicit():
    summary = readiness_summary(recorded_packet())
    assert summary == {
        "status": "READY_FOR_EXPLICIT_PLANNING_APPROVAL",
        "selected_candidate_id": "M2",
        "open_reproducibility_checks": ["data", "code", "environment"],
        "required_obligations": 9,
        "planning_approved": False,
        "model_call_authorized": False,
    }


def test_readiness_rejects_stale_evaluation():
    run, _ = load_recorded_m2_run()
    stale = deepcopy(run.evaluation)
    stale["rationale"] = stale["rationale"] + " changed"
    run.evaluation = stale
    with pytest.raises(PermissionError, match="stale or changed"):
        build_planning_readiness(run)


def test_readiness_rejects_existing_plan():
    run, _ = load_recorded_m2_run()
    run.plan = {"status": "DRAFT_FOR_RESEARCHER_REVIEW"}
    with pytest.raises(PermissionError, match="no generated plan"):
        build_planning_readiness(run)


def test_readiness_packet_never_claims_scientific_execution():
    packet = recorded_packet()
    assert packet["scientific_execution_verified"] is False
    assert packet["scientific_accuracy_verified"] is False
    assert packet["researcher_selection_provenance"]["planning_approved"] is False
    assert packet["researcher_selection_provenance"]["downstream_validation_requirement"].startswith(
        "Where feasible"
    )

from frontierlab.interventions import record_human_event
from frontierlab.models import Audit, Run


def _run():
    return Run(
        question="q",
        mode="live",
        model="m",
        papers=[],
        audit=Audit(),
        hypotheses=[],
        skeptic={},
        log=[],
    )


def test_human_event_is_timestamped_and_bound_to_artifact():
    run = _run()
    event = record_human_event(
        run,
        "METHOD_EVALUATION_SAVED",
        "eval-123",
        actor_label="Jaycee",
        note="Compared two methods.",
        metadata={"selected": "M2"},
    )
    assert event["schema"] == "frontierlab.human-intervention.v1"
    assert event["artifact_id"] == "eval-123"
    assert event["kind"] == "METHOD_EVALUATION_SAVED"
    assert event["severity"] == "decision"
    assert event["actor_label"] == "Jaycee"
    assert event["identity_verified"] is False
    assert event["time_utc"].endswith("+00:00")
    assert len(event["event_id"]) == 20
    assert run.human_events == [event]


def test_event_ids_change_for_repeated_actions():
    run = _run()
    a = record_human_event(run, "PLANNING_APPROVED", "eval-1")
    b = record_human_event(run, "PLANNING_APPROVED", "eval-1")
    assert a["event_id"] != b["event_id"]
    assert len(run.human_events) == 2


def test_event_contract_rejects_unknown_kind_or_artifact():
    run = _run()
    try:
        record_human_event(run, "OTHER", "x")
        raise AssertionError("expected error")
    except ValueError:
        pass
    try:
        record_human_event(run, "CLAIM_REVIEW_SAVED", "")
        raise AssertionError("expected error")
    except ValueError:
        pass

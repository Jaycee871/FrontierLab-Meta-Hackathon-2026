import json

from frontierlab.models import Audit, Run
from frontierlab.trajectory_graph import build_trajectory_graph, summarize, to_json


def _run(**updates):
    base = dict(
        question="Does M2 improve pH-selective binding?",
        mode="live",
        model="meta/muse-glimmer-30b",
        papers=[],
        audit=Audit(),
        hypotheses=[],
        skeptic={},
        log=[],
        backend="nvidia-nim",
        inference={"attempted_calls": 0, "receipts": []},
    )
    base.update(updates)
    return Run(**base)


def _node(graph, prefix):
    return next(node for node in graph["nodes"] if node["id"].startswith(prefix))


def test_trajectory_graph_has_fixed_five_stage_spine():
    graph = build_trajectory_graph(_run())
    stages = [node for node in graph["nodes"] if node["type"] == "stage"]
    assert len(stages) == 5
    assert {node["stage"] for node in stages} == {
        "research", "evidence", "hypothesis", "evaluation", "planning"
    }
    assert sum(edge["relation"] == "NEXT_STAGE" for edge in graph["edges"]) == 4


def test_model_receipts_are_audit_nodes_without_raw_prompt_or_output():
    run = _run(
        inference={
            "attempted_calls": 1,
            "receipts": [{
                "role": "Hypothesis Agent",
                "status": "JSON_OBJECT_RETURNED",
                "requested_model": "meta/muse-glimmer-30b",
                "reported_model": "meta/muse-glimmer-30b",
                "started_at_utc": "2026-10-29T12:00:00+00:00",
                "input_sha256": "a" * 64,
                "output_sha256": "b" * 64,
                "finish_reason": "stop",
                "usage": {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18},
                "elapsed_seconds": 1.25,
                "content": "MUST NOT APPEAR",
                "prompt": "MUST NOT APPEAR",
            }],
        }
    )
    graph = build_trajectory_graph(run)
    call = _node(graph, "model_call:")
    assert call["role"] == "Hypothesis Agent"
    assert call["usage"]["total_tokens"] == 18
    assert "content" not in call and "prompt" not in call
    assert any(
        edge["source"] == call["id"] and edge["target"] == "stage:hypothesis"
        and edge["relation"] == "EXECUTED_IN"
        for edge in graph["edges"]
    )


def test_human_events_and_method_evaluation_become_first_class_nodes():
    run = _run(
        human_events=[{
            "schema": "frontierlab.human-intervention.v1",
            "event_id": "evt1",
            "time_utc": "2026-10-29T12:00:00+00:00",
            "kind": "METHOD_EVALUATION_SAVED",
            "severity": "decision",
            "artifact_id": "E1",
            "actor_label": "Jaycee",
            "identity_verified": False,
        }],
        evaluation={
            "evaluation_id": "E1",
            "status": "READY_FOR_DRAFT_PLANNING",
            "selected_candidate_id": "M2",
            "origin": "RESEARCHER_ASSESSED",
        },
    )
    graph = build_trajectory_graph(run)
    human = _node(graph, "human_event:")
    evaluation = _node(graph, "method_evaluation:")
    assert human["kind"] == "METHOD_EVALUATION_SAVED"
    assert human["identity_verified"] is False
    assert evaluation["selected_candidate_id"] == "M2"
    assert any(edge["target"] == "stage:evaluation" for edge in graph["edges"])


def test_rejected_claims_and_taxonomy_signals_are_visible():
    audit = Audit(
        rejected_claims=[{
            "reason": "Unknown source citation",
            "claim": {"paper_id": "PMC404", "claim_key": "x"},
        }],
        conflicts=[{"claim_key": "pH-effect"}],
    )
    run = _run(
        audit=audit,
        log=[{"role": "Human Claim Review", "status": "BLOCKED", "note": "review pending"}],
    )
    graph = build_trajectory_graph(run)
    assert summarize(graph)["rejected_claims"] == 1
    assert summarize(graph)["process_signals"] >= 3
    rejected = _node(graph, "rejected_claim:")
    assert rejected["paper_id"] == "PMC404"


def test_summary_and_json_are_deterministic_for_same_run():
    run = _run()
    graph1 = build_trajectory_graph(run)
    graph2 = build_trajectory_graph(run)
    assert graph1 == graph2
    assert json.loads(to_json(graph1)) == graph1
    summary = summarize(graph1)
    assert summary["nodes_by_type"]["stage"] == 5
    assert summary["model_calls"] == 0


def test_trajectory_graph_is_explicitly_outside_scientific_gate():
    graph = build_trajectory_graph(_run())
    assert "does not participate in scientific evidence gating" in graph["note"]
    assert graph["schema"] == "frontierlab.trajectory-graph.v1"

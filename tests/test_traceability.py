from frontierlab.evidence_graph import build_evidence_graph
from frontierlab.operating_status import research_operating_status
from frontierlab.traceability import source_audit_summary, trace_coverage, trace_one
from tests.test_evidence_graph import claim, live_run, planned_run, QUOTE_A, QUOTE_B


def test_full_extracted_graph_has_full_measured_trace_coverage():
    run = planned_run(
        [claim("PMC1", QUOTE_A), claim("PMC2", QUOTE_B)],
        ["PMC1", "PMC2"],
        ["PMC1", "PMC2"],
    )
    graph = build_evidence_graph(run)
    result = trace_coverage(graph)
    assert result["material_artifacts"] == 5  # 2 claims + 1 hypothesis + 2 plan steps
    assert result["source_trace_coverage"] == 1.0
    assert result["strict_extracted_coverage"] == 1.0
    assert result["scientific_accuracy_measured"] is False
    assert result["semantic_entailment_verified"] is False


def test_inferred_path_can_be_source_traceable_without_being_strict_extracted():
    run = planned_run(
        [
            claim("PMC1", QUOTE_A),
            claim("PMC2", "invented quotation long enough to fail anchoring"),
        ],
        ["PMC1", "PMC2"],
        ["PMC1", "PMC2"],
    )
    graph = build_evidence_graph(run)
    result = trace_coverage(graph)
    assert result["source_trace_coverage"] == 1.0
    assert result["strict_extracted_coverage"] < 1.0
    assert any(
        item["source_traceable"] and not item["strict_extracted"]
        for item in result["artifacts"]
    )


def test_rejected_claims_are_reported_but_excluded_from_headline_denominator():
    run = live_run([
        claim("PMC1", QUOTE_A),
        claim("PMC2", "invented quotation long enough to fail anchoring"),
    ])
    graph = build_evidence_graph(run)
    result = trace_coverage(graph)
    assert result["material_artifacts"] == 1
    assert result["excluded_rejected_claims"] == 1
    assert result["source_trace_coverage"] == 1.0


def test_trace_one_rejects_non_material_nodes_and_unknown_ids():
    run = live_run([claim("PMC1", QUOTE_A)])
    graph = build_evidence_graph(run)
    paper_id = next(n["id"] for n in graph["nodes"] if n["type"] == "paper")
    try:
        trace_one(graph, paper_id)
        assert False
    except ValueError as exc:
        assert "claim/hypothesis/plan_step" in str(exc)

    try:
        trace_one(graph, "claim:missing")
        assert False
    except ValueError as exc:
        assert "Unknown artifact" in str(exc)


def test_source_audit_counts_anchored_and_rejected_claims():
    run = live_run([
        claim("PMC1", QUOTE_A),
        claim("PMC2", "invented quotation long enough to fail anchoring"),
    ])
    graph = build_evidence_graph(run)
    audit = source_audit_summary(graph)
    assert audit["papers"] == 2
    assert audit["passed_claims"] == 1
    assert audit["anchored_passed_claims"] == 1
    assert audit["rejected_claims_attached"] == 1
    assert audit["source_audit_is_semantic_entailment"] is False


def test_operating_status_exposes_process_not_chain_of_thought():
    run = planned_run(
        [claim("PMC1", QUOTE_A), claim("PMC2", QUOTE_B)],
        ["PMC1", "PMC2"],
        ["PMC1", "PMC2"],
    )
    status = research_operating_status(run)
    assert status["schema"] == "frontierlab.research-operating-status.v1"
    assert status["traceability"]["source_trace_coverage"] == 1.0
    assert status["traceability"]["strict_extracted_coverage"] == 1.0
    assert status["maintainability"]["automatic_repair_enabled"] is False
    assert status["governance"]["plan_generated"] is True
    assert status["scientific_accuracy_measured"] is False
    assert "chain-of-thought" in status["note"]


def test_recorded_m2_core_has_measured_trace_coverage():
    from scripts.trace_coverage_recorded import run as recorded_trace
    result = recorded_trace()
    trace = result["trace_coverage"]
    assert result["new_model_calls"] == 0
    assert result["selected_candidate_id"] == "M2"
    assert result["planning_approved"] is False
    assert trace["material_artifacts"] == 4  # 2 reviewed claims + 2 hypotheses
    assert trace["source_traceable_artifacts"] == 4
    assert trace["strict_extracted_artifacts"] == 4
    assert trace["source_trace_coverage"] == 1.0
    assert trace["strict_extracted_coverage"] == 1.0
    assert result["scientific_accuracy_measured"] is False
    assert result["semantic_entailment_verified"] is False


def test_complete_provenance_export_includes_operating_status():
    import json
    from frontierlab.reporting import export_json
    from tests.test_evidence_graph import planned_run, claim, QUOTE_A, QUOTE_B
    run = planned_run(
        [claim("PMC1", QUOTE_A), claim("PMC2", QUOTE_B)],
        ["PMC1", "PMC2"],
        ["PMC1", "PMC2"],
    )
    payload = json.loads(export_json(run))
    assert payload["research_operating_status"]["schema"] == "frontierlab.research-operating-status.v1"
    assert payload["research_operating_status"]["traceability"]["source_trace_coverage"] == 1.0

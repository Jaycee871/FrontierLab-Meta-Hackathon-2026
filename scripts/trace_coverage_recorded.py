"""Rebuild measured trace coverage for the recorded reviewed M2 core.

Zero model calls. This reuses the recorded extraction/review/hypothesis/evaluation
artifacts and measures provenance coverage only.
"""
from __future__ import annotations

import json

from frontierlab.evidence_graph import build_evidence_graph
from frontierlab.traceability import source_audit_summary, trace_coverage
from scripts.planning_readiness_recorded import load_recorded_m2_run


def run() -> dict:
    recorded_run, selection = load_recorded_m2_run()
    recorded_run.plan = None
    graph = build_evidence_graph(recorded_run)
    trace = trace_coverage(graph)
    source_audit = source_audit_summary(graph)
    return {
        "record_type": "frontierlab_recorded_trace_coverage",
        "selected_candidate_id": selection["selected_candidate_id"],
        "planning_approved": selection["planning_approved"],
        "new_model_calls": 0,
        "trace_coverage": trace,
        "source_audit": source_audit,
        "scientific_accuracy_measured": False,
        "semantic_entailment_verified": False,
        "note": (
            "Measured on the recorded reviewed M2 core. Coverage means provenance "
            "reachability/completeness, not scientific correctness."
        ),
    }


def main() -> None:
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

"""Zero-model-call replay of the recorded, researcher-reviewed real M2 core run.

This module is the single loader used by the Streamlit replay panel and by the
recorded scripts (``scripts/trace_coverage_recorded.py`` and
``scripts/planning_readiness_recorded.py``). It only reads the frozen JSON
artifacts in ``docs/runs/`` (recorded on 2026-10-28, Asia/Taipei) and recomputes
traceability, operating status, planning readiness, the evidence graph and the
trajectory graph with the same code paths used for live runs. It never creates a
model client and never performs a network request.
"""
from __future__ import annotations

import json
from pathlib import Path

from .evidence_graph import build_evidence_graph, summarize as graph_summary
from .models import Audit, Claim, Paper, Run
from .operating_status import research_operating_status
from .planning_readiness import build_planning_readiness, readiness_summary
from .traceability import source_audit_summary, trace_coverage
from .trajectory_graph import build_trajectory_graph, summarize as trajectory_summary

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "docs" / "runs"
EXTRACTION = RUNS / "nim_research_extraction_20261028.json"
REVIEW = RUNS / "nim_claim_review_completed_20261028.json"
CONTINUATION = RUNS / "nim_reviewed_continuation_20261028.json"
EVALUATION = RUNS / "method_evaluation_20261028.json"
SELECTION = RUNS / "researcher_method_selection_20261028.json"
SOURCE_ARTIFACTS = [
    "docs/runs/nim_research_extraction_20261028.json",
    "docs/runs/nim_claim_review_completed_20261028.json",
    "docs/runs/nim_reviewed_continuation_20261028.json",
    "docs/runs/method_evaluation_20261028.json",
    "docs/runs/researcher_method_selection_20261028.json",
]


def rehydrate_run(raw: dict) -> Run:
    """Rebuild a Run object from a recorded JSON receipt (no model call)."""
    papers = [Paper(**item) for item in raw["papers"]]
    audit_raw = raw["audit"]
    audit = Audit(
        verified_claims=[Claim(**item) for item in audit_raw.get("verified_claims", [])],
        rejected_claims=audit_raw.get("rejected_claims", []),
        conflicts=audit_raw.get("conflicts", []),
        warnings=audit_raw.get("warnings", []),
    )
    return Run(
        question=raw["question"],
        mode=raw["mode"],
        model=raw["model"],
        papers=papers,
        audit=audit,
        hypotheses=raw.get("hypotheses", []),
        skeptic=raw.get("skeptic", {}),
        log=raw.get("log", []),
        plan=raw.get("plan"),
        review=raw.get("review"),
        evaluation=raw.get("evaluation"),
        backend=raw.get("backend", "none"),
        inference=raw.get("inference"),
    )


def _read(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_recorded_m2_run(runs_dir: Path | None = None):
    """Load the reviewed M2 core run and the researcher selection record."""
    base = Path(runs_dir) if runs_dir is not None else RUNS
    extraction = _read(base / EXTRACTION.name)
    review = _read(base / REVIEW.name)
    continuation = _read(base / CONTINUATION.name)
    evaluation = _read(base / EVALUATION.name)
    selection = _read(base / SELECTION.name)

    run = rehydrate_run(extraction["receipt"]["run"])
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


def recorded_model_calls(runs_dir: Path | None = None) -> dict:
    """Count model calls made when the artifacts were RECORDED (not now)."""
    base = Path(runs_dir) if runs_dir is not None else RUNS
    extraction = _read(base / EXTRACTION.name)
    continuation = _read(base / CONTINUATION.name)
    inference = extraction["receipt"]["run"].get("inference") or {}
    extraction_receipts = inference.get("receipts", [])
    continuation_receipts = continuation.get("receipts", [])
    return {
        "recorded_date_taipei": extraction.get("recorded_date_taipei"),
        "provider": inference.get("provider"),
        "model": inference.get("model"),
        "extraction_calls": len(extraction_receipts),
        "continuation_calls": len(continuation_receipts),
        "continuation_roles": [item.get("role") for item in continuation_receipts],
        "total_recorded_calls": len(extraction_receipts) + len(continuation_receipts),
        "extraction_run_url": extraction.get("github_run_url"),
        "continuation_run_url": continuation.get("github_run_url"),
    }


def build_recorded_replay(runs_dir: Path | None = None) -> dict:
    """Recompute every replay panel from the recorded files. Zero model calls."""
    run, selection = load_recorded_m2_run(runs_dir)
    graph = build_evidence_graph(run)
    run.evidence_graph = graph
    trace = trace_coverage(graph)
    readiness = build_planning_readiness(run)
    trajectory = build_trajectory_graph(run)
    return {
        "schema": "frontierlab.recorded-replay.v1",
        "recorded_date_taipei": selection.get("recorded_date_taipei"),
        "new_model_calls": 0,
        "run": run,
        "selection": selection,
        "recorded_calls": recorded_model_calls(runs_dir),
        "operating_status": research_operating_status(run),
        "trace_coverage": trace,
        "source_audit": source_audit_summary(graph),
        "planning_readiness": readiness,
        "readiness_summary": readiness_summary(readiness),
        "evidence_graph": graph,
        "graph_summary": graph_summary(graph),
        "trajectory": trajectory,
        "trajectory_summary": trajectory_summary(trajectory),
        "source_artifacts": list(SOURCE_ARTIFACTS),
        "scientific_accuracy_measured": False,
        "semantic_entailment_verified": False,
    }

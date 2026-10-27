"""Bounded continuation of the recorded real NIM extraction after human review.

This runner rehydrates the frozen two-source extraction and the completed
researcher review packet, then allows exactly two new model calls:
1) Adversarial Skeptic Agent
2) Hypothesis Agent

It intentionally stops before method selection and planning.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path

from frontierlab.models import Audit, Claim, Paper, Run
from frontierlab.pipeline import continue_after_review
from frontierlab.research_backend import CallBudget, NvidiaResearchClient
from frontierlab.review import review_packet

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXTRACTION = ROOT / "docs" / "runs" / "nim_research_extraction_20261028.json"
DEFAULT_REVIEW = ROOT / "docs" / "runs" / "nim_claim_review_completed_20261028.json"


def _rehydrate_run(raw: dict) -> Run:
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


def load_recorded_context(extraction_path=DEFAULT_EXTRACTION, review_path=DEFAULT_REVIEW) -> Run:
    extraction = json.loads(Path(extraction_path).read_text(encoding="utf-8"))
    review = json.loads(Path(review_path).read_text(encoding="utf-8"))
    raw_run = extraction["receipt"]["run"]
    run = _rehydrate_run(raw_run)

    fresh = review_packet(run)
    if review.get("schema") != fresh["schema"]:
        raise ValueError("Completed review schema does not match current review contract")
    if review.get("dataset_id") != fresh["dataset_id"]:
        raise ValueError("Completed review is not bound to this recorded extraction")

    fresh_cases = {item["case_id"]: item for item in fresh["cases"]}
    completed_cases = review.get("cases")
    if not isinstance(completed_cases, list) or len(completed_cases) != len(fresh_cases):
        raise ValueError("Completed review case set does not match recorded extraction")
    for item in completed_cases:
        if not isinstance(item, dict) or item.get("case_id") not in fresh_cases:
            raise ValueError("Completed review contains an unknown case")
        expected = fresh_cases[item["case_id"]]
        for field in ("paper_id", "source_snapshot_sha256", "claim", "evidence_quote"):
            if item.get(field) != expected.get(field):
                raise ValueError("Completed review source binding changed for " + item["case_id"])
        if item.get("review_label") == "PENDING":
            raise ValueError("Completed review still contains pending judgments")

    if review.get("status") != "READY_FOR_HUMAN_GATED_SYNTHESIS":
        raise ValueError("Completed review is not ready for synthesis")
    run.review = review
    run.hypotheses = []
    run.evaluation = None
    run.plan = None
    return run


def continue_recorded_context(model_client) -> Run:
    run = load_recorded_context()
    continue_after_review(run, model_client=model_client)
    if run.evaluation is not None or run.plan is not None:
        raise RuntimeError("Continuation crossed the intended human method-selection boundary")
    return run


def main() -> None:
    if os.getenv("FRONTIERLAB_CONTINUATION_TRIAL") != "YES":
        raise PermissionError("Continuation trial disabled; explicit opt-in required")
    if os.getenv("FRONTIERLAB_NIM_RESEARCH") != "YES":
        raise PermissionError("NVIDIA research backend is not enabled")

    client = NvidiaResearchClient(
        authorized=True,
        budget=CallBudget(limit=2),
    )
    base = {
        "record_type": "nim_research_human_reviewed_continuation",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_extraction": str(DEFAULT_EXTRACTION.relative_to(ROOT)),
        "source_review": str(DEFAULT_REVIEW.relative_to(ROOT)),
        "maximum_new_model_calls": 2,
        "automatic_method_selection": False,
        "automatic_planning": False,
        "scientific_accuracy": None,
        "independent_expert_adjudication_verified": False,
    }
    try:
        run = continue_recorded_context(client)
        base.update(
            status=(
                "REAL_RESEARCH_SYNTHESIS_COMPLETED_METHOD_REVIEW_REQUIRED"
                if run.hypotheses
                else "REAL_RESEARCH_SYNTHESIS_COMPLETED_NO_HYPOTHESIS"
            ),
            continuation_inference=client.provenance,
            run=run.as_dict(),
        )
        print(json.dumps(base, ensure_ascii=False, indent=2, allow_nan=False))
    except Exception:
        base.update(
            status="REAL_RESEARCH_CONTINUATION_FAILED_NO_RETRY",
            continuation_inference=client.provenance,
        )
        print(json.dumps(base, ensure_ascii=False, indent=2, allow_nan=False))
        raise


if __name__ == "__main__":
    main()

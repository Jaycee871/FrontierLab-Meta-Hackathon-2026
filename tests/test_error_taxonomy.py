from frontierlab.error_taxonomy import (
    CITATION,
    EVIDENCE,
    GOVERNANCE,
    MODEL_RUNTIME,
    RESOURCE,
    SCIENTIFIC_TENSION,
    classify_run,
)
from frontierlab.models import Audit, Run


def _run(*, log=None, audit=None, backend="none", inference=None):
    return Run(
        question="q",
        mode="live",
        model="m",
        papers=[],
        audit=audit or Audit(),
        hypotheses=[],
        skeptic={},
        log=log or [],
        backend=backend,
        inference=inference,
    )


def test_expected_human_review_gate_is_not_runtime_failure():
    result = classify_run(_run(log=[{
        "role": "Human Claim Review",
        "status": "BLOCKED",
        "note": "Claim-level semantic judgments pending researcher annotations",
    }]))
    assert result["counts"] == {GOVERNANCE: 1}
    assert result["runtime_failures"] == 0
    assert result["non_runtime_blocks"] == 1


def test_evidence_citation_and_resource_blocks_are_separate_categories():
    run = _run(log=[
        {"role": "Audit Gate", "status": "BLOCKED", "note": "Insufficient distinct sourced claims"},
        {"role": "Citation Gate", "status": "BLOCKED", "note": "invalid source IDs"},
        {"role": "Meta AI", "status": "BLOCKED", "note": "No explicit local model selected"},
    ])
    result = classify_run(run)
    assert result["counts"][EVIDENCE] == 1
    assert result["counts"][CITATION] == 1
    assert result["counts"][RESOURCE] == 1
    assert result["runtime_failures"] == 0


def test_rejected_source_passage_and_conflict_are_auditable():
    audit = Audit(
        rejected_claims=[{"reason": "missing/unaligned source passage"}],
        conflicts=[{"claim_key": "affinity"}],
    )
    result = classify_run(_run(audit=audit))
    assert result["counts"][CITATION] == 1
    assert result["counts"][SCIENTIFIC_TENSION] == 1
    assert result["scientific_tensions"] == 1


def test_failed_nim_receipt_is_runtime_failure_not_governance_gate():
    run = _run(
        backend="nvidia-nim",
        inference={"receipts": [{"role": "Hypothesis Agent", "status": "FAILED_NO_RETRY"}]},
    )
    result = classify_run(run)
    assert result["counts"][MODEL_RUNTIME] == 1
    assert result["runtime_failures"] == 1
    assert result["non_runtime_blocks"] == 0

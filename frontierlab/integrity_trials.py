"""Offline failure-injection probes for scientific research handoffs.

Inspired by failure modes discussed in the user's four research papers:
research lifecycle integrity, teachability, out-of-distribution data splits,
and executable paper agents. No external AI inference or scientific experiment.

These checks are deterministic *guards*, not semantic entailment classifiers,
external provenance attestations or biological validation.
"""
from __future__ import annotations

import math
from typing import Any

from .claim_verification import normalize_excerpt
from .models import Paper, Claim
from .review import source_fingerprint

RESULTS = {
    "BLOCK_BAD_SOURCE", "BLOCK_BAD_QUOTE", "BLOCK_STALE_REVIEW",
    "BLOCK_HUMAN_REVIEW", "BLOCK_REVIEW_REJECTED", "PASS_HUMAN_REVIEWED_ONLY",
    "BLOCK_NO_TOOL_RESULT", "BLOCK_TOOL_FAILURE", "BLOCK_UNVERIFIED_ORIGIN",
    "BLOCK_DATA_SPLIT_MISSING", "BLOCK_PEPTIDE_LEAKAGE",
    "PASS_DISJOINT_IDS_ONLY", "BLOCK_NO_TRANSFER_EVIDENCE",
    "DESCRIPTIVE_ONLY_NO_CAUSAL_CLAIM",
}


def check_evidence(paper: Paper, claim: Claim, *,
                   source_snapshot_sha256: str,
                   reviewer_label: str = "PENDING") -> dict:
    """A human verdict is asserted by the caller, never authenticated here."""
    if claim.paper_id != paper.paper_id or paper.synthetic:
        status = "BLOCK_BAD_SOURCE"
    elif source_snapshot_sha256 != source_fingerprint(paper):
        status = "BLOCK_STALE_REVIEW"
    elif not isinstance(claim.evidence_quote, str) or not (
        24 <= len(claim.evidence_quote.strip()) <= 500
    ) or normalize_excerpt(claim.evidence_quote) not in normalize_excerpt(paper.abstract):
        status = "BLOCK_BAD_QUOTE"
    elif reviewer_label in ("CONTRADICTED", "INSUFFICIENT"):
        status = "BLOCK_REVIEW_REJECTED"
    elif reviewer_label == "SUPPORTED":
        status = "PASS_HUMAN_REVIEWED_ONLY"
    else:
        status = "BLOCK_HUMAN_REVIEW"
    return {
        "stage": "evidence_to_hypothesis",
        "status": status,
        "citation_id": paper.paper_id,
        "source_sha256": source_fingerprint(paper),
        "quote_anchored": bool(claim.evidence_quote and (
            normalize_excerpt(claim.evidence_quote) in normalize_excerpt(paper.abstract)
        )),
        "meaning_verified_by_independent_experts": False,
        "warning": "Quote existence and user-supplied verdict cannot establish scientific truth.",
    }


def check_tool_handoff(*, tool_manifest: dict[str, Any] | None,
                       result_manifest: dict[str, Any] | None) -> dict:
    """Do not promote mocked or shape-only model output into real computation."""
    expected_hash = tool_manifest.get("request_sha256") if isinstance(tool_manifest, dict) else None
    reported_hash = result_manifest.get("request_sha256") if isinstance(result_manifest, dict) else None
    if not isinstance(tool_manifest, dict) or tool_manifest.get("status") != "PREPARED_NOT_EXECUTED" or not expected_hash:
        status = "BLOCK_NO_TOOL_RESULT"
    elif not isinstance(result_manifest, dict):
        status = "BLOCK_NO_TOOL_RESULT"
    elif reported_hash != expected_hash:
        status = "BLOCK_UNVERIFIED_ORIGIN"
    elif result_manifest.get("status") in ("FAILED", "ERROR", "API_ERROR"):
        status = "BLOCK_TOOL_FAILURE"
    else:
        # A user can manufacture shape-valid JSON or an "executed" field.
        # Origin requires a separate trust mechanism (e.g. recorded job identity,
        # authenticated provider receipt); this module deliberately cannot attest it.
        status = "BLOCK_UNVERIFIED_ORIGIN"
    return {
        "stage": "experiment_to_claim",
        "status": status,
        "origin_authentication_implemented": False,
        "experimental_validity_established": False,
        "warning": "No trusted runtime attestation; result shape or claimed success is insufficient.",
    }


def check_peptide_split(*, train_peptides: list[str],
                        test_peptides: list[str],
                        unseen_peptides: list[str]) -> dict:
    """Conservative group-level *exact peptide ID* overlap check.

    This does not detect homologous sequences, other sample leakage or
    negative-label construction artifacts.
    """
    groups = [train_peptides, test_peptides, unseen_peptides]
    if any(not isinstance(seq, list) or not seq or
           any(not isinstance(x, str) or not x.strip() for x in seq)
           for seq in groups):
        return {"stage": "dataset_to_evaluation", "status": "BLOCK_DATA_SPLIT_MISSING",
                "overlap": [], "ood_generalization_established": False}
    names = [set(x.strip().upper() for x in seq) for seq in groups]
    overlap = sorted((names[0] & names[1]) | (names[0] & names[2]) | (names[1] & names[2]))
    status = "BLOCK_PEPTIDE_LEAKAGE" if overlap else "PASS_DISJOINT_IDS_ONLY"
    return {"stage": "dataset_to_evaluation", "status": status,
            "overlap": overlap, "ood_generalization_established": False,
            "warning": "Exact group ID disjointness does not establish true out-of-distribution generalization."}


def check_transfer(*, pre_scores: dict[str, float],
                   post_scores: dict[str, float],
                   heldout_problems: bool,
                   intervention_documented: bool) -> dict:
    """Record an observed delta, never claim causal knowledge transfer."""
    valid = (
        isinstance(pre_scores, dict) and isinstance(post_scores, dict)
        and bool(pre_scores) and pre_scores.keys() == post_scores.keys()
        and all(isinstance(k, str) and k.strip()
                and type(pre_scores[k]) in (int, float)
                and type(post_scores[k]) in (int, float)
                and math.isfinite(pre_scores[k]) and math.isfinite(post_scores[k])
                and 0 <= pre_scores[k] <= 100 and 0 <= post_scores[k] <= 100
                for k in pre_scores)
    )
    if not valid or not heldout_problems or not intervention_documented:
        return {"stage": "machine_concept_to_human", "status": "BLOCK_NO_TRANSFER_EVIDENCE",
                "knowledge_transfer_proven": False}
    changes = {k: round(post_scores[k] - pre_scores[k], 3) for k in sorted(pre_scores)}
    return {"stage": "machine_concept_to_human",
            "status": "DESCRIPTIVE_ONLY_NO_CAUSAL_CLAIM",
            "participant_count": len(changes), "changes_in_percentage_points": changes,
            "knowledge_transfer_proven": False,
            "warning": "Descriptive before/after numbers alone cannot establish causal human learning."}


def failure_cases() -> list[dict]:
    """Twelve authored FICTIONAL guard checks; NOT real model accuracy."""
    paper = Paper("PMID:EXAMPLE1", "Fictional Example", "2026", "Test",
                  "The fictional treatment showed no improvement in the test assay.",
                  "https://example.org/study1", synthetic=False)
    claim = Claim(paper.paper_id, "treatment", "supports",
                  "The treatment improves outcomes.", "Fictional example",
                  evidence_quote=paper.abstract, passage_matched=True)
    wrong_paper = Paper("PMID:EXAMPLE2", "Other Fictional Example", "2026", "Test",
                        "An unrelated fictional outcome was observed in a different assay.",
                        "https://example.org/study2")
    reviewed_sha = source_fingerprint(paper)
    cases = [
        ("valid quote / still awaiting reviewer", "BLOCK_HUMAN_REVIEW",
         check_evidence(paper, claim, source_snapshot_sha256=reviewed_sha)),
        ("wrong source identifier", "BLOCK_BAD_SOURCE",
         check_evidence(wrong_paper, claim, source_snapshot_sha256=reviewed_sha)),
        ("fabricated excerpt", "BLOCK_BAD_QUOTE",
         check_evidence(paper, Claim(paper.paper_id, "treatment", "supports",
                      claim.statement, claim.limitation,
                      "An improvement was observed in an entirely different trial."),
                      source_snapshot_sha256=reviewed_sha)),
        ("same identifier / revised abstract", "BLOCK_STALE_REVIEW",
         check_evidence(Paper(paper.paper_id,paper.title,paper.year,paper.authors,
                       paper.abstract+" Later correction.",paper.url),
                       claim, source_snapshot_sha256=reviewed_sha, reviewer_label="SUPPORTED")),
        ("human rejected semantic conclusion", "BLOCK_REVIEW_REJECTED",
         check_evidence(paper, claim, source_snapshot_sha256=reviewed_sha,
                        reviewer_label="CONTRADICTED")),
        ("human accepted but science not proven", "PASS_HUMAN_REVIEWED_ONLY",
         check_evidence(paper, claim, source_snapshot_sha256=reviewed_sha,
                        reviewer_label="SUPPORTED")),
        ("NIM JSON looks plausible / no origin attestation", "BLOCK_UNVERIFIED_ORIGIN",
         check_tool_handoff(tool_manifest={"status": "PREPARED_NOT_EXECUTED", "request_sha256": "abc"},
                            result_manifest={"status":"RESPONSE_SHAPE_CHECKED_ORIGIN_UNVERIFIED",
                                             "request_sha256":"abc","confidence_scores":[0.99]})),
        ("NIM returned explicit failure", "BLOCK_TOOL_FAILURE",
         check_tool_handoff(tool_manifest={"status": "PREPARED_NOT_EXECUTED", "request_sha256":"abc"},
                            result_manifest={"status":"API_ERROR", "request_sha256":"abc"})),
        ("peptide group overlap", "BLOCK_PEPTIDE_LEAKAGE",
         check_peptide_split(train_peptides=["PEPTIDE_A","PEPTIDE_B"],
                             test_peptides=["PEPTIDE_C"],
                             unseen_peptides=["PEPTIDE_B"])),
        ("disjoint peptide identifiers only", "PASS_DISJOINT_IDS_ONLY",
         check_peptide_split(train_peptides=["PEPTIDE_A","PEPTIDE_B"],
                             test_peptides=["PEPTIDE_C"],
                             unseen_peptides=["PEPTIDE_D"])),
        ("human transfer test lacks holdout", "BLOCK_NO_TRANSFER_EVIDENCE",
         check_transfer(pre_scores={"person1":50},post_scores={"person1":75},
                        heldout_problems=False,intervention_documented=True)),
        ("human transfer results are observational", "DESCRIPTIVE_ONLY_NO_CAUSAL_CLAIM",
         check_transfer(pre_scores={"person1":50,"person2":75},
                        post_scores={"person1":75,"person2":75},
                        heldout_problems=True,intervention_documented=True)),
    ]
    return [{
        "id": f"F{i:02d}", "scenario": label, "expected": expected,
        "observed": report["status"], "matched_handwritten_expectation": expected==report["status"],
        "result": report, "data_origin": "FICTIONAL_HAND_AUTHORED",
    } for i,(label,expected,report) in enumerate(cases,1)]


def suite_report() -> dict:
    trials = failure_cases()
    return {
        "suite": "frontierlab.offline-failure-lab.v1",
        "total": len(trials), "matched_expectations": sum(c["matched_handwritten_expectation"] for c in trials),
        "model_calls": 0, "actual_scientific_experiments": 0,
        "independent_semantic_verification": False,
        "is_model_accuracy_benchmark": False,
        "cases": trials,
    }

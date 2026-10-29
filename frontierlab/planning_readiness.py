"""Deterministic Stage-5 planning-readiness packet.

This module prepares the exact evidence/method constraints that a future Planning
Agent must receive. It never authorizes planning and never calls a model.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json

from .evaluation import require_evaluation, selected_method
from .models import Run
from .review import approved_claims, review_packet

SCHEMA = "frontierlab.planning-readiness.v1"


def _digest(value) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def _reviewed_source_ids(run: Run) -> list[str]:
    if run.mode != "live":
        return sorted(p.paper_id for p in run.papers if p.synthetic)
    if not isinstance(run.review, dict):
        raise PermissionError("Planning readiness requires current human review")
    if run.review.get("dataset_id") != review_packet(run)["dataset_id"]:
        raise PermissionError("Planning readiness review is stale")
    if run.review.get("status") != "READY_FOR_HUMAN_GATED_SYNTHESIS":
        raise PermissionError("Planning readiness requires completed supportive review")
    return sorted({claim.paper_id for claim in approved_claims(run)})


def _hypothesis_records(run: Run, reviewed_ids: set[str]) -> list[dict]:
    records = []
    for index, hypothesis in enumerate(run.hypotheses or [], 1):
        if not isinstance(hypothesis, dict):
            raise ValueError("Hypotheses must be structured objects")
        text = hypothesis.get("text")
        ids = hypothesis.get("evidence_ids")
        rationale = hypothesis.get("rationale")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Planning readiness requires hypothesis text")
        if (
            not isinstance(ids, list)
            or not ids
            or any(not isinstance(value, str) or value not in reviewed_ids for value in ids)
        ):
            raise PermissionError("Hypothesis cites evidence outside reviewed sources")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("Planning readiness requires hypothesis rationale")
        records.append({
            "hypothesis_id": f"H{index}",
            "text": text.strip(),
            "evidence_ids": list(ids),
            "rationale": rationale.strip(),
        })
    if not records:
        raise PermissionError("Planning readiness requires at least one hypothesis")
    return records


def build_planning_readiness(run: Run) -> dict:
    """Build a pre-planning contract without approving or generating a plan."""
    if run.plan is not None:
        raise PermissionError("Planning readiness packet is only for runs with no generated plan")

    evaluation = require_evaluation(run)
    method = selected_method(evaluation)
    reviewed_ids = _reviewed_source_ids(run)
    hypotheses = _hypothesis_records(run, set(reviewed_ids))

    method_ids = method.get("evidence_ids", [])
    if any(source_id not in reviewed_ids for source_id in method_ids):
        raise PermissionError("Selected method cites evidence outside reviewed sources")

    open_checks = deepcopy(method.get("open_checks", []))
    open_items = [item.get("item") for item in open_checks if isinstance(item, dict)]
    documented_checks = [
        key
        for key, record in method.get("checks", {}).items()
        if isinstance(record, dict) and record.get("status") == "documented"
    ]

    obligations = [
        {
            "obligation_id": "design-input-provenance",
            "category": "reproducibility",
            "required": True,
            "status": "OPEN" if "data" in open_items else "DOCUMENTED",
            "requirement": (
                "Record the structural/design inputs, candidate-ranking inputs and output provenance "
                "used by the selected computational design path."
            ),
        },
        {
            "obligation_id": "executable-design-stack",
            "category": "reproducibility",
            "required": True,
            "status": "OPEN" if "code" in open_items else "DOCUMENTED",
            "requirement": (
                "Identify a reproducible ADAPT implementation or an explicitly named executable "
                "alternative before treating computational ranking as reproducible."
            ),
        },
        {
            "obligation_id": "computational-environment",
            "category": "reproducibility",
            "required": True,
            "status": "OPEN" if "environment" in open_items else "DOCUMENTED",
            "requirement": (
                "Record dependency versions, environment details and the protonation/modeling "
                "settings used for the dual-pH comparison."
            ),
        },
        {
            "obligation_id": "matched-ph-controls",
            "category": "validation",
            "required": True,
            "status": "REQUIRED_IN_PLAN",
            "requirement": (
                "Prespecify acidic and physiological-pH comparison conditions, matched controls "
                "and a falsification condition before interpreting pH-selective behavior."
            ),
        },
        {
            "obligation_id": "fab-level-validation",
            "category": "validation",
            "required": True,
            "status": "REQUIRED_IN_PLAN",
            "requirement": (
                "Keep Fab-level validation distinct from cell-surface and full-antibody readouts."
            ),
        },
        {
            "obligation_id": "orthogonal-spr",
            "category": "validation",
            "required": True,
            "status": "REQUIRED_WHERE_FEASIBLE",
            "requirement": (
                "Where feasible, include orthogonal SPR on monomeric Fab to distinguish intrinsic "
                "affinity from avidity or stoichiometry effects."
            ),
        },
        {
            "obligation_id": "avidity-stoichiometry-caveat",
            "category": "interpretation",
            "required": True,
            "status": "REQUIRED_IN_PLAN",
            "requirement": (
                "Do not interpret apparent cell-binding affinity mechanistically without addressing "
                "avidity and stoichiometry as alternative explanations."
            ),
        },
        {
            "obligation_id": "structure-and-search-bias",
            "category": "interpretation",
            "required": True,
            "status": "REQUIRED_IN_PLAN",
            "requirement": (
                "Surface structural-model quality and the histidine-centered search assumption as "
                "limitations; M1 remains a comparator for histidine-independent solutions."
            ),
        },
        {
            "obligation_id": "replication-and-falsification",
            "category": "validation",
            "required": True,
            "status": "REQUIRED_IN_PLAN",
            "requirement": (
                "Include independent replication, explicit stopping/invalidating conditions and "
                "falsification criteria; proposed work must not be described as executed."
            ),
        },
    ]

    packet = {
        "schema": SCHEMA,
        "status": "READY_FOR_EXPLICIT_PLANNING_APPROVAL",
        "planning_approved": False,
        "model_call_authorized": False,
        "planning_model_called": False,
        "plan_generated": False,
        "question": run.question,
        "mode": run.mode,
        "backend": run.backend,
        "model": run.model,
        "context_id": evaluation["context_id"],
        "evaluation_id": evaluation["evaluation_id"],
        "evaluation_status": evaluation["status"],
        "selected_candidate_id": method["candidate_id"],
        "selected_method": {
            "name": method["name"],
            "scope": method["scope"],
            "evidence_ids": list(method_ids),
            "reproducibility_status": method["reproducibility_status"],
        },
        "reviewed_source_ids": reviewed_ids,
        "hypotheses": hypotheses,
        "open_reproducibility_checks": open_checks,
        "documented_reproducibility_checks": documented_checks,
        "planning_obligations": obligations,
        "required_method_evidence_ids": list(method_ids),
        "permitted_reviewed_evidence_ids": reviewed_ids,
        "scientific_execution_verified": False,
        "scientific_accuracy_verified": False,
        "note": (
            "This packet proves only that the current reviewed context and researcher-selected "
            "method pass FrontierLab's pre-planning software gates. It does not authorize a "
            "Planning Agent call and does not validate the scientific method."
        ),
    }
    packet["planning_readiness_id"] = _digest(packet)
    return packet


def readiness_summary(packet: dict) -> dict:
    if not isinstance(packet, dict) or packet.get("schema") != SCHEMA:
        raise ValueError("Not a FrontierLab planning-readiness packet")
    obligations = packet.get("planning_obligations", [])
    open_checks = packet.get("open_reproducibility_checks", [])
    return {
        "status": packet["status"],
        "selected_candidate_id": packet["selected_candidate_id"],
        "open_reproducibility_checks": [
            item.get("item") for item in open_checks if isinstance(item, dict)
        ],
        "required_obligations": sum(
            bool(item.get("required")) for item in obligations if isinstance(item, dict)
        ),
        "planning_approved": packet["planning_approved"],
        "model_call_authorized": packet["model_call_authorized"],
    }

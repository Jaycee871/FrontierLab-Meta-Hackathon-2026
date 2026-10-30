"""Deny-by-default capability governance for FrontierLab.

This is a software policy prototype, not legal/IRB authorization.
It never grants access to real patient-identifiable data.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
import json

SCHEMA = "frontierlab.governance-decision.v1"

ROLES = {"RESEARCHER", "REVIEWER", "AGENT_SERVICE", "EXTERNAL_COLLABORATOR"}
DATA_CLASSES = {"PUBLIC", "INTERNAL_RESEARCH", "SENSITIVE_RESEARCH", "PATIENT_IDENTIFIABLE"}
CAPABILITIES = {
    "literature.retrieve", "evidence.audit", "model.infer", "code.execute",
    "external_api.call", "planning.generate", "plan_step.approve",
    "maintenance.repair", "data.read",
}


@dataclass(frozen=True)
class PolicyRequest:
    role: str
    capability: str
    data_class: str = "PUBLIC"
    institutional_authorization: bool = False
    human_approval: bool = False
    purpose: str = ""


def _digest(body: dict) -> str:
    raw = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def _base_rule(req: PolicyRequest) -> tuple[str, str, bool, bool]:
    if req.role not in ROLES:
        return "DENY", "Unknown role: deny by default", False, False
    if req.capability not in CAPABILITIES:
        return "DENY", "Unknown capability: deny by default", False, False
    if req.data_class not in DATA_CLASSES:
        return "DENY", "Unknown data class: deny by default", False, False

    if req.data_class == "PATIENT_IDENTIFIABLE":
        return (
            "DENY",
            "Patient-identifiable data access is outside the implemented FrontierLab governance boundary",
            True, True,
        )

    if req.role == "EXTERNAL_COLLABORATOR":
        if req.data_class == "PUBLIC" and req.capability in {"literature.retrieve", "evidence.audit"}:
            return "ALLOW", "Public read/audit capability only", False, False
        return "DENY", "External collaborator role is public read/audit only", False, False

    if req.role == "REVIEWER":
        if req.capability in {"literature.retrieve", "evidence.audit", "data.read"}:
            if req.data_class == "SENSITIVE_RESEARCH":
                return "DENY", "Sensitive research data requires an institution-defined reviewer policy", True, False
            return "ALLOW", "Reviewer read/audit capability", False, False
        return "DENY", "Reviewer role cannot execute models, code, planning, approvals or repair", False, False

    if req.role == "RESEARCHER":
        if req.capability == "plan_step.approve":
            return "ALLOW", "Researcher-owned approval capability", False, False
        if req.capability == "maintenance.repair":
            return "DENY", "Automatic/bounded repair is not implemented in FrontierLab v0.37", False, True
        if req.data_class == "SENSITIVE_RESEARCH":
            return (
                "REQUIRE_HUMAN_APPROVAL",
                "Sensitive research data requires explicit institutional authorization",
                True, True,
            )
        return "ALLOW", "Researcher capability within non-patient data boundary", False, False

    if req.role == "AGENT_SERVICE":
        if req.capability in {"literature.retrieve", "evidence.audit"} and req.data_class == "PUBLIC":
            return "ALLOW", "Bounded public evidence capability", False, False
        if req.capability in {"model.infer", "code.execute", "external_api.call", "planning.generate"}:
            if req.data_class == "SENSITIVE_RESEARCH":
                return (
                    "DENY",
                    "Agent service may not access sensitive research data without an institution-defined policy",
                    True, True,
                )
            return (
                "REQUIRE_HUMAN_APPROVAL",
                "Consequential agent action requires explicit researcher approval",
                False, True,
            )
        if req.capability == "maintenance.repair":
            return "DENY", "Autonomous repair is disabled; canary may detect/quarantine only", False, True
        if req.capability == "data.read":
            if req.data_class == "PUBLIC":
                return "ALLOW", "Public data read", False, False
            return (
                "REQUIRE_HUMAN_APPROVAL",
                "Non-public research data requires explicit researcher authorization",
                req.data_class == "SENSITIVE_RESEARCH", True,
            )
        return "DENY", "Agent service lacks this capability", False, False

    return "DENY", "No policy rule matched", False, False


def evaluate(request: PolicyRequest) -> dict:
    decision, reason, institution_required, human_required = _base_rule(request)
    effective = decision
    if decision == "REQUIRE_HUMAN_APPROVAL":
        if institution_required and not request.institutional_authorization:
            effective = "DENY"
            reason = reason + "; institutional authorization is not recorded"
        elif human_required and not request.human_approval:
            effective = "REQUIRE_HUMAN_APPROVAL"
        else:
            effective = "ALLOW"
            reason = reason + "; required authorization record supplied"

    body = {
        "schema": SCHEMA,
        "request": asdict(request),
        "policy_decision": decision,
        "effective_decision": effective,
        "reason": reason,
        "institutional_authorization_required": institution_required,
        "human_approval_required": human_required,
        "patient_data_access_implemented": False,
        "legal_responsibility": "NOT_ASSIGNED_BY_FRONTIERLAB",
        "operational_accountability": (
            "RESEARCHER_OR_INSTITUTION_RECORD_REQUIRED"
            if human_required or institution_required else "ROLE_BOUND_POLICY"
        ),
        "policy_version": "frontierlab-governance-v1",
    }
    body["decision_digest"] = _digest(body)
    return body


def capability_matrix() -> list[dict]:
    rows = []
    for role in sorted(ROLES):
        for capability in sorted(CAPABILITIES):
            result = evaluate(PolicyRequest(role=role, capability=capability, data_class="PUBLIC"))
            rows.append({
                "role": role,
                "capability": capability,
                "decision": result["effective_decision"],
                "reason": result["reason"],
            })
    return rows
# Governance capability policy

> **Status:** implemented software policy prototype. Not legal advice, not an IRB decision, and not an institutional authorization system.

FrontierLab's governance layer asks:

> Who may use which research capability, on what class of data, and what authorization must exist before the action proceeds?

## Design principle: deny by default

Unknown roles, capabilities and data classifications are denied.

Roles:
- RESEARCHER
- REVIEWER
- AGENT_SERVICE
- EXTERNAL_COLLABORATOR

Data classes:
- PUBLIC
- INTERNAL_RESEARCH
- SENSITIVE_RESEARCH
- PATIENT_IDENTIFIABLE

Policy decisions:
- ALLOW
- REQUIRE_HUMAN_APPROVAL
- DENY

## Patient-identifiable data

FrontierLab does **not** implement institutional patient-data authorization, IRB enforcement or PHI controls.

Therefore PATIENT_IDENTIFIABLE access is denied for every current role even when the request claims to have human/institutional authorization.

This is deliberate fail-closed behavior.

## Consequential agent actions

The AGENT_SERVICE role may use bounded public literature/evidence capabilities directly.

Model inference, code execution, external API calls and plan generation require explicit human approval in the policy layer.

This does not replace the more specific scientific gates already implemented in the workflow.

## Role boundaries

The RESEARCHER role owns consequential scientific approvals in the current prototype.

The REVIEWER role is read/audit oriented and cannot execute models, code, planning or maintenance repair.

External collaborators are restricted to public literature retrieval/evidence audit in the default policy.

## Sensitive research data

SENSITIVE_RESEARCH access requires an institution-defined authorization record plus human approval.

FrontierLab can represent that requirement, but it does not authenticate an institution or determine whether a real-world policy is legally sufficient.

## Maintainability repair

The capability `maintenance.repair` is denied because automated repair is not implemented.

The Maintenance Canary may detect, record and quarantine a failure; it cannot grant itself permission to change trusted code.

## Responsibility boundary

Each decision records the requested role/capability/data class, policy/effective decisions, authorization requirements and a deterministic decision digest.

FrontierLab explicitly records:

`legal_responsibility = NOT_ASSIGNED_BY_FRONTIERLAB`

Legal/institutional responsibility cannot be inferred by this software policy.

## Implementation

- `frontierlab/governance.py`
- `tests/test_governance.py`

The policy is a prototype for research on workflow governance, not a replacement for institutional RBAC, IRB systems, data-use agreements or legal review.
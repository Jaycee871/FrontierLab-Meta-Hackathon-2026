"""Advisory-only repair planning for FrontierLab maintainability.

This module may classify drift/failures and propose bounded remediation steps.
It never edits dependencies, code, commits, branches, or deployment state.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

HEALTH_SCHEMA = "frontierlab.maintenance-health.v1"
BASELINE_SCHEMA = "frontierlab.maintenance-baseline.v1"
PROPOSAL_SCHEMA = "frontierlab.maintenance-repair-proposal.v1"


def _digest(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(raw.encode("utf-8")).hexdigest()


def compare_to_baseline(health: dict, baseline: dict) -> dict:
    if health.get("schema") != HEALTH_SCHEMA:
        raise ValueError("Unexpected maintenance health schema")
    if baseline.get("schema") != BASELINE_SCHEMA:
        raise ValueError("Unexpected maintenance baseline schema")

    current = health.get("environment", {})
    reference = baseline.get("environment", {})
    current_packages = current.get("installed_packages", {})
    baseline_packages = reference.get("installed_packages", {})

    package_changes = []
    for name in sorted(set(current_packages) | set(baseline_packages)):
        before = baseline_packages.get(name)
        after = current_packages.get(name)
        if before != after:
            package_changes.append({"package": name, "baseline": before, "current": after})

    req_current = current.get("requirements_sha256", {})
    req_baseline = reference.get("requirements_sha256", {})
    requirement_changes = []
    for name in sorted(set(req_current) | set(req_baseline)):
        before = req_baseline.get(name)
        after = req_current.get(name)
        if before != after:
            requirement_changes.append({"file": name, "baseline": before, "current": after})

    python_changed = current.get("python_version") != reference.get("python_version")
    fingerprint_changed = (
        current.get("dependency_fingerprint") != reference.get("dependency_fingerprint")
    )

    return {
        "dependency_fingerprint_changed": fingerprint_changed,
        "python_version_changed": python_changed,
        "package_changes": package_changes,
        "requirements_hash_changes": requirement_changes,
        "drift_detected": bool(
            fingerprint_changed or python_changed or package_changes or requirement_changes
        ),
    }


def classify_failure(health: dict, pytest_output: str, drift: dict) -> dict:
    if health.get("schema") != HEALTH_SCHEMA:
        raise ValueError("Unexpected maintenance health schema")
    text = pytest_output if isinstance(pytest_output, str) else ""
    lowered = text.lower()
    failed = health.get("status") != "HEALTHY"

    if not failed:
        return {
            "category": "HEALTHY_DRIFT" if drift.get("drift_detected") else "HEALTHY_STABLE",
            "confidence": "HIGH",
            "reason": (
                "Regression suite passed but environment/dependency drift was observed."
                if drift.get("drift_detected")
                else "Regression suite passed and no baseline drift was observed."
            ),
        }

    if re.search(r"modulenotfounderror|no module named|package not found", lowered):
        category = "MISSING_DEPENDENCY"
        reason = "Failure log indicates a missing Python package/module."
    elif re.search(r"importerror|cannot import name|version conflict|resolutionimpossible", lowered):
        category = "DEPENDENCY_COMPATIBILITY"
        reason = "Failure log indicates an import/version compatibility problem."
    elif re.search(
        r"jsondecodeerror|validationerror|schema|unexpected field|missing required|keyerror",
        lowered,
    ):
        category = "INTERFACE_OR_SCHEMA_DRIFT"
        reason = "Failure log indicates a structured-output/API/schema contract mismatch."
    elif re.search(r"connectionerror|timeout|timed out|ssl|http error|429|502|503|504", lowered):
        category = "EXTERNAL_RESOURCE_OR_NETWORK"
        reason = "Failure log indicates an external service/network class failure."
    elif drift.get("drift_detected"):
        category = "DEPENDENCY_OR_ENVIRONMENT_DRIFT"
        reason = "Regression failure coincides with a change from the accepted healthy baseline."
    elif health.get("regression_test", {}).get("errors", 0):
        category = "TEST_ENVIRONMENT_ERROR"
        reason = "Pytest reported errors without an identified dependency/schema signature."
    else:
        category = "SOFTWARE_REGRESSION"
        reason = "Regression tests failed while the accepted dependency baseline appears unchanged."

    return {"category": category, "confidence": "HEURISTIC", "reason": reason}


def _actions_for(category: str) -> list[dict]:
    common_validate = [
        "Re-run the full software regression suite in an isolated environment.",
        "Generate a new maintenance health record and compare its dependency fingerprint.",
        "Require human review before changing the accepted maintenance baseline or promoting the revision.",
    ]
    actions = {
        "HEALTHY_STABLE": [
            "Preserve the health record as maintenance evidence.",
            "No repair action is required.",
        ],
        "HEALTHY_DRIFT": [
            "Review the package/Python/requirements drift against the accepted baseline.",
            "If the drift is intentional, update the baseline only through an explicit reviewed repository change.",
            "If the drift is unexpected, reproduce the prior baseline in isolation before changing dependency constraints.",
        ] + common_validate,
        "MISSING_DEPENDENCY": [
            "Identify which import is absent and which declared dependency should provide it.",
            "Recreate the environment from the existing requirement files before editing dependency constraints.",
            "If declaration is genuinely missing, prepare a minimal dependency change for human review.",
        ] + common_validate,
        "DEPENDENCY_COMPATIBILITY": [
            "Compare current package versions with the last accepted healthy baseline.",
            "Reproduce the failure using the baseline versions.",
            "Prepare the smallest compatible pin/range change as a proposal; do not apply it automatically.",
        ] + common_validate,
        "INTERFACE_OR_SCHEMA_DRIFT": [
            "Locate the failing input/output contract and capture the changed schema or payload.",
            "Add or update a regression fixture that reproduces the contract change.",
            "Prepare an adapter/validator change that fails closed for unknown fields or missing required data.",
        ] + common_validate,
        "EXTERNAL_RESOURCE_OR_NETWORK": [
            "Separate transient connectivity/provider failure from a local software regression.",
            "Record provider/status evidence where available and avoid changing scientific logic to mask an outage.",
            "Re-run only after connectivity/provider conditions are understood; automatic retry remains disabled on the verified NIM path.",
        ] + common_validate,
        "DEPENDENCY_OR_ENVIRONMENT_DRIFT": [
            "Compare Python/package versions and requirements hashes with the accepted baseline.",
            "Reproduce the revision under the baseline environment.",
            "Prepare a bounded environment/dependency change only after identifying the drift component correlated with failure.",
        ] + common_validate,
        "TEST_ENVIRONMENT_ERROR": [
            "Inspect collection/setup errors before modifying application code.",
            "Check filesystem, environment variables and test dependencies in isolation.",
        ] + common_validate,
        "SOFTWARE_REGRESSION": [
            "Identify the smallest failing test set and the first bad code change.",
            "Prepare a minimal code patch on a non-trusted branch.",
            "Add a regression test that would have caught the failure before accepting the patch.",
        ] + common_validate,
    }
    return [{"order": i + 1, "action": item} for i, item in enumerate(actions[category])]


def build_repair_proposal(*, health: dict, baseline: dict, pytest_output: str) -> dict:
    drift = compare_to_baseline(health, baseline)
    classification = classify_failure(health, pytest_output, drift)
    category = classification["category"]

    if category == "HEALTHY_STABLE":
        status = "NO_REPAIR_NEEDED"
    elif category == "HEALTHY_DRIFT":
        status = "DRIFT_REVIEW_REQUIRED"
    else:
        status = "REPAIR_PROPOSAL_READY"

    proposal = {
        "schema": PROPOSAL_SCHEMA,
        "status": status,
        "source_health_status": health.get("status"),
        "source_sha": health.get("source_sha"),
        "baseline_source_sha": baseline.get("source_sha"),
        "baseline_source_run_id": baseline.get("source_run_id"),
        "drift": drift,
        "classification": classification,
        "proposed_actions": _actions_for(category),
        "required_validation": [
            "Full software regression suite must pass.",
            "Maintenance health status must return HEALTHY.",
            "Dependency/environment changes must be explicit in the new health record.",
            "Scientific accuracy is not inferred from software-test success.",
        ],
        "governance": {
            "advisory_only": True,
            "automatic_repair_enabled": False,
            "automatic_dependency_edit_enabled": False,
            "automatic_code_edit_enabled": False,
            "automatic_commit_enabled": False,
            "automatic_merge_enabled": False,
            "automatic_deploy_enabled": False,
            "baseline_update_requires_human_review": True,
            "promotion_requires_human_approval": True,
        },
        "note": (
            "This proposal is deterministic advisory output from software/environment evidence. "
            "It does not execute repairs and does not establish scientific validity."
        ),
    }
    proposal["proposal_id"] = _digest(proposal)
    return proposal

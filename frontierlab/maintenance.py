"""Maintainability canary records for FrontierLab.

Phase 1 detects dependency/environment regressions and preserves provenance.
It deliberately does not repair, commit, merge, or promote code automatically.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Mapping

SCHEMA = "frontierlab.maintenance-health.v1"


def _sha(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def dependency_fingerprint(
    *,
    python_version: str,
    requirements: Mapping[str, str],
    installed_packages: Mapping[str, str],
) -> str:
    body = {
        "python_version": python_version,
        "requirements": dict(sorted(requirements.items())),
        "installed_packages": dict(sorted(installed_packages.items())),
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return _sha(raw)


def parse_pytest_summary(text: str) -> dict:
    """Extract coarse test counts without treating tests as model/science accuracy."""
    text = text if isinstance(text, str) else ""
    patterns = {
        "passed": r"(\d+)\s+passed",
        "failed": r"(\d+)\s+failed",
        "errors": r"(\d+)\s+errors?",
        "skipped": r"(\d+)\s+skipped",
    }
    values = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        values[key] = int(matches[-1]) if matches else 0
    return {
        "passed": values["passed"],
        "failed": values["failed"],
        "errors": values["errors"],
        "skipped": values["skipped"],
    }


def build_health_report(
    *,
    frontierlab_version: str,
    source_sha: str | None,
    trigger: str,
    python_version: str,
    requirements: Mapping[str, str],
    installed_packages: Mapping[str, str],
    pytest_exit_code: int,
    pytest_output: str,
) -> dict:
    if not isinstance(pytest_exit_code, int):
        raise ValueError("pytest_exit_code must be an integer")
    if not isinstance(trigger, str) or not trigger.strip():
        raise ValueError("trigger required")

    req_hashes = {name: _sha(text) for name, text in sorted(requirements.items())}
    tests = parse_pytest_summary(pytest_output)
    healthy = pytest_exit_code == 0
    status = "HEALTHY" if healthy else "QUARANTINE_REQUIRED"

    return {
        "schema": SCHEMA,
        "status": status,
        "frontierlab_version": frontierlab_version,
        "source_sha": source_sha,
        "trigger": trigger.strip(),
        "environment": {
            "python_version": python_version,
            "requirements_sha256": req_hashes,
            "installed_packages": dict(sorted(installed_packages.items())),
            "dependency_fingerprint": dependency_fingerprint(
                python_version=python_version,
                requirements=requirements,
                installed_packages=installed_packages,
            ),
        },
        "regression_test": {
            "exit_code": pytest_exit_code,
            **tests,
            "software_tests_only": True,
            "scientific_accuracy_measured": False,
        },
        "maintenance_policy": {
            "failure_detected": not healthy,
            "automatic_repair_enabled": False,
            "repair_attempted": False,
            "automatic_environment_rebuild_enabled": False,
            "automatic_commit_enabled": False,
            "automatic_merge_enabled": False,
            "human_approval_required_before_promotion": True,
            "promotion_allowed": healthy,
        },
        "next_action": (
            "No maintenance action required; preserve this health record."
            if healthy
            else "Quarantine this revision/environment, inspect the failing test log, and require human-approved repair before promotion."
        ),
        "note": (
            "This canary detects software/environment regressions and records provenance. "
            "It does not establish scientific validity and does not perform autonomous repair."
        ),
    }
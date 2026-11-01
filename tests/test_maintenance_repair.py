import copy

from frontierlab.maintenance import build_health_report
from frontierlab.maintenance_repair import (
    build_repair_proposal,
    compare_to_baseline,
)


REQS = {
    "requirements.txt": "streamlit>=1.40,<2\nrequests>=2.31,<3\n",
    "requirements-dev.txt": "-r requirements.txt\npytest>=8,<10\n",
}
PKGS = {"streamlit": "1.66.1", "requests": "2.34.2", "openai": "2.54.0", "pytest": "9.2.0"}


def _health(exit_code=0, output="361 passed in 4.93s", packages=None):
    return build_health_report(
        frontierlab_version="0.37",
        source_sha="current",
        trigger="schedule",
        python_version="3.11.17",
        requirements=REQS,
        installed_packages=packages or PKGS,
        pytest_exit_code=exit_code,
        pytest_output=output,
    )


def _baseline():
    health = _health()
    return {
        "schema": "frontierlab.maintenance-baseline.v1",
        "source_run_id": 41292083692,
        "source_artifact_id": 13077402513,
        "source_sha": "baseline",
        "environment": copy.deepcopy(health["environment"]),
    }


def test_stable_healthy_environment_needs_no_repair():
    proposal = build_repair_proposal(
        health=_health(), baseline=_baseline(), pytest_output="361 passed in 4.93s"
    )
    assert proposal["status"] == "NO_REPAIR_NEEDED"
    assert proposal["classification"]["category"] == "HEALTHY_STABLE"
    assert proposal["drift"]["drift_detected"] is False
    assert proposal["governance"]["automatic_repair_enabled"] is False


def test_healthy_package_drift_requires_review_not_quarantine():
    packages = {**PKGS, "streamlit": "1.67.0"}
    proposal = build_repair_proposal(
        health=_health(packages=packages),
        baseline=_baseline(),
        pytest_output="361 passed in 4.93s",
    )
    assert proposal["status"] == "DRIFT_REVIEW_REQUIRED"
    assert proposal["classification"]["category"] == "HEALTHY_DRIFT"
    assert proposal["drift"]["package_changes"] == [
        {"package": "streamlit", "baseline": "1.66.1", "current": "1.67.0"}
    ]
    assert proposal["governance"]["baseline_update_requires_human_review"] is True


def test_missing_dependency_failure_gets_specific_advisory_plan():
    output = "ModuleNotFoundError: No module named 'scanpy'\n1 error in 0.3s"
    proposal = build_repair_proposal(
        health=_health(exit_code=1, output=output),
        baseline=_baseline(),
        pytest_output=output,
    )
    assert proposal["status"] == "REPAIR_PROPOSAL_READY"
    assert proposal["classification"]["category"] == "MISSING_DEPENDENCY"
    joined = " ".join(item["action"] for item in proposal["proposed_actions"])
    assert "existing requirement files" in joined
    assert proposal["governance"]["automatic_dependency_edit_enabled"] is False


def test_schema_failure_is_not_misclassified_as_dependency_repair():
    output = "ValidationError: missing required field source_id\n1 failed, 360 passed"
    proposal = build_repair_proposal(
        health=_health(exit_code=1, output=output),
        baseline=_baseline(),
        pytest_output=output,
    )
    assert proposal["classification"]["category"] == "INTERFACE_OR_SCHEMA_DRIFT"
    assert proposal["governance"]["automatic_code_edit_enabled"] is False


def test_failed_run_with_dependency_change_flags_environment_drift():
    packages = {**PKGS, "requests": "2.35.0"}
    output = "AssertionError: expected 200 got 500\n1 failed, 360 passed"
    proposal = build_repair_proposal(
        health=_health(exit_code=1, output=output, packages=packages),
        baseline=_baseline(),
        pytest_output=output,
    )
    assert proposal["classification"]["category"] == "DEPENDENCY_OR_ENVIRONMENT_DRIFT"
    assert proposal["drift"]["dependency_fingerprint_changed"] is True
    assert proposal["governance"]["automatic_merge_enabled"] is False


def test_compare_rejects_wrong_baseline_schema():
    import pytest
    baseline = _baseline()
    baseline["schema"] = "wrong"
    with pytest.raises(ValueError, match="baseline schema"):
        compare_to_baseline(_health(), baseline)

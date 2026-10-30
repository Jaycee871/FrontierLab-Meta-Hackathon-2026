from frontierlab.maintenance import (
    build_health_report, dependency_fingerprint, parse_pytest_summary,
)


REQS = {
    "requirements.txt": "streamlit>=1.40,<2\\nrequests>=2.31,<3\\n",
    "requirements-dev.txt": "-r requirements.txt\\npytest>=8,<10\\n",
}
PKGS = {"streamlit": "1.66.1", "requests": "2.34.2", "pytest": "9.2.0"}


def test_parse_pytest_summary_for_success_and_failure():
    assert parse_pytest_summary("356 passed in 4.58s") == {
        "passed": 356, "failed": 0, "errors": 0, "skipped": 0
    }
    assert parse_pytest_summary("1 failed, 355 passed, 2 skipped in 4.8s") == {
        "passed": 355, "failed": 1, "errors": 0, "skipped": 2
    }


def test_dependency_fingerprint_changes_when_requirements_or_environment_change():
    baseline = dependency_fingerprint(
        python_version="3.11.17", requirements=REQS, installed_packages=PKGS
    )
    changed_req = dependency_fingerprint(
        python_version="3.11.17",
        requirements={**REQS, "requirements.txt": REQS["requirements.txt"] + "openai>=1.98,<3\\n"},
        installed_packages=PKGS,
    )
    changed_pkg = dependency_fingerprint(
        python_version="3.11.17",
        requirements=REQS,
        installed_packages={**PKGS, "streamlit": "1.67.0"},
    )
    assert baseline != changed_req
    assert baseline != changed_pkg


def test_healthy_report_allows_promotion_but_never_auto_repairs():
    report = build_health_report(
        frontierlab_version="0.37", source_sha="abc", trigger="schedule",
        python_version="3.11.17", requirements=REQS, installed_packages=PKGS,
        pytest_exit_code=0, pytest_output="356 passed in 4.58s",
    )
    assert report["status"] == "HEALTHY"
    assert report["regression_test"]["passed"] == 356
    policy = report["maintenance_policy"]
    assert policy["promotion_allowed"] is True
    assert policy["automatic_repair_enabled"] is False
    assert policy["repair_attempted"] is False
    assert policy["human_approval_required_before_promotion"] is True
    assert report["regression_test"]["scientific_accuracy_measured"] is False


def test_failed_regression_requires_quarantine_and_human_repair():
    report = build_health_report(
        frontierlab_version="0.37", source_sha="def", trigger="push",
        python_version="3.11.17", requirements=REQS, installed_packages=PKGS,
        pytest_exit_code=1, pytest_output="2 failed, 354 passed in 5.0s",
    )
    assert report["status"] == "QUARANTINE_REQUIRED"
    assert report["regression_test"]["failed"] == 2
    policy = report["maintenance_policy"]
    assert policy["failure_detected"] is True
    assert policy["promotion_allowed"] is False
    assert policy["automatic_commit_enabled"] is False
    assert policy["automatic_merge_enabled"] is False
    assert "human-approved repair" in report["next_action"]


def test_report_rejects_invalid_exit_code_and_empty_trigger():
    import pytest
    kwargs = dict(
        frontierlab_version="0.37", source_sha=None, python_version="3.11",
        requirements=REQS, installed_packages=PKGS, pytest_output="",
    )
    with pytest.raises(ValueError, match="integer"):
        build_health_report(trigger="push", pytest_exit_code="0", **kwargs)
    with pytest.raises(ValueError, match="trigger"):
        build_health_report(trigger=" ", pytest_exit_code=0, **kwargs)
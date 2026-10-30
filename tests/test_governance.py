import pytest

from frontierlab.governance import PolicyRequest, capability_matrix, evaluate


def test_unknown_role_capability_and_data_class_fail_closed():
    assert evaluate(PolicyRequest("UNKNOWN", "literature.retrieve"))["effective_decision"] == "DENY"
    assert evaluate(PolicyRequest("RESEARCHER", "unknown.tool"))["effective_decision"] == "DENY"
    assert evaluate(PolicyRequest("RESEARCHER", "data.read", "UNKNOWN"))["effective_decision"] == "DENY"


@pytest.mark.parametrize("role", ["RESEARCHER", "REVIEWER", "AGENT_SERVICE", "EXTERNAL_COLLABORATOR"])
def test_patient_identifiable_data_is_denied_for_every_current_role(role):
    result = evaluate(PolicyRequest(
        role=role, capability="data.read", data_class="PATIENT_IDENTIFIABLE",
        institutional_authorization=True, human_approval=True,
    ))
    assert result["effective_decision"] == "DENY"
    assert result["patient_data_access_implemented"] is False
    assert result["legal_responsibility"] == "NOT_ASSIGNED_BY_FRONTIERLAB"


def test_agent_planning_requires_explicit_human_approval():
    pending = evaluate(PolicyRequest("AGENT_SERVICE", "planning.generate"))
    assert pending["policy_decision"] == "REQUIRE_HUMAN_APPROVAL"
    assert pending["effective_decision"] == "REQUIRE_HUMAN_APPROVAL"
    approved = evaluate(PolicyRequest("AGENT_SERVICE", "planning.generate", human_approval=True))
    assert approved["effective_decision"] == "ALLOW"
    assert approved["human_approval_required"] is True


def test_sensitive_research_data_requires_institution_and_human_record():
    missing = evaluate(PolicyRequest(
        "RESEARCHER", "data.read", "SENSITIVE_RESEARCH",
        human_approval=True, institutional_authorization=False,
    ))
    assert missing["effective_decision"] == "DENY"
    assert missing["institutional_authorization_required"] is True
    allowed = evaluate(PolicyRequest(
        "RESEARCHER", "data.read", "SENSITIVE_RESEARCH",
        human_approval=True, institutional_authorization=True,
    ))
    assert allowed["effective_decision"] == "ALLOW"


def test_reviewer_and_external_collaborator_are_not_execution_roles():
    assert evaluate(PolicyRequest("REVIEWER", "code.execute"))["effective_decision"] == "DENY"
    assert evaluate(PolicyRequest("EXTERNAL_COLLABORATOR", "model.infer"))["effective_decision"] == "DENY"
    assert evaluate(PolicyRequest("EXTERNAL_COLLABORATOR", "literature.retrieve"))["effective_decision"] == "ALLOW"


def test_maintenance_repair_is_denied_because_not_implemented():
    for role in ("RESEARCHER", "AGENT_SERVICE"):
        result = evaluate(PolicyRequest(role, "maintenance.repair", human_approval=True))
        assert result["effective_decision"] == "DENY"
        assert "repair" in result["reason"].lower()


def test_decision_digest_changes_with_request():
    a = evaluate(PolicyRequest("AGENT_SERVICE", "model.infer"))
    b = evaluate(PolicyRequest("AGENT_SERVICE", "model.infer", human_approval=True))
    assert a["decision_digest"] != b["decision_digest"]


def test_public_matrix_is_deterministic_and_contains_all_role_capability_pairs():
    first = capability_matrix()
    second = capability_matrix()
    assert first == second
    assert len(first) == 4 * 9
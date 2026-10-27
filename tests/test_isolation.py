from frontierlab.isolation import evaluate

def test_allow_only_synthetic_tasks():
    assert evaluate("read_fixture", "synthetic_conflict").allowed
    assert evaluate("compute", "synthetic_heterogeneity").allowed
    assert evaluate("write_audit", "isolated_test_report").allowed

def test_network_host_secrets_repository_denied():
    for action, target in [
        ("http_request", "https://example.com"), ("read_host", "../../private"),
        ("get_secret", "NVIDIA_API_KEY"), ("commit_repository", "main"),
        ("execute_shell", "curl example.com"), ("write_audit", "../README.md")
    ]:
        result = evaluate(action, target)
        assert not result.allowed
        assert result.enforcement == "SIMULATED_APPLICATION_GATE_ONLY"

def test_unknown_names_are_not_permissions():
    assert not evaluate("READ_FIXTURE", "synthetic_conflict").allowed
    assert not evaluate("read_fixture", "synthetic_conflict/../secrets").allowed

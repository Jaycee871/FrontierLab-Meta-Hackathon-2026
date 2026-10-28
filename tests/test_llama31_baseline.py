import json
import pytest

from frontierlab.llama31_baseline import (
    BACKEND,
    CONTEXT_TOKENS,
    MODEL_ID,
    BaselineCallBudget,
    Llama31BaselineClient,
    benchmark_dimensions,
)


class FakeRuntime:
    def __init__(self, output=None):
        self.output = output or {"claims": []}
        self.calls = []

    def complete(self, **kwargs):
        self.calls.append(kwargs)
        return json.dumps(self.output)


def test_baseline_client_matches_frontierlab_json_contract():
    runtime = FakeRuntime({"claims": [{"paper_id": "P1"}]})
    client = Llama31BaselineClient(
        runtime,
        authorized=True,
        budget=BaselineCallBudget(limit=2),
    )
    out = client.json(
        "Evidence Extraction Agent",
        "Extract carefully scoped claims.",
        {"paper_id": "P1", "abstract": "example"},
    )
    assert out["claims"][0]["paper_id"] == "P1"
    assert client.model == MODEL_ID
    assert client.backend == BACKEND
    assert client.provenance["baseline_only"] is True
    assert client.provenance["context_tokens"] == CONTEXT_TOKENS
    assert client.provenance["attempted_calls"] == 1
    assert client.provenance["receipts"][0]["status"] == "JSON_OBJECT_RETURNED"
    assert len(client.provenance["receipts"][0]["input_sha256"]) == 64
    assert len(client.provenance["receipts"][0]["output_sha256"]) == 64
    assert runtime.calls[0]["temperature"] == 0.2
    assert runtime.calls[0]["top_p"] == 0.9


def test_baseline_is_explicitly_not_independent_scientific_verification():
    client = Llama31BaselineClient(FakeRuntime(), authorized=True)
    client.json("Structured Baseline Worker", "Return an empty object.", {})
    receipt = client.provenance["receipts"][0]
    assert receipt["baseline_only"] is True
    assert receipt["scientific_output_independently_verified"] is False
    assert client.provenance["scientific_outputs_independently_verified"] is False


def test_call_budget_prevents_unbounded_local_runs():
    runtime = FakeRuntime()
    client = Llama31BaselineClient(
        runtime,
        authorized=True,
        budget=BaselineCallBudget(limit=1),
    )
    client.json("Structured Baseline Worker", "first", {})
    with pytest.raises(PermissionError, match="budget exhausted"):
        client.json("Structured Baseline Worker", "second", {})
    assert len(runtime.calls) == 1


def test_invalid_json_is_failed_without_retry():
    class BadRuntime:
        def __init__(self):
            self.calls = 0

        def complete(self, **kwargs):
            self.calls += 1
            return "not-json"

    runtime = BadRuntime()
    client = Llama31BaselineClient(runtime, authorized=True)
    with pytest.raises(RuntimeError, match="no automatic retry"):
        client.json("Structured Baseline Worker", "x", {})
    assert runtime.calls == 1
    assert client.provenance["receipts"][0]["status"] == "FAILED_NO_RETRY"


def test_authorization_runtime_and_roles_are_bounded():
    with pytest.raises(PermissionError, match="authorization"):
        Llama31BaselineClient(FakeRuntime())
    with pytest.raises(TypeError, match="complete"):
        Llama31BaselineClient(object(), authorized=True)

    client = Llama31BaselineClient(FakeRuntime(), authorized=True)
    with pytest.raises(ValueError, match="Unsupported"):
        client.json("Autonomous Principal Investigator", "x", {})


def test_benchmark_dimensions_cover_reliability_and_cost_proxies():
    dims = benchmark_dimensions()
    assert "json_validity" in dims
    assert "abstention_rate" in dims
    assert "citation_id_validity" in dims
    assert "verbatim_quote_validity" in dims
    assert "researcher_intervention_rate" in dims
    assert "latency_seconds" in dims

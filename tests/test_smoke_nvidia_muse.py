"""Offline checks for truthful, reproducible single-call inference receipts."""
import hashlib
import json

import pytest

from scripts import smoke_nvidia_muse as smoke


def configure(monkeypatch, result=None, error=None):
    calls = []
    class Client:
        def complete(self, prompt, *, max_tokens):
            calls.append((prompt, max_tokens))
            if error is not None:
                raise error
            return result
    monkeypatch.setattr(smoke, "NvidiaMuseClient", Client)
    monkeypatch.setenv("FRONTIERLAB_NVIDIA_TRIAL", "YES")
    return calls


def response(**changes):
    return {
        "model": smoke.MODEL, "content": "No; the conflicting results leave uncertainty.",
        "finish_reason": "stop", "usage": {"completion_tokens": 20}, **changes
    }


def test_no_authorization_never_initializes_client(monkeypatch, capsys):
    calls = configure(monkeypatch, result=response())
    monkeypatch.delenv("FRONTIERLAB_NVIDIA_TRIAL", raising=False)
    assert smoke.main() == 2
    assert calls == []
    assert "TRIAL_NOT_AUTHORIZED" in capsys.readouterr().out


def test_success_receipt_binds_prompt_ci_revision_and_result(monkeypatch, capsys):
    calls = configure(monkeypatch, result=response())
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    monkeypatch.setenv("GITHUB_RUN_ID", "1234")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    assert smoke.main() == 0
    receipt = json.loads(capsys.readouterr().out)
    assert calls == [(smoke.PROMPT, 2048)]
    assert receipt["status"] == "REAL_INFERENCE_RETURNED"
    assert receipt["git_sha"] == "a" * 40
    assert receipt["github_run_id"] == "1234"
    assert receipt["github_run_attempt"] == "2"
    assert receipt["started_at_utc"].endswith("+00:00")
    assert receipt["elapsed_seconds"] >= 0
    assert receipt["input_sha256"] == hashlib.sha256(smoke.PROMPT.encode()).hexdigest()
    assert receipt["output_sha256"] == hashlib.sha256(response()["content"].encode()).hexdigest()
    assert receipt["synthetic_input_only"] is True
    assert receipt["paid_meta_platforms_api_used"] is False


@pytest.mark.parametrize("reason", ["length", "other"])
def test_truncated_or_unknown_finish_is_not_success(monkeypatch, capsys, reason):
    calls = configure(monkeypatch, result=response(finish_reason=reason))
    assert smoke.main() == 1
    assert len(calls) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "INCOMPLETE_FINAL_ANSWER"


@pytest.mark.parametrize("model", ["NOT_REPORTED", None, "other/model"])
def test_unidentified_model_is_not_success(monkeypatch, capsys, model):
    configure(monkeypatch, result=response(model=model))
    assert smoke.main() == 1
    assert json.loads(capsys.readouterr().out)["status"] == "MODEL_IDENTITY_UNVERIFIED"


def test_failure_receipt_does_not_leak_exception_or_retry(monkeypatch, capsys):
    calls = configure(monkeypatch, error=RuntimeError("PRIVATE-TOKEN-DO-NOT-PRINT"))
    assert smoke.main() == 1
    output = capsys.readouterr().out
    assert "PRIVATE-TOKEN" not in output
    receipt = json.loads(output)
    assert receipt["status"] == "NIM_CHECK_FAILED"
    assert receipt["error_type"] == "RuntimeError"
    assert "output_excerpt" not in receipt
    assert receipt["elapsed_seconds"] >= 0
    assert len(calls) == 1


def test_context_filters_unexpected_environment_text(monkeypatch):
    monkeypatch.setenv("GITHUB_SHA", "PRIVATE-CONTENT")
    monkeypatch.setenv("GITHUB_RUN_ID", "https://example.invalid")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "１")
    assert smoke._run_context() == {
        "git_sha": None, "github_run_id": None, "github_run_attempt": None
    }

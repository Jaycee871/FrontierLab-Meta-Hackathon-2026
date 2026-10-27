"""Offline fixtures verify one-call JSON validation, not model accuracy."""
import json
import pytest
from scripts import smoke_meta_json as trial
from frontierlab.literature_pilot import load_dataset


def fixture():
    data = load_dataset()
    packet, case, source = trial.build_packet(data)
    return packet, case, source


def prediction():
    _, case, source = fixture()
    return {"case_id": case["case_id"], "source_id": case["source_id"],
            "label": "SUPPORTED", "evidence_quote": source["source_text"],
            "explanation": "Artificial test output for the stated excerpt."}


def configure(monkeypatch, *, content=None, finish="stop", model=trial.MODEL, error=None):
    calls = []
    class Client:
        def complete(self, text, *, max_tokens):
            calls.append((text, max_tokens))
            if error:
                raise error
            return {"content": json.dumps(prediction()) if content is None else content,
                    "finish_reason": finish, "model": model, "usage": {"total_tokens": 10}}
    monkeypatch.setattr(trial, "NvidiaMuseClient", Client)
    monkeypatch.setenv("FRONTIERLAB_NVIDIA_TRIAL", "YES")
    monkeypatch.setenv("FRONTIERLAB_META_JSON_TRIAL", "YES")
    return calls


def test_prompt_contains_only_one_case_and_no_provisional_labels():
    packet, case, source = fixture()
    prompt = trial.build_prompt(packet)
    assert case["case_id"] == "R07" and source["source_id"] == "PMC4314675"
    assert "draft_reference_label" not in prompt and "draft_rationale" not in prompt
    assert len(packet["case"]) == 3
    assert "CC-BY" not in prompt  # Metadata attribution is in the receipt, not model labels.


def test_valid_quote_json_is_only_a_structural_check():
    _, case, source = fixture()
    parsed, matched = trial.validate_prediction(json.dumps(prediction()), case, source)
    assert matched and parsed["source_id"] == source["source_id"]


@pytest.mark.parametrize("fault,code", [
    ("wrong_source", "SOURCE_OR_CASE_MISMATCH"),
    ("wrong_case", "SOURCE_OR_CASE_MISMATCH"),
    ("bad_label", "INVALID_LABEL"),
    ("false_quote", "UNMATCHED_QUOTE"),
    ("extra_key", "INVALID_SCHEMA"),
    ("no_explanation", "INVALID_EXPLANATION"),
    ("nonstring", "INVALID_SCHEMA"),
])
def test_invalid_outputs_are_rejected(fault, code):
    _, case, source = fixture()
    obj = prediction()
    if fault == "wrong_source": obj["source_id"] = "PMC8686790"
    elif fault == "wrong_case": obj["case_id"] = "R01"
    elif fault == "bad_label": obj["label"] = "TRUE"
    elif fault == "false_quote": obj["evidence_quote"] = "An invented quotation not found in this excerpt."
    elif fault == "extra_key": obj["validated"] = True
    elif fault == "no_explanation": obj["explanation"] = ""
    else: obj["evidence_quote"] = [source["source_text"]]
    with pytest.raises(trial.InvalidPrediction, match=code):
        trial.validate_prediction(json.dumps(obj), case, source)


def test_markdown_or_duplicate_json_keys_do_not_pass():
    _, case, source = fixture()
    with pytest.raises(trial.InvalidPrediction, match="INVALID_JSON"):
        trial.validate_prediction("Here is JSON: " + json.dumps(prediction()), case, source)
    text = json.dumps(prediction()).replace('{"case_id":', '{"case_id":"FAKE","case_id":', 1)
    with pytest.raises(trial.InvalidPrediction, match="DUPLICATE_JSON_KEY"):
        trial.validate_prediction(text, case, source)


def test_insufficient_can_abstain_without_a_quote():
    _, case, source = fixture()
    obj = prediction()
    obj.update(label="INSUFFICIENT", evidence_quote="")
    _, matched = trial.validate_prediction(json.dumps(obj), case, source)
    assert not matched


def test_main_makes_one_request_and_does_not_score_semantics(monkeypatch, capsys):
    calls = configure(monkeypatch)
    assert trial.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert len(calls) == 1 and calls[0][1] == 2048
    assert result["status"] == "STRUCTURED_OUTPUT_AND_QUOTE_VALID"
    assert result["semantic_support_independently_verified"] is False
    assert result["reference_comparison"] == "PENDING_RESEARCHER_REVIEW"
    assert result["draft_reference_labels_sent"] is False


def test_opt_in_is_required_before_any_request(monkeypatch, capsys):
    calls = configure(monkeypatch)
    monkeypatch.delenv("FRONTIERLAB_META_JSON_TRIAL")
    assert trial.main() == 2 and not calls
    assert "NOT_AUTHORIZED" in capsys.readouterr().out


@pytest.mark.parametrize("finish,model,code", [
    ("length", trial.MODEL, "INCOMPLETE_FINAL_ANSWER"),
    ("stop", "NOT_REPORTED", "MODEL_IDENTITY_UNVERIFIED"),
])
def test_truncation_or_missing_model_fails_without_retry(monkeypatch, capsys, finish, model, code):
    calls = configure(monkeypatch, finish=finish, model=model)
    assert trial.main() == 1 and len(calls) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["error_code"] == code and "final_output" not in result


def test_failure_hides_exception_text_and_never_retries(monkeypatch, capsys):
    calls = configure(monkeypatch, error=RuntimeError("PRIVATE_TOKEN_DO_NOT_PRINT"))
    assert trial.main() == 1 and len(calls) == 1
    text = capsys.readouterr().out
    assert "PRIVATE_TOKEN" not in text
    assert json.loads(text)["status"] == "MODEL_CALL_FAILED"

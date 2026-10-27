"""Artificial outputs test batch integrity; no model performance is measured."""
import json
from copy import deepcopy
import pytest
from scripts import smoke_meta_pilot as batch
from scripts.smoke_meta_json import InvalidPrediction
from frontierlab.literature_pilot import load_dataset


def output(data):
    texts = {s["source_id"]: s["source_text"] for s in data["sources"]}
    return {"cases": [{"case_id": c["case_id"], "source_id": c["source_id"],
                       "label": "INSUFFICIENT", "evidence_quote": ""}
                      for c in data["cases"]]}


def test_batch_prompt_excludes_unreviewed_answers():
    text = batch.build_prompt(load_dataset())
    assert "draft_reference_label" not in text and "draft_rationale" not in text
    assert "exactly twelve" in text


@pytest.mark.parametrize("fault", ["missing", "duplicate", "source", "extra_key", "bad_type"])
def test_malformed_or_incomplete_batch_is_rejected(fault):
    data = load_dataset()
    obj = output(data)
    if fault == "missing": obj["cases"].pop()
    elif fault == "duplicate": obj["cases"][-1] = deepcopy(obj["cases"][0])
    elif fault == "source": obj["cases"][0]["source_id"] = "FAKE"
    elif fault == "extra_key": obj["cases"][0]["reasoning"] = "not accepted"
    else: obj["cases"][0]["label"] = []
    with pytest.raises(InvalidPrediction):
        batch.validate_batch(json.dumps(obj), data)


def test_one_request_preserves_raw_predictions_and_withholds_accuracy(monkeypatch, capsys):
    data = load_dataset()
    calls = []
    class Client:
        def complete(self, text, *, max_tokens):
            calls.append(text)
            return {"model": batch.MODEL, "finish_reason": "stop",
                    "usage": {"total_tokens": 20}, "content": json.dumps(output(data))}
    monkeypatch.setattr(batch, "NvidiaMuseClient", Client)
    monkeypatch.setenv("FRONTIERLAB_NVIDIA_TRIAL", "YES")
    monkeypatch.setenv("FRONTIERLAB_META_PILOT_TRIAL", "YES")
    assert batch.main() == 0 and len(calls) == 1
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["passage_audit"]["metrics"] is None
    assert receipt["passage_audit"]["reviewed"] == 0
    assert receipt["scientific_accuracy"] is None
    assert len(receipt["predictions"]["cases"]) == 12


def test_batch_requires_its_own_authorization(monkeypatch, capsys):
    monkeypatch.setenv("FRONTIERLAB_NVIDIA_TRIAL", "YES")
    monkeypatch.delenv("FRONTIERLAB_META_PILOT_TRIAL", raising=False)
    assert batch.main() == 2
    assert "NOT_AUTHORIZED" in capsys.readouterr().out

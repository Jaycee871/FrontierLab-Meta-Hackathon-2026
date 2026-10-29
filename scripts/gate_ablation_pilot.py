"""Offline gate comparison for the recorded 12-case pilot."""
from __future__ import annotations

import json
from pathlib import Path

from frontierlab.gate_ablation import compare_gates

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "real_ph_excerpt_cases_v1.json"
PREDICTIONS = ROOT / "docs" / "runs" / "meta_pilot_predictions_20261028.json"


def run() -> dict:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    packet = json.loads(PREDICTIONS.read_text(encoding="utf-8"))
    cases = [
        {"case_id": row["case_id"], "source_id": row["source_id"]}
        for row in dataset["cases"]
    ]
    source_texts = {
        row["source_id"]: row["source_text"]
        for row in dataset["sources"]
    }
    result = compare_gates(cases, packet["cases"], source_texts)
    result["dataset_id"] = packet["dataset_id"]
    result["model_id"] = packet["model_id"]
    result["execution_origin"] = packet["execution_origin"]
    result["reference_status"] = dataset["status"]
    return result


def main() -> None:
    result = run()
    result["accuracy_status"] = "UNAVAILABLE_PENDING_INDEPENDENT_HUMAN_GOLD"
    result["draft_reference_labels_used_as_gold"] = False
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

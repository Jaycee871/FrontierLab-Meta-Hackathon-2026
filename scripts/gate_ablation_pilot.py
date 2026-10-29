"""Offline gate comparison for the recorded 12-case pilot."""
from __future__ import annotations

import json
from pathlib import Path

from frontierlab.gate_ablation import compare_gates

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "datasets" / "real_ph_excerpt_cases_v1.json"
PREDICTIONS = ROOT / "docs" / "runs" / "meta_pilot_predictions_20261028.json"

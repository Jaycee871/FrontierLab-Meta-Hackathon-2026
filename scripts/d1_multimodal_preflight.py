"""Offline contract preflight for the optional Liquid AI d1-2B evidence gate.

This script never downloads model weights and makes no network call.
"""
from __future__ import annotations
import json

from frontierlab.multimodal_evidence import MODEL_ID, scientific_figure_questions


def main():
    claim = "Binding selectivity toward acidic pH improved relative to a parental antibody."
    packet = {
        "status": "OFFLINE_CONTRACT_PREFLIGHT_ONLY",
        "model": MODEL_ID,
        "model_loaded": False,
        "network_calls": 0,
        "questions": scientific_figure_questions(claim),
        "boundary": (
            "Decision probabilities, extracted text and boxes are model signals only. "
            "No scientific entailment is claimed; local threshold calibration and researcher review are required."
        ),
    }
    print(json.dumps(packet, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

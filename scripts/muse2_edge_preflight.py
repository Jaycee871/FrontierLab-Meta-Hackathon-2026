"""Zero-network preflight for the optional Muse2-230M edge worker."""
from __future__ import annotations
import json

from frontierlab.muse2_edge import ALLOWED_TASKS, MODEL_ID


def main():
    print(json.dumps({
        "status": "OFFLINE_CONTRACT_PREFLIGHT_ONLY",
        "model": MODEL_ID,
        "model_loaded": False,
        "network_calls": 0,
        "allowed_tasks": sorted(ALLOWED_TASKS),
        "forbidden_role": "scientific truth / entailment / clinical decision",
        "boundary": (
            "Muse2-230M is an optional local preprocessing worker for structured extraction, "
            "formatting and routing. It never replaces FrontierLab evidence or human-review gates."
        ),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

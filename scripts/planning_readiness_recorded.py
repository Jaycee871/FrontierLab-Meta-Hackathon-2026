"""Build the recorded M2 Stage-5 readiness packet with zero model calls."""
from __future__ import annotations

import json

from frontierlab.planning_readiness import build_planning_readiness
from frontierlab.recorded_replay import SOURCE_ARTIFACTS, load_recorded_m2_run

__all__ = ["load_recorded_m2_run", "run"]


def run() -> dict:
    recorded_run, selection = load_recorded_m2_run()
    packet = build_planning_readiness(recorded_run)
    packet["researcher_selection_provenance"] = {
        "schema": selection["schema"],
        "reviewer": selection["reviewer"],
        "decision": selection["decision"],
        "selected_candidate_id": selection["selected_candidate_id"],
        "recorded_date_taipei": selection["recorded_date_taipei"],
        "planning_approved": selection["planning_approved"],
        "downstream_validation_requirement": selection["downstream_validation_requirement"],
    }
    packet["source_artifacts"] = list(SOURCE_ARTIFACTS)
    return packet


def main() -> None:
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

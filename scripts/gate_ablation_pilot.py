"""CLI wrapper for the recorded 12-case Glimmer gate-ablation replay."""
from __future__ import annotations

import json
import os

from frontierlab.recorded_gate_ablation import run_recorded_pilot


def run(*, review_path: str | None = None) -> dict:
    return run_recorded_pilot(review_path=review_path)


def main() -> None:
    result = run(review_path=os.getenv("FRONTIERLAB_ABLATION_REVIEW_PATH"))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

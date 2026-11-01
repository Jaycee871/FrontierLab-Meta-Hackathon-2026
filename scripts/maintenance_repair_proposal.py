"""Build an advisory maintenance repair proposal from canary evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from frontierlab.maintenance_repair import build_repair_proposal


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--health", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--pytest-log", type=Path, required=True)
    args = parser.parse_args()

    health = json.loads(args.health.read_text(encoding="utf-8"))
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    log = args.pytest_log.read_text(encoding="utf-8", errors="replace")
    proposal = build_repair_proposal(
        health=health,
        baseline=baseline,
        pytest_output=log,
    )
    print(json.dumps(proposal, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

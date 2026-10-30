"""Emit a FrontierLab maintenance health record from the current environment."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform

from frontierlab.maintenance import build_health_report
from frontierlab.version import __version__

ROOT = Path(__file__).resolve().parents[1]
REQ_FILES = ("requirements.txt", "requirements-dev.txt")
TRACKED_PACKAGES = ("streamlit", "requests", "openai", "pytest")


def _requirements() -> dict[str, str]:
    return {name: (ROOT / name).read_text(encoding="utf-8") for name in REQ_FILES}


def _installed() -> dict[str, str]:
    versions = {}
    for name in TRACKED_PACKAGES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT_INSTALLED"
    return versions


def build_from_environment(*, pytest_exit_code: int, pytest_output: str, trigger: str) -> dict:
    return build_health_report(
        frontierlab_version=__version__,
        source_sha=os.getenv("GITHUB_SHA"),
        trigger=trigger,
        python_version=platform.python_version(),
        requirements=_requirements(),
        installed_packages=_installed(),
        pytest_exit_code=pytest_exit_code,
        pytest_output=pytest_output,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pytest-exit-code", type=int, required=True)
    parser.add_argument("--pytest-log", type=Path, required=True)
    parser.add_argument("--trigger", default=os.getenv("GITHUB_EVENT_NAME", "manual"))
    args = parser.parse_args()
    log = args.pytest_log.read_text(encoding="utf-8", errors="replace")
    print(json.dumps(
        build_from_environment(
            pytest_exit_code=args.pytest_exit_code,
            pytest_output=log,
            trigger=args.trigger,
        ),
        ensure_ascii=False, indent=2, sort_keys=True,
    ))


if __name__ == "__main__":
    main()
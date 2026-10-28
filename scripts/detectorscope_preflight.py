"""Zero-network preflight for the optional DetectorScope output-audit lens."""
from __future__ import annotations
import json

from frontierlab.detectorscope_audit import (
    DEFAULT_TAU,
    FORBIDDEN_USES,
    comparison_dimensions,
)


def main():
    print(json.dumps({
        "status": "OFFLINE_CONTRACT_PREFLIGHT_ONLY",
        "detector_loaded": False,
        "network_calls": 0,
        "default_tau": DEFAULT_TAU,
        "role": "explainability / output audit lens",
        "comparison_dimensions": comparison_dimensions(),
        "forbidden_uses": sorted(FORBIDDEN_USES),
        "boundary": (
            "DetectorScope may describe interpretable detector features in model outputs. "
            "It may not be used for academic-integrity, hiring, publication, authorship, "
            "or scientific-truth decisions."
        ),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

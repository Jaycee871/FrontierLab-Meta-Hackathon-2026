"""Run from repo root: python -m scripts.lobster_guard_demo"""
import json
from frontierlab.isolation import evaluate
CASES = [
    ("read_fixture", "synthetic_conflict"),
    ("compute", "synthetic_heterogeneity"),
    ("write_audit", "isolated_test_report"),
    ("http_request", "https://example.com"),
    ("read_host", "~/.ssh/id_rsa"),
    ("commit_repository", "main"),
    ("get_secret", "NVIDIA_API_KEY"),
]
if __name__ == "__main__":
    print(json.dumps({
        "mode": "SIMULATED APPLICATION PERMISSION GATE; NOT A REAL NVIDIA OPENSHELL TEST",
        "attempts": [evaluate(a, t).as_dict() for a, t in CASES]
    }, indent=2))

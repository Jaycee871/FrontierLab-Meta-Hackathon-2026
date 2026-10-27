"""Offline FrontierLab capability gate (NOT real OpenShell enforcement)."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
SAFE_TASKS = {"synthetic_conflict", "synthetic_heterogeneity"}

@dataclass(frozen=True)
class Decision:
    action: str
    target: str
    allowed: bool
    rule: str
    timestamp: str
    enforcement: str = "SIMULATED_APPLICATION_GATE_ONLY"
    def as_dict(self):
        return asdict(self)

def evaluate(action: str, target: str) -> Decision:
    if action in {"read_fixture", "compute"} and target in SAFE_TASKS:
        allowed, reason = True, "ALLOW_EXPLICIT_SYNTHETIC_TASK"
    elif action == "write_audit" and target == "isolated_test_report":
        allowed, reason = True, "ALLOW_SANDBOX_LOCAL_REPORT_ONLY"
    else:
        allowed, reason = False, "DENY_NOT_ON_ALLOWLIST"
    return Decision(action, target, allowed, reason, datetime.now(timezone.utc).isoformat())

"""Offline, synthetic-only evaluation. No scientific truths or API inference."""
import json
from frontierlab.claim_benchmark import benchmark, annotated_conflicts
from frontierlab.claim_verification import audit_predictions, conflict_transparency

if __name__ == "__main__":
    sources, cases = benchmark()
    out = audit_predictions(sources,cases)
    out["deliberately_undetected_conflict"] = conflict_transparency([],annotated_conflicts())
    print(json.dumps(out,ensure_ascii=False,indent=2))

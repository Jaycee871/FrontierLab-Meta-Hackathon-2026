"""Run a no-key BioNeMo Boltz-2 schema preflight. No remote inference."""
import json
from frontierlab.bionemo import prepare_boltz2, registry

# Fictional demonstration only; this sequence is not a claimed scientific target.
DEMO_SEQUENCE = "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY"

def main():
    plan = prepare_boltz2(DEMO_SEQUENCE, source_id="SYNTHETIC:TOY_SEQUENCE")
    print(json.dumps({"tools":registry(), "dry_run":plan.manifest},
                     indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

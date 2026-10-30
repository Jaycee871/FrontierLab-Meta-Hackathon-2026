# Maintainability canary

FrontierLab v0.37 implements **Phase 1 maintainability: automatic detection, provenance capture and quarantine policy**.

It does not perform autonomous repair.

## Trigger model

The GitHub Actions workflow `.github/workflows/maintenance-canary.yml` runs:

- manually (`workflow_dispatch`);
- on relevant dependency / FrontierLab code changes;
- daily at `02:17 UTC` (10:17 Asia/Taipei).

The daily schedule matters because FrontierLab uses bounded dependency ranges. A new upstream package release can therefore change the resolved environment even when the repository itself has not changed.

## Canary sequence

```text
install current dependency range
        ↓
run full regression suite
        ↓
capture exit code + pytest log
        ↓
record Python/package versions + requirements hashes
        ↓
compute dependency fingerprint
        ↓
HEALTHY or QUARANTINE_REQUIRED
        ↓
upload maintenance evidence
```

On failure the workflow still uploads its evidence and then exits non-zero.

## Governance boundary

The health record explicitly fixes these controls:

- `automatic_repair_enabled = false`
- `repair_attempted = false`
- `automatic_environment_rebuild_enabled = false`
- `automatic_commit_enabled = false`
- `automatic_merge_enabled = false`
- `human_approval_required_before_promotion = true`

A failing revision/environment therefore enters **QUARANTINE_REQUIRED** rather than being silently repaired or promoted.

## First executed canary

Feature-branch GitHub Actions run: `41064072834`

Artifact: `maintenance-canary-41064072834` (artifact ID `12980538164`)

Recorded result:

| Field | Value |
| --- | --- |
| Status | **HEALTHY** |
| FrontierLab version | 0.36 at execution time |
| Python | 3.11.17 |
| Streamlit | 1.66.1 |
| Requests | 2.34.2 |
| OpenAI | 2.54.0 |
| Pytest | 9.2.0 |
| Regression tests | **361 passed** |
| Dependency fingerprint | `ac61d837d7b2c80e5f0e6e3cb1fe6a0f5cb42705a52dba18fa2dee71f68d4b34` |
| Automatic repair | No |
| Promotion allowed | Yes, because regression tests passed |

The artifact also preserves SHA-256 hashes of `requirements.txt` and `requirements-dev.txt` plus the exact source SHA.

## What this proves

The canary proves that FrontierLab can automatically:

1. instantiate the current allowed dependency environment;
2. run regression tests;
3. detect a software-level pass/fail state;
4. record environment/dependency provenance;
5. preserve the test log and health report;
6. enforce a quarantine decision on failure.

It does **not** prove:

- autonomous repair;
- scientific reproducibility;
- scientific accuracy;
- safety of dependency upgrades beyond the software test suite.

## Next maintainability phase

The next research phase can compare:

- manual maintenance;
- automatic detection + human repair;
- automatic detection + bounded repair proposal + human promotion approval.

Any repair experiment should remain isolated and should never automatically merge into trusted main.
# Advisory maintenance repair proposals

FrontierLab Phase 2 maintainability adds an **advisory repair-proposal layer**.

It does not make FrontierLab self-healing.

## Purpose

Phase 1 already detects regression failures, records dependency/environment provenance and quarantines a failing revision.

Phase 2 answers the next question:

> Given a failed or drifted maintenance record, can the system classify the likely failure class and produce a bounded, reviewable repair plan without changing trusted code or dependencies?

## Inputs

The proposal builder receives:

- the current `maintenance_health.json`;
- the accepted healthy maintenance baseline;
- the current pytest log.

The accepted Nov 1 baseline comes from scheduled canary run **41292083692**, artifact **13077402513**:

- FrontierLab 0.37;
- Python 3.11.17;
- Streamlit 1.66.1;
- Requests 2.34.2;
- OpenAI 2.54.0;
- Pytest 9.2.0;
- dependency fingerprint `ac61d837d7b2c80e5f0e6e3cb1fe6a0f5cb42705a52dba18fa2dee71f68d4b34`;
- 361 / 361 software tests passed.

Updating the accepted baseline is a human-controlled repository change.

## Output states

### NO_REPAIR_NEEDED

Current tests pass and the dependency/environment fingerprint matches the accepted baseline.

### DRIFT_REVIEW_REQUIRED

Tests pass, but Python/package/requirements provenance differs from the accepted baseline.

This is **not** automatically a failure. The drift may be an intentional, compatible update, but a human should decide whether to accept it as the new baseline.

### REPAIR_PROPOSAL_READY

Regression tests fail.

The system classifies the likely failure class and emits an advisory sequence of investigation / repair / revalidation steps.

## Failure classes

Current deterministic classifiers include:

- `MISSING_DEPENDENCY`;
- `DEPENDENCY_COMPATIBILITY`;
- `INTERFACE_OR_SCHEMA_DRIFT`;
- `EXTERNAL_RESOURCE_OR_NETWORK`;
- `DEPENDENCY_OR_ENVIRONMENT_DRIFT`;
- `TEST_ENVIRONMENT_ERROR`;
- `SOFTWARE_REGRESSION`.

The classifications are heuristic unless the evidence is direct (for example a missing module signature). They must not be presented as root-cause proof.

## Governance boundary

Every repair proposal records:

```text
advisory_only = true
automatic_repair_enabled = false
automatic_dependency_edit_enabled = false
automatic_code_edit_enabled = false
automatic_commit_enabled = false
automatic_merge_enabled = false
automatic_deploy_enabled = false
baseline_update_requires_human_review = true
promotion_requires_human_approval = true
```

A proposal therefore cannot modify the repository, dependency constraints, baseline, deployment or trusted main branch.

## Required re-validation

Any human-approved repair must still satisfy:

1. the full software regression suite passes;
2. a new maintenance health record reports HEALTHY;
3. dependency/environment changes are explicit in provenance;
4. the baseline is not silently rewritten;
5. software-test success is not described as scientific accuracy.

## Canary integration

The Maintenance Canary now writes three artifacts:

- `maintenance_health.json`;
- `maintenance_repair_proposal.json`;
- `pytest.log`.

The proposal is emitted even for healthy runs, making the absence of a repair requirement explicit.

On a real regression failure, the workflow still uploads all evidence before enforcing quarantine.

## Research interpretation

The Phase 2 question is not:

> Can an agent rewrite itself until tests turn green?

It is:

> Can a research infrastructure detect drift/failure, explain a bounded repair path and preserve the governance boundary between machine diagnosis and human promotion?

That is the maintainability behavior currently tested by FrontierLab.

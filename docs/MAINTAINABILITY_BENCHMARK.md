# Maintainability benchmark — proposed FrontierLab experiment

> **Status:** Phase 1 detection/provenance canary executed; autonomous repair benchmark remains future work.

## Phase 1 implementation status

FrontierLab now implements the detection half of this research agenda through the [Maintenance canary](MAINTENANCE_CANARY.md).

The executed canary automatically installs the currently allowed dependency range, runs the regression suite, records environment/package provenance, computes a dependency fingerprint and emits either **HEALTHY** or **QUARANTINE_REQUIRED**.

The first executed feature-branch canary (GitHub Actions run 41064072834) produced a HEALTHY record with 361 passing tests and a preserved maintenance artifact.

Autonomous repair, environment rebuilding and automatic promotion remain disabled.

## Research question

When a research agent or scientific tool breaks because its environment changes, can the system detect, diagnose, repair and revalidate the failure without losing provenance or silently changing the scientific result?

## Why this is an Information Management problem

Scientific agents are increasingly assembled from:

- papers;
- repositories;
- packages;
- APIs;
- model providers;
- MCP tools;
- datasets;
- execution environments.

A system may be scientifically useful on day 1 and silently unusable on day 30 because one dependency changed.

Maintainability therefore becomes part of research reliability.

## Controlled failure scenarios

The benchmark can inject failures one at a time.

### M1 — dependency upgrade

Upgrade a package to an incompatible version.

Measure whether FrontierLab detects a regression and identifies dependency drift.

### M2 — missing dependency

Remove one required package.

Measure diagnosis accuracy and whether the environment can be rebuilt reproducibly.

### M3 — API schema change

Change or mock an external API response field.

Measure whether the system distinguishes interface failure from scientific insufficiency.

### M4 — model-output schema drift

Return a structurally different model response.

Measure whether contract validation fails closed rather than silently accepting malformed output.

### M5 — stale data artefact

Replace a required dataset/file with an older or mismatched version.

Measure whether provenance fingerprints prevent downstream reuse.

### M6 — environment reconstruction failure

Delete or corrupt environment metadata.

Measure whether the system can reconstruct a known-good environment from versioned manifests.

## Proposed maintenance loop

```text
controlled change
   ↓
automated regression test
   ↓
failure detection
   ↓
error classification
   ↓
bounded repair / rebuild
   ↓
reference re-validation
   ↓
human approval
   ↓
promote or quarantine
```

## Safety boundary

Initial experiments should run in isolated environments.

Automated repair should be bounded:

- no production/institutional data writes;
- no permission escalation;
- no secret modification;
- no automatic merge to trusted main;
- no silent dependency pin changes;
- no scientific claim accepted solely because the software test passes.

A repaired component should require human approval before promotion.

## Metrics

### Detection

- failure detection rate;
- time-to-detection;
- false alarm rate.

### Diagnosis

- correct error-taxonomy classification;
- correct failing component localization.

### Repair

- repair-attempt count;
- repair success rate;
- time-to-repair;
- percentage requiring human takeover.

### Revalidation

- regression-test pass rate after repair;
- reference-output agreement;
- scientific artefact equivalence/tolerance where defined.

### Provenance

- fraction of repairs with complete before/after version records;
- whether data/tool/model/environment hashes remain reconstructable;
- whether any provenance chain is broken during repair.

### Governance

- number of automated actions requiring approval;
- unauthorized-action attempts blocked;
- human intervention count.

## Experimental conditions

A useful study can compare:

```text
Condition A — manual maintenance
Condition B — automatic detection + human repair
Condition C — automatic detection + bounded automated repair + human promotion approval
```

This separates the value of detection from the value of autonomous repair.

## Outcome

The benchmark should answer more than “did the agent recover?”

It should test:

> Did the system recover **without losing reproducibility, provenance or governance guarantees**?

That is the maintainability criterion most relevant to scientific research infrastructure.

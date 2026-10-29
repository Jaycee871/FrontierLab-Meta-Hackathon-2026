# Stage 5 planning readiness

FrontierLab separates **planning readiness** from **planning authorization**.

A run can have current evidence, human review, hypotheses and a researcher-selected method while the Planning Agent remains completely disabled.

## Recorded M2 state

The current recorded biomedical path has:

- two source-bound researcher-reviewed claims;
- two citation-linked hypotheses from the bounded Muse Glimmer continuation;
- a canonical Method Evaluation with M2 selected;
- no generated plan;
- no Stage 5 planning authorization.

Selected method:

**M2 — Structure-based dual-pH histidine-scanning computational design**

Canonical IDs:

- context ID: `ee7f790ba48474bb63a935f6108f1e698121a404d93a5bf0389946ba2932dcf8`
- evaluation ID: `00c440f3a78a95a1703725ea261b992ab51551d1dedd9cf41ba481dd0954f231`

## What the readiness packet proves

`frontierlab.planning_readiness.build_planning_readiness(run)` first re-runs `require_evaluation(run)`.

If that exact evaluation is stale, altered or no longer bound to the current reviewed evidence/hypotheses, readiness fails.

A valid packet records:

```text
status = READY_FOR_EXPLICIT_PLANNING_APPROVAL
planning_approved = false
model_call_authorized = false
planning_model_called = false
plan_generated = false
```

This is an eligibility/precondition record, not an approval record.

## Open reproducibility checks

M2 currently has three unresolved reproducibility checks:

- **data** — complete design inputs, intermediate ranking outputs and raw validation data are not yet packaged;
- **code** — the original ADAPT implementation or a reproducible executable alternative has not been independently verified;
- **environment** — dependency versions, computational environment and protonation/modeling settings have not been reconstructed.

The recorded parameters, protocol and metrics are source-documented but have not been reproduced by FrontierLab.

## Planning obligations

Any later Stage 5 draft must retain these constraints:

1. **Design-input provenance** — record structural/design inputs and candidate-ranking provenance.
2. **Executable design stack** — identify ADAPT or a named reproducible alternative.
3. **Computational environment** — record dependencies and protonation/modeling settings.
4. **Matched-pH controls** — prespecify acidic vs physiological-pH comparisons and falsification conditions.
5. **Fab-level validation** — keep Fab readouts distinct from cell/full-antibody measurements.
6. **Orthogonal SPR** — where feasible, use SPR on monomeric Fab to separate intrinsic affinity from avidity/stoichiometry.
7. **Avidity/stoichiometry caveat** — do not overinterpret apparent cell-binding affinity mechanistically.
8. **Structure/search bias** — surface structural-model uncertainty and the histidine-centered search assumption; M1 remains a comparator for histidine-independent solutions.
9. **Replication/falsification** — include independent replication, stopping criteria and explicit falsification conditions.

## Evidence boundary

The packet distinguishes:

- **selected-method evidence**: `PMC6927761`;
- **all currently reviewed evidence available to planning**: `PMC4314675`, `PMC6927761`.

The Planning Agent, if later authorized, may use only reviewed evidence and must cite the selected method's source.

## Recorded builder

`python -m scripts.planning_readiness_recorded`

reconstructs the exact October 28 extraction, human review, reviewed continuation and Method Evaluation, then emits a readiness packet with **zero model calls**.

The recorded researcher-selection provenance remains separate from the canonical Method Evaluation so the latter continues to rebuild exactly from code.

## UI

When a current evaluation exists and no plan has been generated, Streamlit exposes:

**Planning readiness · pre-approval contract**

The panel shows the selected method, open reproducibility checks and all required obligations. It does not add a new authorization control.

The existing Stage 5 checkbox remains the only researcher authorization for draft planning.

## Scientific boundary

Planning readiness does not establish that M2 works, that the original experiment is reproducible, or that any proposed plan is safe/effective.

It only establishes that FrontierLab's current source-bound workflow state is internally eligible to ask the researcher for an explicit Stage 5 decision.

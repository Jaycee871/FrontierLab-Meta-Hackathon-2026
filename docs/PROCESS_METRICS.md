# Process metrics

FrontierLab exposes deterministic workflow metrics for audit and demo use. These metrics describe **process state**, not scientific accuracy.

## Metrics

### SCR — stage completion rate

SCR is the number of completed FrontierLab milestones divided by five:

1. research question defined;
2. evidence stage reached a terminal audit/review state;
3. at least one hypothesis exists;
4. a method evaluation exists;
5. a research plan exists.

A 100% SCR means the five workflow milestones exist. It does **not** mean the science is correct.

### Human-intervention event stream

New runs record four consequential researcher events in `Run.human_events`:

- `CLAIM_REVIEW_SAVED`;
- `METHOD_EVALUATION_SAVED`;
- `PLANNING_APPROVED`;
- `PLAN_STEP_APPROVED`.

Each event carries a UTC timestamp, event kind, bound artifact ID, actor label when available, note and `identity_verified=false`. The record therefore provides attributable process evidence without pretending that a typed reviewer name is authenticated identity.

Process metrics prefer this recorded event stream. Older runs that predate the event schema remain readable and fall back to the conservative artifact-derived observable count.

The UI continues to call the value **Observed human actions** rather than a fully verified HIC, because the event stream covers the four instrumented consequential actions rather than every possible researcher interaction.

### AERR — autonomous error recovery rate

AERR is reported only for the verified NVIDIA NIM research backend.

- If no runtime error occurred, AERR is **N/A** because the denominator is zero.
- If runtime errors occurred, the current no-retry policy means autonomous recoveries are zero, so AERR is 0% for that nonzero-error denominator.
- Other optional backends return NOT_APPLICABLE rather than inheriting NIM assumptions.

### Efficiency fields

For NIM receipts, the process-metrics layer sums:

- attempted calls;
- failed calls;
- prompt tokens;
- completion tokens;
- total tokens;
- recorded model-call elapsed seconds.

## Export

`frontierlab.reporting.export_json(run)` adds a top-level `process_metrics` object to the provenance JSON.

The Streamlit interface exposes the same values in **Process metrics · audit only**. The complete provenance JSON also contains the raw `human_events` array through `Run.as_dict()`.

## Scientific boundary

The metrics record workflow activity. They do not measure:

- claim entailment accuracy;
- hypothesis quality;
- wet-lab validity;
- clinical correctness;
- model generalization.

Every process-metrics export therefore records `scientific_accuracy_measured = false` and `scientific_validity_verified = false`.

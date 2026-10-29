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

### Human-intervention observable count

FrontierLab reports a conservative lower-bound count from artifacts already stored in a `Run`:

- reviewed claim decisions;
- saved method evaluation;
- generated plan as a proxy for explicit planning approval;
- approved evidence-graph plan steps.

The field is deliberately named **Observed human actions** in the UI. It is not a complete, identity-verified Human Intervention Count because the current data model does not store every human action as a normalized event.

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

The Streamlit interface exposes the same values in **Process metrics · audit only**.

## Scientific boundary

The metrics record workflow activity. They do not measure:

- claim entailment accuracy;
- hypothesis quality;
- wet-lab validity;
- clinical correctness;
- model generalization.

Every process-metrics export therefore records `scientific_accuracy_measured = false` and `scientific_validity_verified = false`.

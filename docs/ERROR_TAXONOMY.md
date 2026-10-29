# Error taxonomy

FrontierLab separates expected research-governance blocks from runtime failures.

## Categories

| Category | Meaning |
| --- | --- |
| `GOVERNANCE_GATE` | A deliberate human gate stopped progression, such as pending claim review. |
| `EVIDENCE_INSUFFICIENT` | The evidence set does not meet the minimum source/claim requirement. |
| `CITATION_OR_SOURCE_FAILURE` | A citation, source ID or source passage failed a deterministic check. |
| `RESOURCE_NOT_CONNECTED` | A required model/backend resource was not connected or enabled. |
| `MODEL_RUNTIME_FAILURE` | A recorded model request failed under the no-retry runtime policy. |
| `MODEL_OUTPUT_FAILURE` | Reserved for structured model-output failures that are explicitly recorded as such. |
| `CLAIM_REJECTED` | A rejected claim did not fit a more specific source/citation category. |
| `SCIENTIFIC_TENSION` | The evidence catalogue contains a detected directional conflict. This is not a software failure. |

## Aggregates

`classify_run(run)` reports:

- `non_runtime_blocks`: governance, evidence, citation/source and resource/setup blocks;
- `runtime_failures`: model runtime/output failures;
- `scientific_tensions`: evidence conflicts.

The UI currently retains the older label “Governance / evidence blocks” for compatibility, while the exported taxonomy also exposes the more precise `non_runtime_blocks` field. A later presentation-only cleanup can rename the UI label without changing the metric.

## Why the distinction matters

A mandatory human review is expected behavior. It must not be counted as a model crash.

Likewise, insufficient evidence is a research outcome, not necessarily a software defect. The taxonomy therefore supports process auditing without converting conservative stopping behavior into an artificial “error rate”.

## Export

The taxonomy is included inside `process_metrics.error_taxonomy` in the complete provenance JSON.

These counts describe pipeline events only. They do not measure scientific accuracy or model generalization.

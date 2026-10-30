# Trace Coverage — measured provenance metric

FrontierLab's Research Operating Interface uses **Trace Coverage** as a measured provenance metric.

It is not a model-accuracy score and it does not establish scientific truth.

## Why two coverage metrics are necessary

A research artifact can be traceable to a real source while its provenance path still contains an inference or disagreement.

FrontierLab therefore reports two separate values.

### Source Trace Coverage

> What fraction of downstream-eligible research artifacts can be followed to at least one known Paper node?

Headline scope:

- claims that passed the evidence gate;
- hypotheses;
- plan steps.

Claims rejected by the evidence gate remain visible as exclusions and are not silently added to or removed from the denominator.

### Strict Extracted Coverage

> What fraction of those same artifacts have a complete provenance path in which every reachable edge is EXTRACTED, every path reaches a Paper, and there are no unresolved source IDs or dead ends?

This is deliberately stricter than simple reachability.

EXTRACTED still means that the passage/source linkage was checked. It does **not** mean that semantic entailment or scientific correctness has been independently proven.

## Recorded M2 core measurement

The zero-call recorded M2 trace reconstruction currently measures:

| Metric | Result |
| --- | ---: |
| In-scope material artifacts | 4 |
| Reviewed claims | 2 |
| Hypotheses | 2 |
| Source-traceable artifacts | 4 / 4 |
| **Source Trace Coverage** | **100%** |
| Strict-EXTRACTED artifacts | 2 / 4 |
| **Strict Extracted Coverage** | **50%** |
| New model calls | 0 |
| Scientific accuracy measured | No |

The four in-scope artifacts are two reviewed claims and two hypotheses.

## Why strict coverage is 50%, not 100%

The result exposes a real provenance distinction in the recorded run.

For the PMC4314675 claim:

- the source and exact passage are real and traceable;
- the researcher later judged the specific claim **SUPPORTED**;
- the original Evidence Extraction Agent stance was **inconclusive**.

The Evidence Graph intentionally preserves that original model stance.

Its claim-to-passage edge therefore remains:

`CITES · AMBIGUOUS`

with the reason:

> Stance `inconclusive` does not decide the claim.

The hypothesis that depends on that claim inherits the same non-strict path.

Therefore:

- both the claim and hypothesis are still **source traceable**;
- neither is counted as **strict EXTRACTED**.

This is not repaired into 100% because doing so would erase a meaningful model-versus-researcher decision history.

The other reviewed claim/hypothesis path (PMC6927761) is fully EXTRACTED.

## Interpretation

A useful provenance system should be able to say:

> I know exactly where this came from, but I also know that the model and the later researcher judgment were not identical.

That is different from both:

- the source is missing; and
- the evidence chain is unambiguous.

Trace Coverage is intended to preserve that distinction.

## Implementation

- `frontierlab/traceability.py`
- `frontierlab/operating_status.py`
- `scripts/trace_coverage_recorded.py`

The Streamlit **Research Operating Interface · operational status** panel displays:

- next required stage;
- Source Trace Coverage;
- Strict Extracted Coverage;
- source-audit counts;
- recorded human events;
- governance status;
- maintainability status;
- provenance blockers when strict coverage is lower than source coverage.

The complete provenance export also embeds `research_operating_status`.

## Maintainability boundary

The current panel reports:

`REGRESSION_MONITORED_MANUAL_REPAIR`

FrontierLab has CI, centralized version metadata and an error taxonomy, but automatic repair and automatic environment rebuilding are **not implemented**.

## Metric boundary

Trace Coverage must always be reported with its denominator.

Avoid:

> FrontierLab has 100% traceability.

Prefer:

> In the recorded reviewed M2 core, 4/4 in-scope artifacts can be traced to a known paper (100% Source Trace Coverage), while 2/4 have a fully EXTRACTED provenance path (50% Strict Extracted Coverage).

This keeps the metric reproducible and prevents a small demonstration set from being mistaken for a general performance claim.
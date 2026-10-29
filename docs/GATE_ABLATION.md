# Gate ablation

FrontierLab treats "does governance help?" as an experiment rather than a slogan.

Two different comparisons are implemented because they answer different questions.

## 1. Recorded post-generation replay

This reuses the genuine 12-case Meta Muse Glimmer batch recorded on October 28, 2026.

No new model call is made.

The same fixed model outputs are passed through three policy layers:

```text
Arm A  fixed recorded model outputs
  ↓
Arm B  source-ID + verbatim-quote post-processing gate
  ↓
Arm C  source/quote gate + researcher review
```

This is a **post-generation gate ablation**. The original model prompt already requested evidence quotes, so it does not isolate the causal effect of quote-grounded prompting.

### Current recorded result

| Quantity | Result |
| --- | ---: |
| Cases | 12 |
| Model | Meta Muse Glimmer 30B |
| Recorded model calls reused | 1 joint-context call |
| New model calls for replay | 0 |
| Recorded tokens | 1,794 |
| Recorded model time | 11.168 s |
| Raw decisive outputs | 8 |
| Raw abstentions | 4 |
| Decisive outputs after source/quote gate | 8 |
| Abstentions after source/quote gate | 4 |
| New abstentions introduced by post gate | 0 |
| Surviving decisions requiring human review | 8 |
| Completed 12-case reviews | 0 |
| Accuracy reported | **No** |

All eight decisive outputs in this clean recorded batch already carried a source ID matching the fixed case and an anchored quote. Therefore the deterministic post-processing gate introduced zero additional abstentions.

That is a valid null effect for this particular batch. It does not show that the gate is unnecessary, because the prompt itself already asked the model to produce evidence quotes.

The public app computes this result from bundled records with `frontierlab.recorded_gate_ablation.run_recorded_pilot()`.

## 2. Controlled prompt-level ablation

A separate manual workflow is prepared for a stronger comparison:

```text
Same Glimmer model
Same 12 cases
Same source excerpts

Arm A: label-only instruction
Arm B: label + exact quote instruction → deterministic source/quote gate
Arm C: Arm B survivors → human review
```

The implementation is:

- `scripts/nim_gate_ablation_trial.py`
- `.github/workflows/nim-gate-ablation-trial.yml`

The workflow is manual (`workflow_dispatch`) and requires explicit NIM opt-in. It uses a hard `CallBudget(limit=2)` and no automatic retry.

The runner hashes the shared case/source payload and records both call receipts so the comparison can demonstrate that the model and cases were held fixed while the task instruction changed.

## Human review and accuracy boundary

The 12-case dataset contains provisional AI-authored reference labels, but FrontierLab never uses those labels as gold.

Researcher review and independent gold are intentionally separate concepts:

- a supplied researcher review can be used to measure how often a reviewer changes a surviving model decision;
- reviewer agreement is descriptive, not automatically "accuracy";
- accuracy is emitted only when a complete reference set is supplied **and** explicitly marked as independently verified.

Until then:

```text
scientific_accuracy_measured = false
accuracy_reportable = false
```

## Metrics

The ablation reports:

- decisive / abstained / pending counts and rates;
- quote-gate retention;
- new abstentions caused by the deterministic gate;
- prompt-induced label changes in the true A/B trial;
- post-gate changes;
- reviews required / completed;
- reviewer corrections to surviving decisions;
- token and latency provenance for recorded/live NIM calls.

## Interpretation

A useful outcome is not necessarily "the gate rejects more."

If a strong prompt already produces well-grounded outputs, a deterministic quote gate may have a zero incremental rejection rate while still providing an enforceable fail-closed boundary for malformed future outputs.

The experiment therefore separates:

1. model behavior under different instructions;
2. deterministic source/quote enforcement;
3. human scientific judgment.

None of those layers alone proves scientific truth.


## Completing Arm C in the public app

The literature-pilot panel now supports a source-bound review round trip:

1. download `frontierlab_real_excerpt_review.json`;
2. edit only each case's `label` and `rationale`;
3. enter a reviewer name in the app;
4. upload the edited JSON;
5. FrontierLab revalidates the fixed sources, case IDs and claim text;
6. a canonical packet is produced with UTC time, coverage and `independence_verified=false`;
7. Arm C is recomputed from those researcher labels with **zero new model calls**.

A completed researcher review can therefore measure reviewer corrections and intervention burden, but it still does not unlock an accuracy claim unless a separate independently verified reference set exists.

# Optional Liquid AI d1-2B Multimodal Evidence Gate

**Status:** software contract implemented; no d1-2B scientific inference has been executed in FrontierLab.

## Why this belongs in FrontierLab

FrontierLab's core Meta Muse Glimmer path remains responsible for skeptical synthesis and hypothesis generation. The optional Liquid AI d1-2B extension has a narrower role: inspect figure, table, document-image or video evidence and return typed decision signals that a researcher can review before the evidence is allowed to influence synthesis.

This avoids treating a small vision model as a general scientific reasoner.

## Model facts used by this integration

Liquid AI released d1-2B with the LFM3 family on October 27, 2026. The official model card describes it as a 1.92B-parameter decision model built on LFM3-VL-2B, with a 128K-token context and an LFM Open License v1.0. It accepts text/JSON plus pictures or video and returns typed answers with probabilities in a single forward pass rather than generated tokens.

The native local interface is:

```python
out = model.system_one(state, questions, media=[image])
```

Question types include yes/no probability (`noul`), choices, scores, text/number/date extraction and image boxes. The model card explicitly says decision thresholds should be calibrated on the user's own data.

Official sources:

- https://www.liquid.ai/blog/lfm3
- https://huggingface.co/LiquidAI/d1-2B

## FrontierLab contract

`frontierlab.multimodal_evidence.D1EvidenceGate` expects an already-loaded object exposing `system_one()`. The main application never downloads d1-2B automatically and `requirements.txt` is unchanged.

For a scientific claim and an image, FrontierLab asks five typed questions in one pass:

1. Is the image relevant to the claim?
2. Does the visible evidence support the claim?
3. Does the visible evidence contradict the claim?
4. Which image region is most relevant?
5. What visible short value/statistic/text span is most relevant?

The resulting record stores hashes of the question packet and model answers plus input-token usage. It always marks:

- `scientific_entailment_verified = false`
- `researcher_review_required = true`

Without a researcher-supplied calibrated threshold, probabilities remain unthresholded signals.

## Intended architecture

```text
Paper / PDF
   |
   +--> text/abstract ------------------> existing source + quote gate
   |
   +--> figure / table / image
              |
              v
       optional d1-2B gate
       - relevance P(yes)
       - support P(yes)
       - contradiction P(yes)
       - evidence region
       - visible value/span
              |
              v
       researcher review
              |
              v
       Meta Muse Glimmer
       Skeptic -> Hypothesis
```

The d1 signal cannot bypass human review or create a hypothesis directly.

## Why no automatic 0.5 support threshold

The model card uses a `found` convention for extraction/localization, but explicitly recommends calibrating decision thresholds on application data. FrontierLab therefore does not turn `P(supports) >= 0.5` into a scientific support label.

A future benchmark should calibrate thresholds on a small preregistered set of scientific figures/tables with blinded researcher labels, and report calibration error, abstention and false-support rates separately.

## Local execution boundary

FrontierLab does not add Transformers, Torch or the 2B checkpoint to the default installation. A user who intentionally runs the optional model should install the official-compatible runtime separately and load:

```python
from transformers import AutoModel
model = AutoModel.from_pretrained(
    "LiquidAI/d1-2B",
    trust_remote_code=True,
    dtype=...,
).to(device)
```

Then pass the loaded model into `D1EvidenceGate(model)`.

This is a supporting open-weight component. It does not replace Meta Muse Glimmer as the central model used for the Meta Global AI Developer Hackathon entry.

## Reproducibility

Run the offline contract check:

```bash
python -m scripts.d1_multimodal_preflight
```

and the normal test suite:

```bash
python -m pytest -q
```

The preflight makes zero network calls and downloads no model weights.

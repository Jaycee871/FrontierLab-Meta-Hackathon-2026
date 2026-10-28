# DetectorScope Explainability / Output Audit Lens

**Status:** optional software contract implemented; no real DetectorScope inference has been executed by FrontierLab.

## Why it joins

DetectorScope is a 2026 Google DeepMind + University of Pennsylvania research project for building **auditable AI-text detectors with sparse autoencoders**.

Unlike a black-box detector that only returns an AI score, a released DetectorScope model can return:

- a detector label;
- `p_ai`;
- logit and bias;
- active interpretable features;
- each feature's contribution / importance;
- optional token-level highlights showing where the feature activates.

Official sources:

- https://github.com/google-deepmind/detectorscope
- https://pypi.org/project/detectorscope/
- https://aclanthology.org/2026.emnlp-main.762/

The package installs as `pip install detectorscope`, and released detectors load through `AuditableDetector.from_pretrained(...)`.

## FrontierLab role

DetectorScope is assigned exactly one role:

**Explainability / Output Audit Lens**

It can inspect outputs from different FrontierLab workers and help compare linguistic signatures across model scales.

For example:

```text
Muse2-230M output ----\
Llama 3.1 8B output ---+--> DetectorScope --> feature contributions / highlights
Glimmer 30B output ----+
Spark output ----------/
```

This can support analysis of:

- detector probability as a diagnostic signal;
- number of active interpretable features;
- positive versus negative contribution mass;
- recurring feature descriptions across model families;
- how researcher editing changes detector features.

## It is not an AI-authorship judge

The DetectorScope authors explicitly warn that the released detectors make mistakes, including on human-written text, and that accuracy outside their training domains and generators is not established.

FrontierLab therefore rejects use for:

- academic-integrity or student-discipline decisions;
- hiring;
- publication decisions;
- authorship attribution;
- scientific-truth judgments.

A DetectorScope `p_ai` is a diagnostic model signal, not evidence that a person used AI.

## Detector variants

The project publishes:

- `liamdugan/detector-scope` — open-domain detector;
- `liamdugan/detector-scope-peer-review-gpt4o` — ML peer-review domain, human vs GPT-4o;
- `liamdugan/detector-scope-peer-review-llama` — ML peer-review domain, human vs Llama.

Each detector exposes interpretable sparse-autoencoder features and supports a `tau` threshold controlling the interpretability/accuracy tradeoff.

The default published `tau` is 0.85. Released heads are available from 0.00 to 0.95 in 0.05 increments. FrontierLab validates this grid rather than silently choosing an arbitrary threshold.

## Runtime boundary

The default FrontierLab installation remains unchanged.

`DetectorScopeAuditLens` accepts an already-loaded callable detector. It does not add DetectorScope, Gemma, SAE weights, PyTorch or model checkpoints to the default `requirements.txt`.

A normal optional runtime can load:

```python
from detectorscope import AuditableDetector

detector = AuditableDetector.from_pretrained(
    "liamdugan/detector-scope",
    tau=0.85,
)
lens = DetectorScopeAuditLens(
    detector,
    detector_id="liamdugan/detector-scope",
)
record = lens.inspect(model_output)
```

Every FrontierLab record is marked:

```text
diagnostic_only = true
individual_decision_forbidden = true
scientific_truth_verified = false
```

Raw input text is not copied into the audit record; only its SHA-256 hash is retained.

## Future model-scale audit

DetectorScope adds an orthogonal audit axis to the planned FrontierLab model-scale comparison:

```text
230M -> 8B -> 30B -> 816B
          |
          +--> reliability / abstention / citation checks
          |
          +--> DetectorScope linguistic-feature audit
```

The goal is not to optimize outputs to evade detectors. The goal is to understand which interpretable detector features recur across bounded scientific-writing outputs and how those features change with model scale and researcher editing.

Run the zero-network preflight:

```bash
python -m scripts.detectorscope_preflight
```

No detector or model is downloaded by that command.

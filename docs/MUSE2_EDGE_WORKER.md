# Muse2-230M Edge Structured Worker

**Status:** optional local software contract implemented; no real Muse2 inference has been executed in FrontierLab.

## Why it joins FrontierLab

`Muse-research/Muse2-230M` is deliberately assigned a small job.

The Muse Research model card describes the instruction-tuned model as a compact edge/on-device language model optimized for assistant-style chat, formatting and structured log-to-JSON extraction. It is English-only, approximately 230M parameters, uses an 8K default context with a documented 128K maximum, and is released under Apache-2.0.

The same model card explicitly warns that this model scale hallucinates facts readily, has no RLHF/DPO safety alignment, and is out of scope for factual-reliance, medical or safety-critical use.

Therefore FrontierLab uses it only as an **Edge Structured Worker**.

Official source:

- https://huggingface.co/Muse-research/Muse2-230M

## Allowed work

The adapter allows four tasks:

- metadata normalization;
- log-to-JSON extraction;
- schema formatting;
- lightweight routing.

Example:

```text
messy paper metadata / developer log
        |
        v
Muse2-230M edge worker
        |
        v
strict JSON
        |
        v
FrontierLab deterministic validation
        |
        v
Evidence / multimodal / reasoning layers
```

## Explicitly forbidden work

The edge worker cannot be used to produce scientific or clinical truth fields such as:

- supported / contradicted;
- entailment / truth;
- diagnosis / treatment;
- efficacy / safety;
- clinical decision.

Those fields are rejected before generation.

Muse2 does not decide whether a biomedical claim is true. It does not replace source matching, human claim review, d1 visual evidence inspection, Muse Glimmer or Muse Spark reasoning.

## Runtime boundary

The default FrontierLab installation remains unchanged.

Muse2's official repository uses its own from-scratch `muse` PyTorch package and tokenizer stack rather than a Transformers-native architecture. FrontierLab therefore does not add PyTorch, the `muse` package or the checkpoint to `requirements.txt`.

Instead, `Muse2EdgeWorker` accepts an already-loaded runtime exposing:

```python
runtime.complete(
    messages=[...],
    max_new_tokens=256,
    temperature=0.2,
    top_k=50,
)
```

This mirrors the low-temperature structured-output usage described by the model card while keeping model loading outside the core application.

## Provenance

Every successful preprocessing operation records:

- model and backend;
- preprocessing task;
- SHA-256 of input text;
- SHA-256 of requested schema;
- SHA-256 of validated output;
- elapsed time.

Raw text is not stored in the receipt.

Every receipt permanently states:

```text
scientific_entailment_verified = false
researcher_review_required_for_scientific_use = true
```

## Architecture role

```text
raw text / metadata / logs
        |
        v
Muse2-230M
edge formatting + JSON
        |
        v
deterministic schema validator
        |
        +--> d1-2B visual evidence signal (optional)
        |
        +--> Muse Glimmer verified reasoning
        |
        +--> Muse Spark frontier multimodal reasoning (optional)
        |
        v
human review + FrontierLab gates
```

Run the zero-network preflight:

```bash
python -m scripts.muse2_edge_preflight
```

No model weights are downloaded by that command.

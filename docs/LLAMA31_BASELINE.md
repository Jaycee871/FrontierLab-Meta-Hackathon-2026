# Meta Llama 3.1 8B Instruct — Local Baseline Worker

**Status:** optional software contract implemented; no new Llama 3.1 inference has been executed by FrontierLab.

## Why it joins

`meta-llama/Llama-3.1-8B-Instruct` fills the middle of FrontierLab's model-size spectrum.

Meta released Llama 3.1 on July 23, 2024. The 8B Instruct model is text-only, supports a 128K-token context, eight officially supported languages, Grouped-Query Attention, multilingual dialogue and tool-use-oriented workflows.

Official references:

- https://ai.meta.com/blog/meta-llama-3-1/
- https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct

FrontierLab does **not** add it because it is newer or stronger than Muse Glimmer. It joins as a mature, widely deployed medium-size baseline.

## Role

The intended role is:

**Local General-Purpose Baseline / Worker**

It can run the same structured `json(role, task, payload)` interface used by FrontierLab research agents, but every receipt is permanently marked:

```text
baseline_only = true
scientific_output_independently_verified = false
```

This makes it suitable for controlled A/B comparisons while keeping the verified Glimmer path distinct.

## Future scale-vs-reliability comparison

A useful controlled comparison is:

```text
Muse2-230M  -> edge structured preprocessing
Llama 3.1 8B -> local general-purpose baseline
Muse Glimmer 30B -> verified scientific reasoning backend
Muse Spark 816B -> frontier multimodal reasoning
```

Run the same bounded structured task and compare:

- JSON validity;
- abstention rate;
- citation-ID validity;
- exact quotation validity;
- researcher intervention rate;
- latency;
- input/output size or token usage.

The goal is not to prove that larger models are always better. It is to identify the smallest model that can reliably perform each bounded job.

## Runtime boundary

The default FrontierLab installation remains unchanged. No 8B checkpoint, Transformers runtime or GPU dependency is added to `requirements.txt`.

`Llama31BaselineClient` accepts an injected local runtime exposing:

```python
runtime.complete(
    messages=[...],
    max_new_tokens=1024,
    temperature=0.2,
    top_p=0.9,
)
```

This allows llama.cpp, Transformers or another local serving layer to be wrapped without coupling FrontierLab to one runtime.

## Scientific boundary

Llama 3.1 8B can participate in a controlled baseline version of evidence extraction, skeptical review or hypothesis formatting, but its output still goes through the same:

```text
source ID -> exact quote -> human review -> evaluation -> planning gate
```

It never receives authority to approve its own scientific output.

Run the zero-network preflight:

```bash
python -m scripts.llama31_baseline_preflight
```

No checkpoint is downloaded by that command.

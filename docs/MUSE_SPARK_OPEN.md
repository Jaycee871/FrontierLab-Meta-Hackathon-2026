# Meta Muse Spark Open — Frontier Multimodal Backend

**Status:** provider-neutral software adapter implemented; no hosted Muse Spark call has been executed by FrontierLab.

## Role in the architecture

Muse Spark Open is added as an optional **frontier multimodal Meta backend**, not as a replacement for the already verified Muse Glimmer path.

- **Muse Glimmer 30B** remains the recorded stable research backend.
- **Muse Spark Open** can use the same FrontierLab research governance through the existing `json(role, task, payload)` contract.
- Spark also exposes `multimodal_json(..., media=[...])` for image, audio and video evidence.
- **Liquid d1-2B** remains an optional lightweight typed evidence verifier; it is not a substitute for Spark or Glimmer.

## Official model facts

Meta describes Muse Spark Open as:

- 816B total parameters / 42B active parameters;
- sparse mixture-of-experts;
- 1,048,576-token context window;
- text, image, audio and video input with text output;
- open weights under the Muse Model License.

Meta's documentation says Muse Spark Open is not called through the Meta Model API. It can be self-hosted or called through a hosted inference provider.

Official references:

- https://dev.meta.ai/docs/muse-spark-open
- https://dev.meta.ai/docs/muse-spark-open/deploy
- https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B
- https://huggingface.co/blog/meta-muse-spark-open

## Hosted provider registry

FrontierLab currently records the model strings listed by Meta for:

| Provider | Model string |
| --- | --- |
| Together AI | `meta-models/muse-spark-open` |
| Fireworks AI | `accounts/fireworks/models/muse-spark-open` |

The core adapter does **not** contain a provider API key, endpoint or SDK. A provider-specific transport is injected by the caller.

This keeps the scientific workflow independent from the commercial inference host.

## Compatible research interface

The class `MuseSparkHostedClient` implements:

```python
client.json(role, task, payload)
```

so it can be used by FrontierLab's existing Evidence Extraction, Skeptic, Hypothesis, Method Evaluation and Planning code without changing those scientific gates.

It also implements:

```python
client.multimodal_json(
    "Multimodal Evidence Agent",
    task,
    payload,
    media=[
        {"type": "image", "source": image_ref, "mime_type": "image/png"},
        {"type": "video", "source": video_ref, "mime_type": "video/mp4"},
    ],
)
```

The transport receives provider-neutral content blocks and converts them into the provider's wire format.

## Safety and provenance boundaries

Every attempted call:

- consumes a process-local hard call budget;
- has no automatic retry;
- records provider, requested model, canonical Meta model, role, media types, timestamps, usage and input/output hashes;
- does **not** copy raw media references into the receipt;
- rejects non-JSON, duplicate-key, non-finite or incomplete results;
- rejects an unexpected model identity.

The model prompt explicitly treats source text and media as untrusted scientific data and forbids inventing papers, measurements or experimental execution.

These checks verify execution provenance. They do not verify scientific correctness.

## M2 use case

For the selected **M2 — Structure-based dual-pH histidine-scanning computational design**, a future Spark-enabled evidence path can combine:

```text
paper text + antibody/antigen structure figure + assay figure
        |
        v
Muse Spark Open multimodal reasoning
        |
        v
source / quotation / media evidence gates
        |
        v
researcher review
        |
        v
hypothesis + M2 evaluation + planning gate
```

Potential tasks include checking whether a figure actually shows the claimed pH-dependent effect, identifying which structure/assay panel is relevant, and reasoning over text plus visual evidence before a researcher approves downstream use.

## Execution boundary

FrontierLab does not attempt to load the 816B checkpoint into the public HF CPU Space.

No hosted Muse Spark API call has been executed by this integration. The adapter is deliberately provider-neutral until an explicitly authorized hosted transport and credentials are supplied.

Run the zero-network preflight:

```bash
python -m scripts.muse_spark_preflight
```

Then run the normal software suite:

```bash
python -m pytest -q
```

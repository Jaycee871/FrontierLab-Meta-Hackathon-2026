# Live Meta Muse via Hugging Face Inference Providers (v0.39)

Status: **implemented, no live result recorded yet.** All tests mock the OpenAI client; no live call was made while building this path.

## What it does

`frontierlab/hf_providers.py` adds the sidebar mode **Live Meta Muse (via Hugging Face)**. It calls Meta Muse models through the OpenAI-compatible Hugging Face router and plugs into the existing `json(role, task, payload)` contract used by the pipeline.

| Position | Model ID sent to the router | Provider | Timeout |
| --- | --- | --- | --- |
| Primary | `meta-models/Muse-Spark-Open-816B-A42B:baseten` | Baseten (pinned) | 60 s |
| Fallback | `meta-models/Muse-Glimmer-30B` | chosen by the router (Together, DeepInfra or Featherless AI) | 45 s |

- Router: `https://router.huggingface.co/v1` (`chat/completions`), per <https://huggingface.co/docs/inference-providers>. `model:provider` pins a provider; no suffix means the router's default `:fastest` policy.
- Fallback happens on any provider error, timeout, HTTP error, empty or truncated output (`finish_reason != "stop"`), unexpected reported model identity, or unparseable / non-object / duplicate-key JSON. If both fail, the step stops with a plain message that points to the recorded replay.
- Request: system + user message, `max_tokens=1536`, `temperature=0.2`, `stream=false`, OpenAI SDK `max_retries=0`.
- Roles: Evidence Extraction; after researcher claim review, Adversarial Skeptic and Hypothesis; then Method Evaluation suggestions and the approved draft plan through the same client.

## What it does not change

- Every extracted claim still passes `audit.validate_claims(..., require_quote=True)`: a 24–500-character verbatim excerpt of the **full** cited abstract. Abstracts sent to the model are truncated to a 3,000-character prefix, so any quote from the prefix is still checked against the full text.
- Human claim review, method selection and the Stage 5 planning approval are unchanged. A model output is only a proposal.
- The direct billed Meta Model API adapter (`frontierlab/meta.py`) stays off.

## Guards

- **Token**: read from the environment only, first non-empty of `HF_TOKEN`, `HF_INFERENCE_TOKEN`, `HUGGINGFACEHUB_API_TOKEN`. It is never logged, stored in provenance, exported or displayed. Without a token the mode is listed as unavailable with the reason.
- **Consent**: the Run button stays disabled until the visitor ticks *“This will make live calls to Meta Muse models via Hugging Face Inference Providers, billed to the project owner”*. Unticking it detaches the live client from all later steps.
- **Caps**: 6 attempts per browser session and a per-process daily cap (`FRONTIERLAB_HF_DAILY_CALL_CAP`, default 60, max 500, UTC day). Every attempt counts, including fallbacks. A capped request is never sent. These are app-side guards, not Hugging Face billing limits: also set a spending limit on the Hugging Face account.
- **Input**: at most 2 abstracts per run, each truncated to 3,000 characters; question truncated to 1,000; the whole prompt must be at most 16,000 characters or the step is rejected before any request.

## Receipts

Each attempt appends a receipt to `run.inference["receipts"]` (shown in *Model request receipts* and in the provenance export): role, chain position, requested model, router model string, provider requested, provider reported (from the `x-inference-provider` response header when present), reported model, model-identity check, start / finish timestamps (UTC), elapsed seconds, token usage, finish reason, input / output SHA-256, truncation flag, status (`JSON_OBJECT_RETURNED`, `FAILED_FALLBACK_NEXT`, `FAILED`) and, on failure, only the exception class and HTTP status. Prompt and output text are not stored in receipts.

## After deploying (owner checklist)

1. Space secret named `HF_TOKEN` (or one of the two alternatives) holding a fine-grained token with **Make calls to Inference Providers**. Restart the Space after adding it.
2. Open the Space, choose **Live Meta Muse (via Hugging Face)**, tick the consent box and run one small search (2 abstracts). Check the receipts show `meta-models/Muse-Spark-Open-816B-A42B` with `JSON_OBJECT_RETURNED`, or a Glimmer fallback.
3. Save that run's provenance JSON under `docs/runs/` before describing any live result.

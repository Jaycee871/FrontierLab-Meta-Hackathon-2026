# Cost-safe Meta Muse Glimmer execution

Status: 2026-10-27. Model adapter and scripts prepared, but real inference has NOT been tested. Offline mocks do not prove competition eligibility.

Official Meta GGUF checkpoint: https://huggingface.co/meta-models/Muse-Glimmer-30B-GGUF
Official llama.cpp instructions: https://dev.meta.ai/docs/muse-glimmer/llama-cpp
HF Spaces specifications: https://huggingface.co/docs/hub/spaces-overview

Hugging Face CPU Basic has 2 vCPUs, 16GB RAM and 50GB disk: not sufficient for the 16.8GB Glimmer checkpoint plus runtime memory. This CPU environment can run FrontierLab retrieval, auditing, and a small user interface. An upgraded CPU host with more than 24GB available RAM is only a candidate and may be slow; upgrades can charge fees and require explicit user permission. HF also states compute Space creation may require paid-plan eligibility; Static Spaces remain free.

Kaggle dual T4 offers two distinct VRAM pools and is a candidate for split-mode layer placement with llama.cpp, not a guarantee. Inspect your real Kaggle allocation before doing anything costly.

Resource-only audit from repo root:

    python -m scripts.muse_hardware_check

This does not download a checkpoint or allocate a GPU.

To actually load the model on a compatible, already-configured machine:
1. Install a CUDA-enabled llama.cpp build b10353 or newer (Kaggle GPU mode).
2. Check ample free disk and memory. Check GPU quota rules.
3. Make an explicit decision to download approximately 17GB.
4. From repo root:

    export FRONTIERLAB_DOWNLOAD_OK=YES
    bash scripts/start_muse_local.sh gpu

On a compatible large-RAM CPU host replace gpu with cpu. Model may still fail to load; inspect logs. No API key is supplied and no paid Meta Model API call is made.

The localhost-only adapter uses the local OpenAI-compatible llama.cpp REST server at 127.0.0.1:8080. It probes /v1/models and refuses Qwen or another model masquerading as a Meta inference backend. Never expose an unauthenticated model port publicly.

A Hugging Face Space cannot call Kaggle's local 127.0.0.1; cross-machine connectivity requires an intentionally configured and authenticated private connection, which is NOT part of this prototype.

To demonstrate true Meta model use for competition, record actual Muse Glimmer checkpoint version, positive local model identity check, real inference inputs and outputs, validated source IDs, constraints and limitations, and a live system demo. None of those real inference milestones are claimed yet.

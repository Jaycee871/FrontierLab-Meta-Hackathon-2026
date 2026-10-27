# Hugging Face PRO: FrontierLab CPU Basic Space setup

Prepared 2026-10-27. Status: repository template only. **No HF Space has been created or deployed** through this document, and no paid HF hardware has been authorized.

## What the user account screenshots show

Account: Jaycee766 · PRO.
- Private storage: 0 TB / 1 TB shown.
- Public storage: 0 TB / 11.2 TB shown. This is Hub storage, NOT live RAM or a free GPU balance.
- ZeroGPU: 0/40 min shown (included daily usage; resets based on first use).
- Inference usage: US$0.00 usage cost shown (this is not a guarantee of zero future charges).
- Egress: 807 kB / 100 TB shown for the current month.
- Rate limits: 2.5k Hub API, 12k Resolver, and 400 Page requests per 5-minute interval shown.

According to official Hugging Face documentation, CPU Basic provides 2 vCPUs, 16 GB of RAM, and 50 GB nonpersistent disk, at no hourly cost; PRO permits users to create Docker/Gradio compute Spaces. Paid GPU upgrades incur usage charges separate from the PRO subscription.

## Recommended first Space: public CPU-only research interface

On Hugging Face, log in as Jaycee766 and open https://huggingface.co/new-space

1. Owner: Jaycee766
2. Space name: FrontierLab-Meta-Hackathon-2026
3. Visibility: Public (assuming public competition demonstration is desired)
4. SDK: Docker
5. Hardware: CPU Basic (FREE). **Do not select CPU Upgrade, T4, L4, Inference Endpoint, paid GPUs, or pay-as-you-go.**
6. Create Space. On the Files tab at the repository root, add a file named Dockerfile using the exact contents of deploy/hf-space/Dockerfile in GitHub.
7. Optional: replace the auto-generated README.md with deploy/hf-space/README.md, which provides correct SDK metadata (docker, port 7860).
8. The Space should build automatically and present a Streamlit interface. Check the Build logs for errors. Do not call it deployed unless the app is publicly reachable.

The Dockerfile fetches the public GitHub source during build. It uses Python 3.11, installs required dependencies, and serves Streamlit on port 7860; **it includes no API credentials and no Meta API calls**.

If Space fails, check its hardware type, logs, and Streamlit port; do not upgrade to paid hardware to mask a software error.

## Separate experimental ZeroGPU Space (future milestone)

PRO is entitled to 40 included minutes of ZeroGPU per day and can host up to ten ZeroGPU Spaces under their own account; official current backing GPUs have 48 GB (large) or 96 GB (xlarge) VRAM. ZeroGPU is currently **Gradio-only**, not Docker/Streamlit, and uses time-limited dynamic GPU allocation. It is not a 40-minute persistent GPU VM.

Only after testing model-loading feasibility and the appropriate Gradio/ZeroGPU compatibility would it make sense to create a second Space for Muse Glimmer. 48GB VRAM is a reason to test, not proof that llama.cpp / custom runtime works under ZeroGPU. Additional usage beyond included quota can draw from prepaid credits at US$1 per 10 minutes. Monitor HF Billing; do not prepay or approve upgrades without user consent.

Current proposal:
- Space A: Docker, CPU Basic, FrontierLab front-end + retrieval/audit demo.
- Space B (later): Gradio, ZeroGPU, isolated Meta open-weight inference experiment if supported.
- Kaggle: offline experimental GPU benchmarking, subject to the user's quota.

Do not expose the GitHub HF_TOKEN1 secret to either public Space or its logs. Creating a Space manually does not require adding that secret. The Space will not automatically share memory or connect to an independent Kaggle localhost server.

Official references:
- https://huggingface.co/docs/hub/spaces-overview
- https://huggingface.co/docs/hub/spaces-sdks-docker
- https://huggingface.co/docs/hub/spaces-zerogpu
- https://huggingface.co/docs/hub/billing

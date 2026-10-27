# FrontierLab | Evidence-Grounded Scientific Research Agents

**Meta Global AI Developer Hackathon 2026** · **Indie Developer Track** · **Push the Frontier**

**Status: Day-1 prototype, v0.1.1. Paid Meta API is intentionally DISABLED at the user's request.** All competition code in this repository began on 2026-10-27. The application is an early research workflow; no claim of validated scientific inference or live Meta API success has been made.

## What we are building

FrontierLab transforms a scientific question into an evidence-gathering and hypothesis workflow with explicit, auditable decisions. It is not a general chatbot or an AI medical advisor.

Research question → Europe PMC abstract retrieval → (planned) **Meta open-weight** Evidence Extraction Agent → deterministic citation / conflict audit → skeptical review → hypothesis generation → human approval gate → research planning → provenance JSON export. **Only synthetic audit and metadata retrieval have been verified; the new local Muse Glimmer adapter is implemented but actual model inference is not yet tested.**

The pipeline deliberately preserves conflicting claims and may abstain. Two distinct source IDs with verified-format claims are required before hypotheses; source-ID validation by itself does NOT verify scientific truth. Researchers must inspect full source papers, protocols, context, and all results before acting on any output.

## Run the prototype locally

1. Install Python 3.10 or later.
2. Install dependencies: python -m pip install -r requirements.txt
3. Start the web UI: streamlit run app.py
4. Run Synthetic audit demonstration first (no key and no external calls).
5. For authentic paper abstracts (no model reasoning), choose Live Europe PMC metadata.
6. **No Meta Model API calls are made by this UI.** We are assessing a non-billed, open-weight Muse Glimmer backend; see [resource assessment](docs/RESOURCE_STRATEGY.md).

For Windows, run run_windows.bat after installing Python. Never commit local keys or send them to chat.

## Three modes and precise limits

- **Synthetic audit demonstration:** Invented, explicitly labeled SYNTHETIC:A/B/C publications and hand-authored claims. Shows deterministic conflict handling and researcher approval. It makes no Meta API call. Synthetic papers are not scientific citations.
- **Live Europe PMC without API key:** Retrieves source metadata and abstracts only. It will NOT fake a successful model result.
- **Future Meta open-weight stage:** Muse Glimmer, subject to GPU feasibility tests. A local-only model client can now be selected in the UI, but its real inference and end-to-end reliability remain UNVERIFIED.

The historical paid Meta API client is disabled and raises an exception on use; paid calls are not available in this prototype. Official Muse Glimmer open-weight model is preferred for Hackathon eligibility without Meta Model API billing.

## Tests and guardrails

Run: python -m pip install -r requirements-dev.txt
Then: python -m pytest -q

The eight original offline tests cover: fictional disagreement and labeling, human approval enforcement, fabricated citation rejection, unsupported hypothesis blocking, JSON handling, missing API credentials, a mocked role-by-role inference flow, and abstention when only one source has verified-format claims.

This source-ID gate is an integrity check, not independent fact verification. Conflict matching relies on model-supplied claim keys, which are fallible. The research interface is NOT for diagnosis, therapy, medical advice, or automated wet-lab decisions. The UI and outputs are prototypes, not validated products.

## Hackathon submission transparency

- Keep the repository PUBLIC and all newly built work easy to distinguish.
- All synthetic content is explicitly labeled, never portrayed as real science or proof of actual Meta API use.
- Competition demo requirement from the participant guide: 3-minute video highlighting features actually created during the competition.
- Submission deadline in the guide: Nov 4, 2026 at 9:00 PM U.S. Eastern. Check organizer updates before submitting.
- Meta Model API credits must be claimed separately; do not make chargeable calls before your free credit balance is applied.
- Hosted deployment, real model testing, robust evaluation and experimental scientific validation remain milestones.
- **Additional quantitative tests:** deterministic inverse-variance fixed-effect heterogeneity module cross-checked against a live Wolfram computation with clearly fictitious data.
- **Kaggle hardware inspection:** `python scripts/kaggle_gpu_check.py` from inside a GPU-enabled Kaggle Notebook. No model download or paid API access.
- See [docs/RESOURCE_STRATEGY.md](docs/RESOURCE_STRATEGY.md) for resources tested and hardware feasibility caveats.

## Technical stack

Python, Streamlit, Europe PMC REST API, Meta Model API, OpenAI-compatible Python SDK, pytest, GitHub Actions.

Official links:
- Meta API: https://dev.meta.ai/
- Hackathon: https://cerebralvalley.ai/e/meta-ai-developer-hackathon

Project idea originally submitted by Pack Kwan Low (Jaycee). This repository is the new competition-period implementation of that idea.


## 🦞 OpenClaw / NVIDIA OpenShell isolation research

Added an optional offline permission-gate demonstration and host-only OpenShell launch/inspection/probe scripts. **Actual NVIDIA runtime has not been deployed or validated.** No Meta paid API calls, secrets or private repository mounts are involved. See [docs/OPENCLAW_OPENSHELL.md](docs/OPENCLAW_OPENSHELL.md). Run the clearly simulated demo with `python -m scripts.lobster_guard_demo`.


## Optional real Meta open-weight inference (NO paid Meta API)

A new localhost-only Muse Glimmer adapter is available as an experimental third UI mode. This connects to an already-running local llama.cpp server, and never to Meta Model API. The old paid API client is intentionally blocked at initialization. See [deployment notes](docs/META_OPENWEIGHT_HF_CPU.md) and the hardware checker at scripts/muse_hardware_check.py. The HF free CPU tier is too small for the 17GB model; use it for the frontend and research tools. No real checkpoint or GPU test has been completed.


## HF PRO Spaces deployment template

For a no-hourly-cost public CPU Basic Docker demonstration, see [HF PRO setup](docs/HF_PRO_SETUP.md), [Space Dockerfile](deploy/hf-space/Dockerfile) and [Space README](deploy/hf-space/README.md). This has not been deployed to Hugging Face yet. The free CPU Space runs metadata retrieval and synthetic audits, not actual Meta Glimmer inference. An experimental Gradio ZeroGPU model Space would be a separate project.


## Springer Nature Open Access connector (optional)

A new read-only client for Springer Nature's Open Access API returns DOI-grounded publication metadata and available abstracts. It is covered by offline tests and will not call the API automatically. The user's GitHub secret named Open_Access_API is accessible only to explicitly configured GitHub Actions workflows, not to Hugging Face Spaces. The optional [manual connection check](.github/workflows/springer-oa-check.yml) makes one low-volume query, without printing the secret. See [configuration and licensing notes](docs/SPRINGER_NATURE_OA.md). Real credential-backed connectivity has not yet been verified.


## Three-source metadata discovery (Springer Nature Meta API v2)

The GitHub secret Meta_API_Key is wired into a manual-only Springer Nature Meta API v2 smoke test. A separate, opt-in three-source workflow retrieves small sets from Europe PMC, Springer Nature Meta API and Springer Nature Open Access API and merges by normalized DOI. The merged catalog preserves source names and records missing abstracts without inventing evidence. The public HF Space does not inherit GitHub Secrets, so it still runs its pre-existing Europe PMC interface. No paid Meta model API is used. See docs/SPRINGER_NATURE_META.md.


## v0.6 · Claim-to-evidence audit / optional NVIDIA-hosted Muse Glimmer

The existing synthetic research demo now includes a separate 10-case, HAND-LABELED, FICTIONAL claim-to-passage benchmark: source IDs, exact quote anchors, and comparison with human-authored labels are separate checks. No semantic truth can be inferred from quote matches. The optional NVIDIA NIM adapter is isolated from Meta Platforms' billed Model API, off by default, and can only be exercised in a manual GitHub Actions workflow with synthetic input. See [full experiment protocol](docs/CLAIM_VERIFICATION_AND_NIM.md). An HF Space rebuild is required for new UI code to appear.


## OpenCode optional developer assistant

We include an approval-first [OpenCode project config](opencode.json), a read-only scientific review subagent, and [setup / security caveats](docs/OPENCODE_DEVELOPER.md). This is LOCAL developer tooling only, not a deployed scientific agent or sandbox. Nothing runs automatically or uses GitHub Secrets. The public HF Space is unchanged.

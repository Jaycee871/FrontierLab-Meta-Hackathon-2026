# FrontierLab | Evidence-Grounded Scientific Research Agents

**Meta Global AI Developer Hackathon 2026** · **Indie Developer Track** · **Push the Frontier**

**Status: Day-1 prototype, v0.1.1. Paid Meta API is intentionally DISABLED at the user's request.** All competition code in this repository began on 2026-10-27. The application is an early research workflow; no claim of validated scientific inference or live Meta API success has been made.

## What we are building

FrontierLab transforms a scientific question into an evidence-gathering and hypothesis workflow with explicit, auditable decisions. It is not a general chatbot or an AI medical advisor.

Research question → Europe PMC abstract retrieval → (planned) **Meta open-weight** Evidence Extraction Agent → deterministic citation / conflict audit → skeptical review → hypothesis generation → human approval gate → research planning → provenance JSON export. **Only the clearly synthetic audit and metadata retrieval are currently active; model inference is not yet connected.**

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
- **Future Meta open-weight stage:** Muse Glimmer, subject to GPU feasibility tests. All real model-based extraction, skeptical review and planning remain UNIMPLEMENTED in the current Streamlit UI.

A legacy Meta API client exists in source for traceability but is intentionally NOT called by the current application; do not use it for this run. Official Muse Glimmer open-weight model is preferred for Hackathon eligibility without Meta Model API billing.

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

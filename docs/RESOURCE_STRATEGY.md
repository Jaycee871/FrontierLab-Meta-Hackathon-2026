# FrontierLab: connected research tooling & cost-safe implementation

Updated **2026-10-29 (Asia/Taipei)**. This document describes the resource and execution boundary of the current project. It is not, by itself, proof of Hackathon submission or scientific validity.

## 1. Current shipped baseline

**Main branch:** `0adcfb37e11290c30a4649c8b7712419502a4a52` (v0.25).

Verified on that source snapshot:

- GitHub Actions deployment run [40740516474](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40740516474) completed with **289 passing tests**.
- The same run uploaded the exact main source snapshot to the existing Hugging Face Space and recorded Space commit `429f4accad2d141aadde6c1eaba1224771f90158`.
- The shipped main code includes the v0.25 provenance-tagged evidence graph and EXTRACTED-only plan-step path gate.
- Stage 5 Planning remains unapproved and ungenerated for the real M2 path.

Two later changes are still **pending PRs**, not shipped main:

- [PR #9](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/pull/9): docs-only agentic-AI landscape and Level 1 self-assessment.
- [PR #10](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/pull/10): evidence-graph schema v2 integrity hardening; its branch reports **304 passing tests**.

Do not cite PR-only behavior as a main-branch capability until the owner merges it.

## 2. Meta-model policy

The project does **not** use the paid Meta Model API. That remains an explicit owner choice.

The verified Meta path uses **Meta Muse Glimmer 30B through NVIDIA NIM**. Dated records include:

1. one synthetic smoke call;
2. one strict-JSON published-excerpt check;
3. one 12-case joint-context batch;
4. two real Evidence Extraction Agent calls over frozen published excerpts;
5. a researcher-completed claim review;
6. one bounded two-call continuation: Adversarial Skeptic Agent → Hypothesis Agent.

The continuation stopped before Method Evaluation and Planning by design. See:

- [NIM backend](NIM_RESEARCH_BACKEND.md)
- [structured Meta runs](META_STRUCTURED_RUNS.md)
- [reviewed continuation summary](runs/nim_reviewed_continuation_20261028.json)

The project must keep distinguishing:

- **model returned a response**
- **software/provenance checks passed**
- **researcher reviewed a claim**
- **scientific truth / reproducibility was independently verified**

These are different statements.

## 3. Model/resource matrix

| Component | Role | Execution status | Default-install impact |
| --- | --- | --- | --- |
| **Muse Glimmer 30B / NVIDIA NIM** | Verified research reasoning backend | **Real recorded inference exists** | No credential bundled; live calls require explicit owner opt-in |
| **Muse Spark Open** | Optional frontier multimodal Meta backend | Adapter + tests only; **no live Spark inference claimed** | No 816B checkpoint, provider SDK or secret in default install |
| **Liquid d1-2B** | Optional typed multimodal evidence signal | Contract + fake-model tests only | No model download or Torch/Transformers dependency added |
| **Meta Llama 3.1 8B Instruct** | Optional local general-purpose baseline | Contract + tests only | No 8B checkpoint or GPU runtime added |
| **Muse2-230M** | Optional edge structured worker | Contract + tests only | No checkpoint or `muse` runtime added |
| **DetectorScope** | Optional explainability/output-audit lens | Contract + tests only | No Gemma/SAE weights or DetectorScope dependency added |
| **BioNeMo / Boltz-2** | Optional scientific-computation preflight | Offline request/response-shape checks only | No hosted scientific computation claimed |

The design principle is **capability separation**: a larger model never bypasses source checks, human review, stale-state invalidation, method selection or planning approval.

## 4. Cost and retry policy

Normal software tests make no model calls.

Live model scripts and clients use explicit opt-ins and hard process-local budgets. The verified Glimmer research path deliberately has **no automatic retries**. A failed model call is recorded as a failure and stops rather than silently spending more tokens.

This no-retry policy is also why FrontierLab should not describe itself as Level 2+ autonomous agent behavior. Any future retry/self-repair capability would be an intentional product/research decision, not a cleanup change.

Before any new hosted inference:

- confirm the exact model/provider;
- confirm the intended call budget;
- confirm that credentials stay in server-side secrets;
- preserve model identity, timing, token usage and input/output hashes;
- avoid storing credentials, auth headers or hidden reasoning;
- keep the result clearly separated from independent scientific validation.

## 5. Hugging Face Space boundary

The public Space is a **CPU Basic frontend / retrieval / audit surface**.

It is not the place to self-host Muse Glimmer 30B, Muse Spark Open 816B, Llama 3.1 8B or DetectorScope/Gemma checkpoints.

The manual deployment workflow:

1. runs the main software test suite;
2. uploads a fixed source snapshot rather than cloning moving `main` in Docker;
3. records source SHA and uploaded asset hashes;
4. uses the existing HF token only inside the GitHub deployment runner;
5. transfers no NVIDIA credential or NIM opt-in.

The latest source upload recorded by GitHub Actions used main SHA `0adcfb3`. Earlier v0.16 runtime/health verification is retained in [the deployment receipt](runs/hf_deployment_20261028.json). The 2026-10-29 source upload itself should not be described as post-build runtime verification unless the Space runtime is checked separately.

## 6. Kaggle / local GPU boundary

Do not assume two GPUs behave like one pooled VRAM device. Hardware must be inspected before downloading large checkpoints or consuming quota.

The original local Glimmer path remains experimental; the verified competition evidence currently comes from NVIDIA NIM, not from a successful Kaggle self-hosted 30B run.

Do not make Kaggle availability a submission blocker.

## 7. Literature and connected research services

### Europe PMC / Springer Nature

The app uses Europe PMC for live metadata/abstract retrieval. A separate workflow also supports Springer Nature Meta API v2 and Open Access API. Retrieval proves that a source record was found; it does not establish entailment.

### Undermind

Undermind was used during research exploration to locate pH-switchable protein-binding literature. The standalone Streamlit Space has no Undermind credential or automatic Undermind integration.

### Wolfram

A deterministic quantitative heterogeneity example was cross-checked with Wolfram during development using explicitly fictional inputs. It is a software demonstration, not biological evidence.

## 8. Evidence and provenance boundary

Main v0.25 includes a provenance graph:

```text
Paper <- Passage <- Claim <- Hypothesis <- PlanStep
```

Edges are tagged EXTRACTED, INFERRED or AMBIGUOUS. A plan step is approvable only when its reachable evidence path is EXTRACTED.

Important: **EXTRACTED means the passage/ID linkage was found and checked. It does not prove semantic entailment.**

The graph is a traceability aid, not a replacement for researcher review.

PR #10 proposes additional integrity binding (schema v2). Until merged, cite it only as pending work.

## 9. Current highest-value validation milestones

1. **Owner-review open PRs #9 and #10.** Merge only if their claims and implementation are acceptable; otherwise revise or close them.
2. **Complete Stage 5 deliberately.** M2 is selected, but a real plan should be generated only after explicit researcher approval.
3. **Run the controlled gate ablation.** Same model and cases: no gate vs source/quote gate vs source/quote + human review. Report abstention and intervention separately.
4. **Optional one-case Spark demo.** If authorized hosted access is available, one bounded M2 structure/assay multimodal case is enough; do not make it a blocker.
5. **Record the three-minute demo.** The story should show a genuine model trace plus a visible human/evidence gate, not only a happy-path UI.
6. **Complete formal submission.** Repository publication and a public Space are not the submission itself.

## 10. Submission-time principle

A transparent partial prototype is preferable to a false end-to-end success claim.

For every demo statement, ask:

> Is this **software-verified**, **model-executed**, **researcher-reviewed**, or **scientifically validated**?

Use the narrowest true label.

# FrontierLab
### Evidence-grounded scientific research agents

**Meta Global AI Developer Hackathon 2026 · Indie Developer Track · Push the Frontier**

FrontierLab helps researchers turn a scientific question into a testable hypothesis and a reviewable research plan. Its initial focus is biomedical research: collect literature, inspect supporting and conflicting evidence, examine uncertainty, and let the researcher intervene before moving forward.

**Current codebase: v0.19 prototype · Hosted interface: v0.16 · Status reviewed: October 28, 2026 (Asia/Taipei)**

The evidence retrieval and audit components have working software and recorded tests. **One genuine Meta Muse Glimmer inference through NVIDIA NIM succeeded on a synthetic prompt**; the [run receipt](docs/runs/meta_nim_smoke_20261028.json) records the answer, model identity, timing and token use. A single published-excerpt JSON check, a 12-case joint-context batch and a two-call core extraction have also completed; see [structured run records](docs/META_STRUCTURED_RUNS.md) and the [NIM research backend](docs/NIM_RESEARCH_BACKEND.md). Both extracted core claims now have explicit researcher SUPPORTED judgments. A genuine human-reviewed Meta continuation has completed through the Skeptic and Hypothesis stages. The researcher then selected **M2 — Structure-based dual-pH histidine-scanning computational design** as the primary method, with M1 retained as a comparator. The canonical method evaluation is source-bound and passes the Planning eligibility check. Planning remains intentionally unapproved and incomplete. Paid Meta Model API access is disabled.

[Original project charter](docs/ORIGINAL_PROJECT_CHARTER.md) · [Final sprint plan](docs/HACKATHON_FINAL_SPRINT.md) · [Changelog](CHANGELOG.md) · [Test workflow](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/workflows/tests.yml)

## The research workflow

| Stage | Researcher-facing goal | Current implementation |
| --- | --- | --- |
| **1. Research** | Define the scientific question, scope and assumptions. | Question and literature-query inputs in Streamlit. |
| **2. Evidence** | Retrieve papers and inspect citation-linked claims, quotations and disagreement. | Europe PMC retrieval; separate three-source discovery workflow; source and quotation checks. |
| **3. Hypothesis** | Propose falsifiable hypotheses grounded in reviewed evidence. | **Real reviewed continuation completed:** two Meta Muse Glimmer calls ran after human review, producing two citation-linked hypotheses and a skeptical uncertainty analysis; execution boundary validated. |
| **4. Evaluation** | Compare candidate methods, reproducibility conditions and uncertainty. | **Completed researcher decision:** M2 selected; M1 retained as comparator. Canonical evaluation is bound to the exact live hypothesis trace and passes `require_evaluation()`; open reproducibility checks remain for data, code and environment. |
| **5. Planning** | Approve a draft with controls, measurements and falsification criteria. | Requires a current method evaluation and explicit approval; exports the selected method, rationale, unresolved checks and draft controls/metrics/replication/falsification. Live inference remains unverified. |

Four principles guide the workflow: **transparent evidence, reproducibility, uncertainty analysis and meaningful researcher intervention**. BioNeMo and the Research Failure Lab support these stages.

## What is working today?

| Component | Verified status | Scope |
| --- | --- | --- |
| **Literature discovery** | Recorded three-source run succeeded. | Europe PMC, Springer Nature Meta API v2 and Springer Nature Open Access API each returned two records: six total, four with abstracts. The Streamlit retrieval interface currently uses Europe PMC. |
| **Evidence checks** | Implemented and covered by offline tests. | Source-ID validation and a contiguous, verbatim 24–500-character quotation from the cited abstract; invalid claims are rejected. |
| **Human claim review** | Implemented; both recorded core claims explicitly reviewed SUPPORTED by Jaycee871. | Every accepted claim must be reviewed, with at least two distinct papers judged supportive before synthesis resumes. Reviews bind to source snapshots and the research question. |
| **Method evaluation** | Implemented with offline and Streamlit interaction tests. | Researcher-assessed candidate dossiers and optional local-model proposals; documented materials are not claimed to have been executed. [Protocol](docs/METHOD_EVALUATION.md). |
| **Audit trail** | Implemented. | Source records, claim checks, review judgments, workflow decisions and draft outputs can be exported as JSON. |
| **Software checks** | **224 tests passed in GitHub CI** for the current codebase, including exact live-trace method-evaluation reconstruction and Planning-gate eligibility. | Tests cover deterministic rules, parsers, adapters and mocked or fictional scenarios; this count is not a model-accuracy score. |
| **Meta model inference** | **Recorded smoke, JSON, 12-case, core extraction and reviewed continuation runs.** | Run [40574846326](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40574846326) executed exactly two additional Muse Glimmer roles after human review: Skeptic and Hypothesis. Both returned validated JSON; two citation-linked hypotheses survived audit. [Summary](docs/runs/nim_reviewed_continuation_20261028.json) · [handoff](docs/runs/nim_method_handoff_20261028.json). |
| **Hosted interface** | **v0.16 deployed and verified RUNNING on CPU Basic.** | Runtime revision, health endpoint and rendered source marker checked; both supplied claim judgments and rationales are visible. NIM is still owner-disabled on HF. [Space](https://huggingface.co/spaces/Jaycee766/FrontierLab-Meta-Hackathon-2026) · [Deployment receipt](docs/runs/hf_deployment_20261028.json). |
| **BioNeMo computation** | Offline preflight only. | Boltz-2 request preparation and response-format checks; no hosted scientific computation has run. |

Evidence: [three-source discovery run](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40519989268), [171-test run](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40560343730), and [recorded NVIDIA trial](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40562188386).

## Run locally

Requires **Python 3.10+**.

```bash
git clone https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026.git
cd FrontierLab-Meta-Hackathon-2026
python -m pip install -r requirements.txt
streamlit run app.py
```

On Windows, `run_windows.bat` is also available after installing dependencies.

Choose a mode in the sidebar:

| Mode | What it does | Requirements |
| --- | --- | --- |
| **Synthetic audit demonstration** | Uses labeled, hand-authored fictional publications to show disagreement, approval and planning. | No keys, model or external calls. |
| **Live Europe PMC metadata (no model calls)** | Retrieves real publication metadata and available abstracts. | Internet connection; no API key. |
| **Live Europe PMC + local Meta model** | Attempts model-based claim extraction and the human-reviewed synthesis workflow. | An actual Muse Glimmer checkpoint served by llama.cpp on the same host at `127.0.0.1:8080`. Experimental and unverified. |
| **Live Europe PMC + Meta via NVIDIA** | Reuses one NIM research client across extraction, reviewed synthesis, method proposals and planning. | Owner-enabled backend, server-side credential, explicit question/abstract transfer consent and shared process call cap. [Setup](docs/NIM_RESEARCH_BACKEND.md). |

The CPU Space hosts the interface and retrieval/audit tools; it does not have a loaded Muse Glimmer model. A remote Kaggle server is not reachable through the Space's localhost address. See [local inference notes](docs/META_OPENWEIGHT_HF_CPU.md) and [Space setup](docs/HF_PRO_SETUP.md).

The NVIDIA client now has an optional, explicitly enabled Streamlit research backend. See [owner configuration and call limits](docs/NIM_RESEARCH_BACKEND.md). One explicitly authorized, branch-scoped GitHub-triggered smoke test has completed; its one-shot trigger is now disabled. The default-branch trial workflow remains manual. GitHub Secrets are not automatically available inside Hugging Face Spaces. See [resource strategy](docs/RESOURCE_STRATEGY.md).

## How evidence reaches a research plan

1. Retrieve publications and their available abstracts.
2. Ask the connected model to propose claims with source IDs and exact quotations.
3. Reject invalid source references and quotations that do not match the cited abstract.
4. Stop for human judgments: **supported, contradicted or insufficient**.
5. Resume skeptical review and hypothesis generation only after all claims are reviewed and at least two distinct sources are human-supported.
6. Compare candidate methods, document reproducibility gaps and uncertainty, then select a method with a rationale or defer.
7. Require a current saved evaluation and explicit approval before drafting a cited research plan.
8. Export the evidence, evaluation and decision trail for inspection.

Changed source records or a changed question invalidate the previous review. Insufficient evidence stops synthesis.

**A matching quotation establishes that text exists in a source; it does not establish that the text supports the model's interpretation.** Human labels are review decisions, not independently adjudicated scientific ground truth. Conflict detection also depends on fallible model-supplied claim keys. Outputs are research drafts, with no validated clinical or wet-lab execution capability.

See [method evaluation and planning](docs/METHOD_EVALUATION.md), [verbatim evidence gate](docs/VERBATIM_EVIDENCE_GATE.md) and [human review protocol](docs/HUMAN_REVIEW_GATE.md).

## Supporting experiments and tools

| Module | Purpose | Current boundary |
| --- | --- | --- |
| [Real literature pilot](docs/REAL_LITERATURE_PILOT.md) | Twelve excerpt-level cases from four published papers; blank reviewer packets and imported-output comparison. | One real Meta batch is recorded; reference labels are AI-authored proposals awaiting researcher review. No accuracy claim. |
| [Claim-to-passage audit](docs/CLAIM_VERIFICATION_AND_NIM.md) | Separate source identity, quotation matching and semantic-label agreement. | Ten hand-authored fictional cases; not measured Meta model performance. |
| [Research Failure Lab](docs/RESEARCH_FAILURE_LAB.md) | Exercise stale reviews, misattributed quotations, spoofed tool results and other handoff failures. | Twelve fictional software scenarios; not a biological or human-participant study. |
| [BioNeMo tools](docs/BIONEMO_SCIENCE_TOOLS.md) | Prepare an optional scientific-computation step within Evaluation. | Protein-only Boltz-2 preflight and response-shape checks. ProteinMPNN, RFdiffusion and OpenFold3 are listed but not connected. |
| Quantitative heterogeneity example | Illustrate disagreement using inverse-variance estimates, Cochran Q and I². | Fictional inputs; Python results cross-checked with Wolfram during development. |
| [OpenCode](docs/OPENCODE_DEVELOPER.md) / [OpenShell exploration](docs/OPENCLAW_OPENSHELL.md) | Support local development and isolation experiments. | OpenCode configuration and simulated permission checks; real OpenShell runtime isolation unverified. |
| [Legacy Facebook Research MUSE](docs/LEGACY_MUSE_MULTILINGUAL.md) | Historical cross-lingual embedding alignment reference for a future multilingual Evidence layer. | Archived upstream project, distinct from Meta Muse Glimmer; no upstream code/data bundled or executed. |

These modules support the five-stage product. Their offline results do not demonstrate successful Meta inference or scientific discovery.

**Muse naming note:** the archived Facebook Research **MUSE** project (Multilingual Unsupervised and Supervised Embeddings) is a separate legacy research project from **Meta Muse Glimmer 30B**. FrontierLab tracks the former only as an optional multilingual-evidence reference; it is not part of the current runtime. See [the MUSE reference note](docs/LEGACY_MUSE_MULTILINGUAL.md).

## Tests and reproducibility

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Optional offline demonstrations:

```bash
python -m scripts.research_failure_lab
python -m scripts.bionemo_preflight
python -m scripts.lobster_guard_demo
```

The **224-test** suite includes Streamlit interaction, NIM backend reuse, consent revocation, bounded extraction, recorded-review rebinding, reviewed-continuation boundaries, continuation-artifact provenance validation, exact live-hypothesis method-evaluation reconstruction and single/batch output validation tests. GitHub Actions run [40578886168](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40578886168) passed all 224 tests. Synthetic fixtures are labeled explicitly; genuine model outputs require separate, dated execution records.

## Repository guide

| Path | Contents |
| --- | --- |
| `app.py` | Streamlit interface, claim review and export controls. |
| `frontierlab/` | Retrieval, audit rules, review packets, model adapters, research pipeline and supporting experiments. |
| `scripts/` | Offline demonstrations, hardware checks and opt-in connection trials. |
| `tests/` | Offline software tests. |
| `deploy/hf-space/` | Docker Space deployment template. |
| `docs/` | Project charter, protocols, resource notes and sprint plan. |
| `.github/workflows/` | Automated tests and manual connection workflows. |
| [CHANGELOG.md](CHANGELOG.md) | Version-by-version development history. |

Publisher connector details: [Springer Nature Meta API](docs/SPRINGER_NATURE_META.md) · [Springer Nature Open Access](docs/SPRINGER_NATURE_OA.md).

Some setup documents preserve earlier implementation snapshots. Use the dated status and linked execution records above when assessing what has actually been verified.

## Next milestones

1. **Stage 5 remains human-gated:** M2 is now formally selected in [the canonical method evaluation](docs/runs/method_evaluation_20261028.json), with the human rationale preserved separately in [the researcher selection record](docs/runs/researcher_method_selection_20261028.json). Planning has not been approved or generated.
2. **Complete one live five-stage case:** question, literature, human-reviewed claims, hypothesis, evaluation and approved plan.
3. **Run a controlled comparison:** use the same model and cases to compare no gate, source/quote checks, and checks plus human review; report abstention and intervention separately.
4. **Record the public demo:** v0.16 is deployed with a checked revision; record an approximately three-minute demonstration of actual behavior.
5. **Submit the entry:** verify the participant portal's current requirements and complete the formal submission.

See the [final sprint plan](docs/HACKATHON_FINAL_SPRINT.md). Repository publication and a hosted demo do not establish formal submission.

## Project and competition

Created by **Pack Kwan Low (Jaycee)**. Competition-period implementation began on **October 27, 2026**.

- [Meta Global AI Developer Hackathon](https://cerebralvalley.ai/e/meta-ai-developer-hackathon)
- [Meta developer platform](https://dev.meta.ai/)
- [Original project charter](docs/ORIGINAL_PROJECT_CHARTER.md)


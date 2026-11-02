# FrontierLab — submission copy

This file contains reusable public-facing copy. Update only claims that have actually changed.

## Submission at a glance

| Field | Value |
| --- | --- |
| Project | FrontierLab — evidence-grounded, human-gated multi-agent AI for scientific research |
| Event / track / theme | Meta Global AI Developer Hackathon 2026 · Indie Developer Track · Push the Frontier |
| Representative / author | Pack Kwan Low (Jaycee) · GitHub [Jaycee871](https://github.com/Jaycee871) · Hugging Face [Jaycee766](https://huggingface.co/Jaycee766) |
| Team members | Solo — Pack Kwan Low (Jaycee), Indie Developer track |
| Code repository | https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026 (MIT License) |
| Live demo (HF Space) | https://huggingface.co/spaces/Jaycee766/FrontierLab-Meta-Hackathon-2026 · direct app: https://jaycee766-frontierlab-meta-hackathon-2026.hf.space |
| Demo video | [Demo video (3 min)](https://youtu.be/d3VaysvMFuA) (YouTube, unlisted; follows [DEMO_VIDEO_SCRIPT.md](DEMO_VIDEO_SCRIPT.md)) |
| Version | v0.40 on main (`6f0f7d2`), deployed to the Space (Space commit `94bc1eb3…`) |
| Submission deadline | 2026-11-04 21:00 ET = 2026-11-05 10:00 Asia/Taipei (recheck the participant portal) |

## One-line description

**FrontierLab is an evidence-grounded, human-gated scientific research pipeline that uses Meta models to turn literature into reviewable hypotheses and plans without hiding the evidence, uncertainty or researcher decisions in between.**

## Short description

FrontierLab uses Meta Muse models — Muse Spark Open (primary) and Muse Glimmer 30B (fallback) through Hugging Face Inference Providers, plus recorded Muse Glimmer 30B runs through NVIDIA NIM — inside a five-stage scientific workflow: Research → Evidence → Hypothesis → Evaluation → Planning. Model claims must cite exact source passages, critical transitions require researcher review, and evidence/process provenance are exported separately. The system is designed to make scientific AI more auditable rather than more theatrically autonomous.

## Project description

Scientific language models can cite a real paper while still overstating what the source supports. FrontierLab addresses that failure mode by treating literature-to-plan reasoning as an auditable process instead of a single generation step.

A Meta Muse Glimmer 30B backend proposes source-linked claims, receives adversarial critique and produces falsifiable hypotheses. Deterministic source/quote checks reject unanchored claims, while explicit researcher gates control semantic review, method selection and planning authorization. A provenance-tagged Evidence Graph traces scientific artifacts back to source passages; a separate Trajectory Audit Graph records model calls, human interventions, rejected claims and process failures without treating those events as scientific evidence.

The current biomedical demonstration uses published pH-dependent antibody-engineering literature. The researcher selected a structure-based dual-pH design route, while FrontierLab carries unresolved reproducibility checks and orthogonal-validation requirements into a pre-planning contract. Planning remains deliberately human-authorized.

## Impact

**Who it is for.** Biomedical researchers who use language models to read literature, the PIs and reviewers who must sign off on what those models produce, and the research-integrity, journal and funder staff who increasingly have to ask "where did this AI-assisted claim come from, and who approved it?"

**The problem it addresses.** A model can cite a real paper and still assert something the paper does not support. In biomedical work that error is not cosmetic: an unsupported claim about binding, safety or mechanism can steer which experiment gets funded or run. At the same time, work such as Paper2Agent (Miao et al., *Nature* 2026, cited prior work) shows that papers and their code/data can become operable agents. Once research artefacts become agents, the open question is no longer only "can the model answer?" but "can anyone reproduce, trace and govern what the agent did?"

**What FrontierLab changes, concretely and checkably.**

- **Claims are bound to verbatim evidence.** A model claim that does not cite a retrieved source ID with a contiguous 24–500-character quotation from that source is rejected before synthesis. Quote presence is then separately reviewed by a human, because a matching quote is not proof of support.
- **Provenance becomes a number a reviewer can recompute.** On the recorded, researcher-reviewed real M2 case (two published abstracts; real Meta Muse Glimmer 30B outputs recorded 2026-10-28, Asia/Taipei), the app recomputes from the files in `docs/runs/`: **100% source trace coverage (4/4 artifacts reach a known paper), 50% strict EXTRACTED coverage (2/4 have an all-EXTRACTED path), 9 planning obligations carried into Stage 5, and 0 model calls to replay**. The 50% is not hidden or "fixed": it preserves a real model/researcher provenance disagreement on PMC4314675. These are provenance metrics on a very small sample, not accuracy.
- **Reproducibility does not require trust, keys or money.** Anyone can open the public Space and replay the real case with no API key and no model call; tampered recorded files or a selection that would authorize planning fail closed.
- **Governance is enforced, not described.** Claim review, method selection and Stage 5 planning authorization are explicit researcher actions bound to content hashes. In the recorded case the researcher selected M2, yet planning remains **not approved**: readiness carries open data/code/environment checks and obligations such as monomeric-Fab SPR, avidity/stoichiometry handling, search-bias disclosure, replication and falsification.
- **Maintainability is measured, not assumed.** A scheduled Maintenance Canary re-runs the full regression suite and compares the environment with a human-accepted baseline. On the v0.40 main merge (run 41408148311) all 407 tests passed and the canary reported `HEALTHY`, while the advisory proposal correctly flagged `DRIFT_REVIEW_REQUIRED` because `requirements.txt` changed — detection plus human review, with automatic repair, commit, merge and deploy disabled.

**Why it matters beyond this demo.** The five-stage contract, the evidence gate and the provenance/trajectory graphs are domain-agnostic; the pH-dependent antibody-engineering case is the first worked domain. The broader contribution is Pack Kwan Low's Information Management extension — maintainability, provenance and research governance as the three pillars for managing paper-derived agents as research infrastructure — and the Research Operating Interface that reports those pillars as operational status. FrontierLab also proposes a concrete field list for an Agent Availability statement; the Agent Availability concept itself was anticipated by the Paper2Agent authors.

**What we do not claim.** No scientific-accuracy score, no independently adjudicated gold standard, no wet-lab or clinical validation, and no recorded result yet from the live Hugging Face Muse path. The impact claimed is narrower and verifiable: model-assisted scientific steps become inspectable, challengeable and reproducible.

## Why this fits Push the Frontier

FrontierLab applies Meta models to the scientific-research process itself: evidence interpretation, skeptical reasoning, hypothesis generation and experiment-planning preparation.

The project does not define progress as "more autonomy." Its technical ambition is to make increasingly capable scientific agents inspectable enough that a researcher can see:

- what source supports a claim;
- what the model inferred rather than extracted;
- what the researcher changed or approved;
- which reproducibility gaps remain;
- why a later scientific action was allowed or blocked.

That is a path toward useful scientific agency without turning uncertainty into invisible automation.

## Technical implementation

Core implementation:

- Python + Streamlit;
- Europe PMC literature retrieval;
- Meta Muse Spark Open (primary) and Muse Glimmer 30B (automatic fallback) through the Hugging Face Inference Providers router for the live path (v0.39, reasoning-budget fix v0.40);
- Meta Muse Glimmer 30B through NVIDIA NIM for the recorded model-backed research runs;
- zero-call recorded replay of the real reviewed M2 case;
- strict structured JSON contracts;
- deterministic source-ID and verbatim-passage gates;
- source-bound human review;
- adversarial Skeptic and Hypothesis agents;
- researcher-owned Method Evaluation;
- explicit Stage 5 Planning authorization;
- Evidence Graph schema v2 with source fingerprints and content-bound step approvals;
- normalized human-intervention events;
- process metrics and error taxonomy;
- separate Trajectory Audit Graph;
- recorded gate-ablation tooling;
- source-bound 12-case review workspace;
- deterministic M2 planning-readiness contract;
- scheduled Maintenance Canary with advisory, human-gated repair proposals.

Optional adapters for Muse Spark Open, Llama 3.1 8B, Muse2-230M, Liquid d1-2B and DetectorScope are intentionally separated from the verified Glimmer path.

## Built with Meta

| Model ID | Reached through | What it does in FrontierLab | Status |
| --- | --- | --- | --- |
| `meta-models/Muse-Spark-Open-816B-A42B` | Hugging Face Inference Providers router (`https://router.huggingface.co/v1`, OpenAI-compatible), provider `baseten` | **Primary** live model for Evidence Extraction, then (after researcher claim review) Adversarial Skeptic and Hypothesis; also Method Evaluation suggestions and the approved draft plan | Implemented in v0.39 (`frontierlab/hf_providers.py`), reasoning-budget fix in v0.40; **live extractions recorded**: 2026-11-01 locally (`docs/runs/hf_muse_live_extraction_20261101.json`: Baseten, 7.99 s, 4,287 tokens, paper MED:42959777 (BIGH3), 2 claims, both quotes verified) and 2026-11-02 on the deployed Space (`docs/runs/space_live_muse_20261102.md`: Baseten, 23.07 s, 4,713 tokens, same paper, 2 claims, 0 rejected) |
| `meta-models/Muse-Glimmer-30B` | Same router, provider chosen automatically (Together, DeepInfra or Featherless AI) | **Automatic fallback** when Muse Spark Open returns a provider error, times out or gives invalid output | Implemented in v0.39; not invoked in the recorded live run (the primary succeeded), so **no live fallback result recorded yet** |
| `meta/muse-glimmer-30b` (Muse Glimmer 30B) | NVIDIA NIM | Earlier recorded real runs on 2026-10-28 (Asia/Taipei): smoke test, strict JSON, 12-case pilot batch, 2 Evidence Extraction calls and the reviewed Skeptic → Hypothesis continuation; these drive the zero-call recorded replay | Recorded (`docs/runs/*_20261028.json`) |

Guards on the live path: explicit per-session consent, a 6-call per-session cap and a per-process daily cap (`FRONTIERLAB_HF_DAILY_CALL_CAP`, default 60) that count every attempt including fallbacks, strict timeouts (90 s primary / 75 s fallback) with no SDK retries, `max_tokens=8192` (both Muse models are reasoning models and hidden reasoning tokens count against `max_tokens`; v0.39's 1,536 was used up by reasoning), temperature 0.2, at most two abstracts truncated to 3,000 characters, and a receipt per call (model ID, provider when reported, timestamps, token usage, latency, status) in the provenance export. Model outputs never bypass the fail-closed verbatim evidence gate or the human review gates. The direct billed Meta Model API adapter remains off.

## Meta-model usage that is genuinely demonstrated

The repository preserves several dated genuine Meta Muse Glimmer / NVIDIA NIM executions, including:

- a smoke/identity check;
- strict structured output;
- a 12-case published-excerpt batch;
- two Evidence Extraction Agent calls on the core biomedical case;
- a human-reviewed two-call continuation: Adversarial Skeptic Agent → Hypothesis Agent.

These are model-execution records, not claims of scientific accuracy.

The live Hugging Face Inference Providers path also has one recorded run ([`docs/runs/hf_muse_live_extraction_20261101.json`](runs/hf_muse_live_extraction_20261101.json), 2026-11-01 23:18 Asia/Taipei, run locally on the v0.40 code): one Evidence Extraction call to `meta-models/Muse-Spark-Open-816B-A42B` via Baseten through HF Inference Providers, 7.99 s, 4,287 tokens (810 prompt + 3,477 completion, of which 3,182 reasoning), `finish_reason="stop"`, model identity matched. On paper MED:42959777 (BIGH3, pH-dependent antibody engineering) it returned 2 claims and both evidence quotes passed the verbatim quote gate. With a single source the pipeline correctly stopped at `INSUFFICIENT_EVIDENCE` before hypothesis generation; researcher review of the claims is pending.

On the deployed Space (v0.40, Space commit `94bc1eb3…`) a live run was then verified through the browser UI on 2026-11-02 (about 16:13 Asia/Taipei; [`docs/runs/space_live_muse_20261102.md`](runs/space_live_muse_20261102.md) with [screenshot](runs/space_live_muse_20261102.png), transcribed from the UI receipt panel, not an exported receipt file): query `EXT_ID:42959777 AND SRC:MED`, 1 abstract, one call to Muse Spark Open via Baseten (model identity matched, fallback not used), 23.07 s, 4,713 tokens (810 prompt + 3,903 completion, of which 3,578 reasoning), `finish_reason=stop`, 2 claims both `supports`, 0 conflicts, 0 rejected, decision `INSUFFICIENT_EVIDENCE` (single source), 0 runtime failures. As with the local run, the quotes are checked by passage grounding only (verbatim match against the abstract); semantic entailment is not verified.

## Current evaluation story

Software verification and scientific evaluation are reported separately.

Current software baseline:

- v0.40 on main (merge `6f0f7d2`, PR #37);
- **407 software tests passed** after merge (GitHub Actions run 41408148161);
- matched main Maintenance Canary run 41408148311 is **HEALTHY** (407 tests passed); its advisory proposal is **DRIFT_REVIEW_REQUIRED / HEALTHY_DRIFT** because the `requirements.txt` hash differs from the accepted Nov 1 baseline (v0.38–v0.39 dependency changes). Accepting a new baseline is a human decision;
- automatic repair, dependency/code edits, commit, merge and deploy remain disabled;
- v0.40 is the deployed HF Space baseline: source `6f0f7d2…` → Space commit `94bc1eb3…` (run 41408148915, 407 tests, receipt `HF_SOURCE_COMMITTED_BUILD_PENDING`; a read-only check of the public Space API on 2026-11-02 showed runtime `RUNNING` and a served `deployment.json` with `version: v0.40` and that source SHA). Any later merge needs one more manual deploy for exact Space/main parity;
- no normal test invokes a model.

Recorded 12-case Glimmer gate replay:

- 12 cases;
- 8 decisive outputs;
- 4 abstentions;
- all 8 decisive outputs already had anchored source quotes;
- deterministic post-processing gate introduced 0 additional abstentions;
- researcher review / independent gold are separate;
- no accuracy is claimed.

The repository also includes a manual same-model/same-cases two-call prompt-ablation workflow. It must not be described as executed until an actual run record exists.

## What is working today

- real literature retrieval;
- genuine recorded Meta inference;
- source/quote validation;
- source-bound human review;
- reviewed Skeptic/Hypothesis continuation;
- researcher Method Evaluation with M2 selected;
- evidence and trajectory provenance;
- measured Trace Coverage (recorded reviewed M2 core: 4/4 source-traceable; 2/4 fully EXTRACTED);
- Research Operating Interface operational status;
- scheduled dependency/environment Maintenance Canary with provenance capture and quarantine-on-failure;
- process metrics/error taxonomy;
- gate-ablation replay;
- 12-case review packet round trip;
- M2 planning readiness.

## Deployment state

Latest deployed baseline: **v0.40**. v0.40 main source `6f0f7d2431548621c3f2481939823058d2b9a72d` (merge of PR #37) was uploaded by run [41408148915](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/41408148915) (2026-11-02 15:43 Asia/Taipei) to HF Space commit `94bc1eb3cf8d216c17573fe958fa2ec01bef885d` after **407 software tests passed**. The receipt reported `HF_SOURCE_COMMITTED_BUILD_PENDING`; a later read-only check of the public Space API (2026-11-02, Asia/Taipei) showed runtime stage `RUNNING` and a served `deployment.json` with `version: v0.40` and that source SHA. A live Muse run on the deployed Space was then verified through the browser UI (2026-11-02, about 16:13 Asia/Taipei): the sidebar lists **Live Meta Muse (via Hugging Face)** as available, and one Muse Spark Open call via Baseten returned 2 passage-grounded claims on MED:42959777 (record: [`runs/space_live_muse_20261102.md`](runs/space_live_muse_20261102.md)). Any later merge (including this docs change) changes the GitHub revision and should be followed by one final deploy if exact Space/main source parity is required.

## What remains deliberately incomplete

- the 12-case benchmark does not yet have an independently verified gold standard;
- the manual two-call prompt-level ablation should be called "prepared" until executed;
- M2 data/code/environment reproducibility checks remain open;
- Stage 5 Planning is not approved or generated unless the researcher explicitly authorizes it;
- no wet-lab experiment has been executed or scientifically validated by FrontierLab;
- optional Spark/d1/Llama/Muse2/DetectorScope adapters do not imply live model runs; the live Hugging Face Muse path has two recorded single-paper Muse Spark Open extractions (one local, one on the deployed Space; passage grounding only, researcher review pending) and no recorded Muse Glimmer fallback result; it is not an accuracy evaluation.

## Autonomy statement

FrontierLab is a **Level 1 Assisted Pipeline by design**.

Models fill bounded research roles. Code and the researcher control transitions. The verified NIM path has no automatic retries or autonomous repair loop. FrontierLab should not be described as a closed-loop autonomous scientist.

## Suggested final sentence

**The goal is not to remove the scientist from the loop; it is to make every model-assisted scientific step strong enough to inspect, challenge and reproduce.**


## Information Management extension

Beyond the hackathon prototype, FrontierLab develops a research direction from Information Management: once papers, code, data and methods become operable agents, the next problem is how to manage them as research infrastructure.

The extension has three pillars:

- **Maintainability:** detect dependency/tool breakage, run regression tests, attempt bounded rebuild/repair, and revalidate before a repaired component returns to trusted use.
- **Provenance:** preserve an inspectable chain from source/data through tool/model/version/parameters/human actions to the resulting scientific artefact.
- **Governance:** define permissions, approval boundaries, sensitive-data access, audit responsibilities and accountability for agent-assisted research.

The current FrontierLab prototype now implements substantial provenance/human-governance controls plus two bounded maintainability layers: a scheduled dependency/environment canary with regression testing, fingerprints and quarantine-on-failure, followed by an advisory repair proposal that compares against a human-controlled healthy baseline. The proposal can recommend bounded remediation and re-validation steps but cannot edit code/dependencies, commit, merge or deploy. Autonomous repair/rebuild, institutional role-based access control and patient-data governance remain future research.

This three-pillar framework is a FrontierLab / Pack Kwan Low extension inspired by the shift from static papers to operable research agents; it is not presented as a result already established by Paper2Agent.

FrontierLab also proposes studying an **Agent Availability** reporting statement—analogous in spirit to Data Availability and Code Availability. The Paper2Agent authors anticipated such an “agent availability” section; FrontierLab's contribution is a concrete field list disclosing the agent version, represented artefacts, validation status, permissions, provenance and maintenance state. This is not a current journal standard.

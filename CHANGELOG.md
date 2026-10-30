## 2026-10-30 · Research Operating Interface Traditional Chinese companion — docs only

- Added `docs/RESEARCH_OPERATING_INTERFACE.zh-TW.md`, a Traditional Chinese write-up of the Research Operating Interface concept, the three Information Management aspects, the Agent Availability idea and the five research directions.
- Every section is labelled 【文獻】 (from the cited literature), 【作者前瞻】 (the source authors' forward-looking proposal, not an announced policy) or 【延伸觀點】 (the author's own Information Management extension, not a paper-validated conclusion).
- The mock-up figures “12 source audits” and “98% trace coverage” are marked 【示意數字】 wherever they appear: illustrative only, not measured. They are kept separate from the measured v0.36 Trace Coverage values (100% source / 50% strict on 4 artifacts).
- The closing comparison with current FrontierLab lists only capabilities found in the code and keeps the Level 1 Assisted Pipeline framing.
- Full bibliographic details for AlphaGenome, Scanpy and TISSUE are left as a stated to-do rather than filled in.
- README documentation index links the new document.
- No code, test, dependency or central version changed.

## 2026-10-30 · v0.37 — Maintainability canary and quarantine policy

- Added `frontierlab/maintenance.py` to create deterministic maintenance-health records containing requirements hashes, tracked package versions, Python version, dependency fingerprint and software regression outcome.
- Added `scripts/maintenance_canary.py` and a GitHub Actions **Maintenance canary** that runs manually, on relevant code/dependency changes, and daily at 02:17 UTC.
- The canary installs the currently allowed dependency range, runs the full regression suite, preserves `pytest.log`, emits `maintenance_health.json`, uploads both as a 30-day artifact, and fails the workflow when regression tests fail.
- Failure policy is **QUARANTINE_REQUIRED**. Automatic repair, environment rebuild, commit and merge are explicitly disabled; human approval is required before promotion.
- First executed canary: run 41064072834, artifact 12980538164, status **HEALTHY**, with **361 tests passed**.
- Final v0.37 validation canary: run **41064836504**, artifact **12982122350**, status **HEALTHY**, Python 3.11.17, Streamlit 1.66.1, Requests 2.34.2, OpenAI 2.54.0, Pytest 9.2.0, dependency fingerprint `ac61d837d7b2c80e5f0e6e3cb1fe6a0f5cb42705a52dba18fa2dee71f68d4b34`, **361 tests passed**.
- Research Operating Interface now reports maintainability as **CANARY_MONITORED_MANUAL_REPAIR**. The last GitHub canary result is not embedded into the app runtime, avoiding a stale-status claim.
- Updated maintainability benchmark / Research Operating Interface documentation and added a dedicated Maintenance Canary document.
- No autonomous repair, code modification, model call or scientific-validity claim was added.

## 2026-10-30 · v0.36 — Measured Trace Coverage and Research Operating Status

- Added `frontierlab/traceability.py` with two distinct provenance metrics: Source Trace Coverage and Strict Extracted Coverage.
- Headline scope includes evidence-gate-passed claims, hypotheses and plan steps; rejected claims remain visible as exclusions rather than distorting the denominator.
- Added `frontierlab/operating_status.py` to aggregate current activity, active sources, source audit, traceability, governance and maintainability state without exposing private chain-of-thought.
- Streamlit now exposes **Research Operating Interface · operational status**, including provenance blockers whenever source reachability exceeds strict EXTRACTED coverage.
- The complete provenance export now embeds `research_operating_status`.
- Added a zero-call recorded M2 trace reconstruction. Measured result: **4/4 source-traceable artifacts (100%) and 2/4 fully EXTRACTED artifacts (50%)**.
- The 50% strict result is intentional: the PMC4314675 claim/hypothesis path preserves the original model stance `inconclusive` even though later researcher review marked the claim SUPPORTED, so that path remains AMBIGUOUS.
- Added `docs/TRACE_COVERAGE.md` and updated the Research Operating Interface documentation.
- Maintainability status remains regression-monitored/manual-repair; automatic repair and environment rebuilding are not implemented.
- No new model call, scientific-accuracy claim or Stage 5 authorization was added.

## 2026-10-30 · Information Management research extension — docs only

- Added a FrontierLab Information Management extension authored as a project research direction rather than a claim from Paper2Agent.
- Formalized three management pillars for operable scientific agents: **maintainability, provenance and governance**.
- Added the **Research Operating Interface** concept: Paper / Code / Data plus MCP-style tool/resource/prompt integration under Evidence Trace, Governance and Maintainability controls.
- Distinguished current prototype capabilities from future work: FrontierLab already implements substantial provenance/human-governance machinery, while autonomous repair/rebuild, institutional RBAC and sensitive-data policy enforcement remain future research.
- Added a proposed **Agent Availability statement** template covering agent identity, represented artefacts, validation, provenance, governance and maintenance. It is explicitly marked as a forward-looking proposal, not an existing journal standard.
- Clarified that mock-up figures such as “98% trace coverage” must not be presented as measured results unless a real claim-set metric exists.
- No code, model call, scientific gate or central version changed.

## 2026-10-30 · Submission/demo package — docs only

- Added a ~3-minute demo runbook that distinguishes genuine recorded Meta inference, deterministic replay, researcher review and unexecuted optional experiments.
- Added reusable public submission copy aligned to the Indie Developer / Push the Frontier story and current v0.35 shipped boundaries.
- Added a release checklist covering repository freeze, manual HF deployment, runtime verification, demo checks, optional gate-ablation/review work, Stage 5 status and authenticated portal submission.
- Rechecked the public Meta and Cerebral Valley event pages: project submissions remain due November 4, 2026 at 9:00 PM ET; public pages do not expose every logged-in final-submission field.
- No code, model call, scientific gate or central version changed.

## 2026-10-29 · v0.35 — M2 Stage-5 planning-readiness contract

- Added `frontierlab/planning_readiness.py`, a deterministic pre-planning contract that calls `require_evaluation()` and refuses stale/changed method evaluations.
- The recorded M2 packet preserves exact context/evaluation IDs, reviewed source IDs, citation-linked hypotheses and the selected-method evidence set.
- M2's unresolved reproducibility checks are carried forward explicitly: **data, code and environment**.
- Nine planning obligations are recorded, including design-input provenance, executable design stack, environment/protonation settings, matched-pH controls, Fab-level validation, monomeric-Fab SPR where feasible, avidity/stoichiometry caveats, histidine-search/structure bias, replication and falsification.
- The readiness packet explicitly records `planning_approved=false`, `model_call_authorized=false`, `planning_model_called=false` and `plan_generated=false`.
- Added `scripts/planning_readiness_recorded.py` to rebuild the exact recorded M2 context with zero model calls.
- Streamlit now shows **Planning readiness · pre-approval contract** before the existing Stage 5 authorization checkbox. No new approval control was added.
- Feature/UI branch CI passed **348 tests** before final documentation synchronization.
- No Planning Agent call, experiment execution or scientific-validity claim was added.

## 2026-10-29 · v0.34 — Source-bound 12-case researcher review workspace

- Added `frontierlab/pilot_review.py` to canonicalize researcher-edited literature-pilot review packets against the fixed dataset and source snapshot.
- Completed judgments require a nonempty reviewer label and an 8+ character rationale; modified source text, source IDs or claims are rejected.
- Canonical packets record UTC time, review coverage and `independence_verified=false`. Researcher labels remain process evidence, not independent scientific gold.
- The recorded gate-ablation replay can now consume validated in-memory review labels and complete Arm C without rerunning Meta Muse Glimmer.
- The Streamlit literature-pilot panel adds a reviewer-name field and JSON uploader. Uploaded packets are validated, Arm C is recomputed immediately, and a canonical source-bound review JSON can be downloaded.
- Added regression tests; the feature branch passed **341 tests** before the v0.34 documentation/version sync.
- No model call, automatic retry or scientific-accuracy claim was added.

## 2026-10-29 · v0.33 — Controlled gate-ablation experiment

- Added `frontierlab/gate_ablation.py` with two explicitly separated experiment types: post-generation gate replay and same-model/same-cases prompt-level ablation.
- Added a deployable recorded replay for the genuine 12-case Meta Muse Glimmer batch. The replay makes zero new model calls and binds back to the recorded NIM receipt.
- Current recorded result: 8 decisive + 4 abstaining model outputs; all 8 decisive outputs already had valid anchored quotes, so the post-processing source/quote gate introduced 0 new abstentions. Eight surviving decisions still require 12-case researcher review.
- Added a manual, hard-capped two-call NIM workflow for the stronger prompt-level comparison: label-only Arm A versus quote-grounded Arm B, followed by deterministic gating; Arm C remains human review.
- Accuracy stays unavailable unless a complete independently verified gold set is explicitly supplied. Provisional AI-authored labels are never used as gold.
- Added a Streamlit panel for the recorded replay with tokens, latency, gate effect and review-pending status.
- Added tests, documentation and a v0.33 version bump. The workflow has no automatic retry and is not automatically triggered.

## 2026-10-29 · v0.32 — Trajectory audit graph

- Added `frontierlab/trajectory_graph.py`, an audit-only process graph separate from the evidence graph.
- The graph contains the fixed five-stage workflow spine plus model-call receipts, recorded human-intervention events, method evaluation, rejected claims and process-taxonomy signals.
- Model-call nodes retain hashes, model identity, timing and usage only; prompts and model outputs are not copied into the graph.
- Trajectory relations describe process flow and never participate in the EXTRACTED-only scientific evidence gate.
- `reporting.export_json()` now includes a top-level `trajectory_graph` object.
- The Streamlit interface adds **7 · Trajectory audit graph · process trace** with node counts and a `trajectory.json` download.
- Added dedicated tests and documentation. No model call, retry behavior or scientific decision rule changed.

## 2026-10-29 · v0.31 — Process error taxonomy

- Added `frontierlab/error_taxonomy.py` to classify blocking and failure signals without treating expected human-governance gates as runtime errors.
- Categories cover governance gates, insufficient evidence, citation/source failures, missing resources, model runtime failures, rejected claims and scientific tensions.
- `process_metrics` now exports the taxonomy alongside SCR, human-intervention events and NIM efficiency/AERR semantics.
- The Streamlit process-metrics panel displays non-runtime blocking signals separately from runtime failures and scientific tensions.
- Added regression tests and documentation. No model calls, autonomous retry or scientific decision rule changed.

## 2026-10-29 · v0.30 — Recorded human-intervention event stream

- Added `frontierlab/interventions.py` with normalized, timestamped human-intervention events bound to workflow artifacts.
- New runs record four consequential researcher actions: claim review saved, method evaluation saved, planning approved and plan-step approved.
- `Run` now exports `human_events`; events include UTC time, event kind, bound artifact ID, actor label when supplied and `identity_verified=false`.
- Process metrics now prefer the recorded event stream instead of inferring human actions from downstream artifacts. Legacy runs without events retain the conservative artifact-derived fallback.
- Planning approval is recorded only after the saved evaluation passes `require_evaluation()`; a blocked attempt before a valid evaluation does not create a false approval event.
- Added integration coverage proving the real review → evaluation → planning workflow produces the expected event sequence and that provenance export exposes it.
- Feature branch CI passed **316 tests** in run 40908530796.
- No model calls, autonomous retries or identity-authentication mechanism were added.

## 2026-10-29 · v0.29 — Process metrics and audit export

- Added `frontierlab/process_metrics.py`, a deterministic metrics layer derived from the current `Run` state.
- Added five-stage SCR as workflow milestone completion, explicitly not a scientific quality score.
- Added a conservative human-intervention observable count from claim reviews, saved method evaluation, planning proxy and evidence-graph step approvals; the UI labels this **Observed human actions**, not a complete HIC.
- Added NIM-specific AERR semantics: N/A on zero-error runs; 0% only when runtime errors occurred and none were autonomously recovered under the no-retry policy.
- Added NIM attempted-call, failure, token and recorded elapsed-time summaries.
- `reporting.export_json()` now includes a top-level `process_metrics` record; the Streamlit UI exposes an audit-only process-metrics panel.
- Added dedicated documentation and regression tests. No model call, retry behavior or scientific gate was added.

## 2026-10-29 · v0.28 — Agentic-AI landscape and Level 1 self-assessment (docs only)

- Added a concise, original-language summary of the 2026 agentic-AI autonomy framework and mapped it to FrontierLab without reproducing the source paper's figures or tables.
- Self-assessment: FrontierLab is a **Level 1 Assisted Pipeline by design**. Models fill fixed roles, while code and the researcher control stage transitions; the verified NIM path has no automatic retry or autonomous repair loop.
- Corrected the earlier draft's overstatements: not every free-form model field is semantically validated; receipt/budget guarantees are scoped to the verified NIM backend; workflow state is not transactional rollback; AERR is N/A on zero-error runs.
- Updated traceability mapping after evidence-graph schema v2: approval/content binding and source-fingerprint validation are now shipped on main, while signed identity, full trajectory nodes, process metrics and a shared error taxonomy remain future work.
- README now links the assessment and records the **304-test** main verification run after schema v2.
- No model calls, dependencies or runtime behavior changed.

## 2026-10-29 · v0.27 — Evidence-graph approval integrity (schema v2)

- `load_graph()` now applies the same reviewer and note rule as `approve_plan_step()` (non-empty reviewer, note of 8+ characters; one shared check). An approval with an empty reviewer or a short note, hand-injected onto an approvable step, is now rejected instead of accepted.
- Approval records now include `approved_at_utc` (ISO-8601 UTC) and `approval_digest`. The digest is a SHA-256 over the step ID, the exact step text, the cited IDs, the reached papers and their source fingerprints. An approval moved to another step, or kept after the step text is rewritten, is now rejected. A rebuild drops approvals whose step or source record changed.
- Paper nodes now carry `review.source_fingerprint`. `load_graph()` rejects a Paper record that doesn't match it, which closes the self-consistent abstract + passage + quote rewrite. New `load_graph(..., expected_fingerprints=run_fingerprints(run))` checks the graph against a trusted run. Without it, an unsigned file whose every hash was recomputed still passes; this is documented and tested.
- The schema is bumped to `frontierlab.evidence-graph.v2`. v1 graphs are rejected with a "rebuild from the run" message rather than migrated, because a v1 approval carries nothing that can be verified. The app builds graphs from the live run and never loads saved ones, so its round trip is unaffected.
- Tests: 15 new tests in `tests/test_evidence_graph.py`, and one existing assertion updated (`v1` → `v2`). The local suite passed **304 tests**.

## 2026-10-29 · v0.25 — Provenance-tagged evidence graph

- Added `frontierlab/evidence_graph.py`, a plain-dict graph that links a run's plan steps back to the literature (Paper ← Passage ← Claim ← Hypothesis ← PlanStep). Edges are tagged EXTRACTED, INFERRED or AMBIGUOUS.
- EXTRACTED is assigned only when a claim passed the verbatim evidence gate and its quote is located in the cited abstract, with character offsets. Model stances without an anchored quote are INFERRED. Conflicting labels (mixed or inconclusive stances, opposite stances from the same source, or a reviewer CONTRADICTED / INSUFFICIENT verdict) are AMBIGUOUS.
- New plan-step path gate: a step can be approved only if every reachable edge is EXTRACTED and every cited source is reached. This adds to the existing gates and does not replace or relax any of them.
- `claim_verification` now exposes the shared anchor check (`quote_anchored`, `locate_quote`). `audit_predictions` uses it with unchanged behaviour.
- `Run.evidence_graph` is included in the provenance JSON export. The app adds section 6 with provenance counts, a monochrome line-art view, the surfaced non-evidence links, a step gate table and approval form, and a `graph.json` download.
- `load_graph()` re-anchors passages and EXTRACTED edges, and fails closed on a tampered or stale graph.
- The provenance vocabulary is inspired by Graphify (Graphify Labs, Apache-2.0), credited in the docs. No dependency was added and no NOTICE entry is needed.
- The local suite passed **289 tests**.

## 2026-10-28 · v0.24 — DetectorScope explainability / output-audit lens

- Added an optional DetectorScope adapter for interpretable AI-text detector diagnostics across FrontierLab model outputs.
- Records detector label, `p_ai`, logit, bias, active feature descriptions, per-feature importance and token-level highlights when available.
- Added a strict diagnostic-only boundary: academic-integrity, student-discipline, hiring, publication, authorship-attribution and scientific-truth uses are rejected before the detector is called.
- Supports DetectorScope's published `tau` grid from 0.00 to 0.95 in 0.05 increments and the logreg / XGBoost head choices.
- Raw audited text is not copied into the audit record; only a SHA-256 input hash and normalized feature evidence are stored.
- Added comparison summaries for cross-model linguistic-feature audits without optimizing text to evade detection.
- The default installation remains unchanged; no DetectorScope, Gemma, SAE weights or PyTorch dependency is added to `requirements.txt`.
- GitHub Actions run 40730431308 passed **265 tests**.
- No real DetectorScope inference has been executed; the authors' disclaimer against high-stakes individual decisions is preserved in FrontierLab's runtime contract.
- Architecture diagram, README shape legend and Mermaid text version now show DetectorScope as an optional lens in an aside off the truth path (it reads copies of model outputs and feeds no gate, review or plan); NOTICE records the DetectorScope (Apache 2.0 / CC BY 4.0) and Gemma-based checkpoint terms.
- NOTICE adds the previously missing Meta Llama 3.1 8B Instruct (Llama 3.1 Community License, Acceptable Use Policy, required attribution notice) and Muse2-230M (Apache 2.0) entries; later sections renumbered.

## 2026-10-28 · v0.23 — Llama 3.1 8B local baseline worker

- Added `meta-llama/Llama-3.1-8B-Instruct` as an optional medium-size local baseline / general-purpose worker.
- The adapter implements FrontierLab's existing `json(role, task, payload)` contract so the same bounded structured task can be compared across model scales.
- Every Llama 3.1 receipt is explicitly marked `baseline_only=true` and `scientific_output_independently_verified=false`.
- Added a process-local hard call budget, no automatic retry, strict JSON parsing, input/output hashes and runtime injection without adding an 8B checkpoint or GPU dependency to the default installation.
- Added benchmark dimensions for JSON validity, abstention, citation-ID validity, verbatim-quote validity, researcher intervention, latency and input/output size.
- Added a zero-network preflight and dedicated documentation for the 128K-context, text-only baseline role.
- GitHub Actions run 40664232272 passed **259 tests**.
- No new Llama 3.1 inference has been executed by this integration; Muse Glimmer remains the verified scientific reasoning backend.

## 2026-10-28 · v0.22 — Muse2-230M edge structured worker

- Added `Muse-research/Muse2-230M` as an optional **Edge Structured Worker**, not as a scientific reasoning model.
- Allowed tasks are restricted to metadata normalization, log-to-JSON extraction, schema formatting and lightweight routing.
- Scientific/medical truth-decision fields such as supported, contradicted, entailment, diagnosis, treatment, efficacy and safety are rejected before generation.
- Added strict output-schema/type validation plus SHA-256 provenance for input text, schema and validated output; raw input text is not stored in receipts.
- Kept the default FrontierLab installation unchanged: no PyTorch, Muse runtime or checkpoint is added to `requirements.txt`.
- Added a zero-network preflight and documentation for the injected local runtime boundary.
- GitHub Actions run 40663293839 passed **253 tests**.
- No real Muse2 inference has been executed; the model card itself warns that this scale hallucinates facts readily and is unsuitable for factual-reliance or medical/safety-critical judgment.

## 2026-10-28 · v0.21.1 — Hosted Spark capability matrix corrected

- Rechecked the current hosted-provider catalogs rather than assuming every Muse Spark deployment exposes every native modality.
- Updated Together to its current published endpoint `meta-models/Muse-Spark-Open-816B-A42B` with serverless image/audio/video input.
- Added the temporary Together promo endpoint as an explicit, non-default profile.
- Kept Fireworks serverless at `accounts/fireworks/models/muse-spark-open` and restricted its advertised media profile to image input.
- Provider-specific unsupported media is rejected locally before consuming the call budget or making a request.
- Documented current standard serverless pricing parity: $1.25/M input, $0.15/M cached input and $4.25/M output.
- No hosted inference was triggered by this correction.

## 2026-10-28 · v0.21 — Muse Spark Open frontier multimodal backend

- Added a provider-neutral `MuseSparkHostedClient` for Meta Muse Spark Open while preserving the existing `.json(role, task, payload)` research interface.
- Added `.multimodal_json(..., media=[...])` for text plus image, audio and video evidence without changing the five-stage scientific governance pipeline.
- Recorded Meta-listed hosted model strings for Together AI and Fireworks AI, while keeping provider SDKs, endpoints and credentials outside the core adapter.
- Added process-local call budgeting, no automatic retries, provider/model identity checks, strict JSON parsing, media-type bounds and input/output hash provenance.
- Raw media references are not copied into provenance receipts.
- Added a zero-network preflight; FrontierLab does not self-host or auto-download the 816B checkpoint.
- Meta Muse Glimmer remains the verified stable backend; Muse Spark Open is an optional frontier mode and Liquid d1 remains a lightweight evidence verifier.
- GitHub Actions run 40656773225 passed **237 tests**.
- No live Muse Spark hosted inference has been executed by this integration.

## 2026-10-28 · v0.20 — Optional d1-2B multimodal evidence gate

- Added a strict optional adapter for Liquid AI `d1-2B` using its documented `system_one(state, questions, media=...)` decision interface rather than treating it as a chat model.
- Scientific figure inspection asks typed questions for relevance, support, contradiction, evidence localization and visible-value extraction in one pass.
- d1 probabilities remain model signals; no scientific entailment label is produced automatically and no default 0.5 support threshold is assumed.
- Local threshold calibration and researcher review remain mandatory before a d1 signal can influence the research workflow.
- The default FrontierLab installation does not add Torch/Transformers, download a 2B checkpoint or change the public HF CPU Space.
- Added an offline preflight that performs zero network calls and a dedicated documentation note for the optional extension.
- GitHub Actions run 40655646863 passed **230 tests**.
- No live d1 scientific inference has been executed; Meta Muse Glimmer remains the central hackathon reasoning model.

## 2026-10-28 · v0.19 — Researcher-selected M2 method evaluation

- Recorded the researcher's explicit selection of **M2 — Structure-based dual-pH histidine-scanning computational design**; M1 remains a comparator rather than being discarded.
- Preserved the human rationale separately from the canonical `frontierlab.method-evaluation.v1` object so provenance does not invalidate deterministic evaluation reconstruction.
- Bound the evaluation to the exact recorded live Muse hypothesis trace rather than a paraphrased summary.
- Added an explicit downstream validation requirement: where feasible, use an orthogonal assay such as SPR on monomeric Fab to distinguish intrinsic affinity from avidity/stoichiometry effects.
- `require_evaluation()` now reconstructs the saved M2 evaluation exactly and confirms it is eligible for Stage 5 Planning.
- Open reproducibility checks remain for M2 data, code availability and computational environment; no scientific execution is claimed.
- GitHub Actions run 40578886168 passed **224 tests**.
- Planning remains unapproved and no Planning Agent call has been made.

## 2026-10-28 · v0.18 — Human-reviewed Meta synthesis completed

- GitHub Actions run 40574846326 completed the bounded reviewed continuation on the previously recorded two-source research case.
- Exactly two additional Muse Glimmer roles ran in order: Adversarial Skeptic Agent and Hypothesis Agent.
- Both calls completed normally; combined continuation usage was 2,317 tokens.
- Two citation-linked hypotheses survived source auditing.
- The run stopped before Method Evaluation and Planning; neither stage was automated.
- The saved artifact passed the offline provenance validator and is summarized in `docs/runs/nim_reviewed_continuation_20261028.json`.
- Added a validated Stage 4 handoff and an unselected two-method comparison draft for researcher review.
- Scientific accuracy and generalization remain unverified.

## 2026-10-28 · v0.17 — Bounded continuation after human review

- Added `scripts/nim_research_continue_trial.py` to rehydrate the recorded two-source Meta extraction and the completed researcher review without repeating extraction calls.
- Revalidates review schema, dataset ID, case IDs, paper IDs, source fingerprints, claims and exact quotations before any continuation is eligible.
- Enforces a fresh two-call hard cap: **Adversarial Skeptic Agent → Hypothesis Agent**, then stops before method evaluation or planning.
- Added a manual-only GitHub workflow that preserves a non-secret continuation artifact and performs no automatic retries.
- Added regression tests for source-bound rehydration, exact role sequence, method-boundary stop, stale review rejection and pending-review rejection.
- GitHub Actions run 40573319812 passed **217 tests**.
- No real continuation API call has been triggered by this change; live skeptic/hypothesis synthesis remains pending.

## 2026-10-28 · Legacy MUSE multilingual reference

- Added a dedicated reference note for Facebook Research's archived MUSE multilingual word-embedding project.
- Explicitly separated legacy **MUSE (Multilingual Unsupervised and Supervised Embeddings)** from the current **Meta Muse Glimmer 30B** model integration.
- Documented a possible future Stage 2 multilingual query-expansion role without claiming the archived project is bundled, executed or validated in FrontierLab.
- Kept upstream code and data out of the repository; the upstream repository declares CC BY-NC 4.0.

## 2026-10-28 · v0.16 — Researcher review and revision-bound HF deployment

- Saved Jaycee871's explicit SUPPORTED judgments and supplied rationales for both core-extraction cases, bound to the original question, case IDs and source snapshots.
- Displayed the completed two-claim review separately from the still-unreviewed 12-case pilot; preserved the original pending packet and extraction receipt.
- Added deployment revision display and an opt-in HF deploy script that updates only the existing public Docker CPU Basic Space from an explicit source snapshot.
- The deploy job receives only HF_TOKEN1. It neither transfers an NVIDIA key nor changes inference enablement or hardware.
- Hypotheses, method selection and plans remain separate workflow actions; deployment is not a live synthesis result.
- All 214 offline tests pass locally and in GitHub CI, including recorded-review bindings and deployment packaging/target checks.
- Deployed 58 snapshot assets to the existing HF Space; verified matching RUNNING runtime revision, health HTTP 200, v0.16 source marker and both human judgments/rationales in the rendered UI. HF NIM inference remains disabled.

## 2026-10-28 · v0.15 — Optional NIM research backend and real review pause

- Added an owner-enabled NIM backend with explicit per-session transfer consent and a shared process cap of eight attempted calls; no automatic retries.
- Preserved the same client through all five UI stages, recorded backend identity and request receipts, blocked provider switching and cleared stale results before new attempts.
- Tested all five UI stages and consent revocation with fake HTTP responses. Local suite: 210 passing tests.
- Completed two real core extraction calls on frozen published excerpts (1,802 tokens total); two quoted claims reached HUMAN_CLAIM_REVIEW_REQUIRED, with no automated review, hypothesis or plan.
- Preserved the receipt and pending review packet and disabled the dedicated bounded trigger.
- Public HF configuration/deployment and real reviewer-controlled continuation remain pending; no NVIDIA key was copied to HF.

## 2026-10-28 · v0.14 — Real Meta JSON and published-excerpt batch runs

- Verified one published-excerpt JSON response (5.126 seconds, 526 tokens) and one 12-case joint-context batch (11.168 seconds, 1,794 tokens) via NVIDIA NIM.
- Preserved strict schema checks, expected IDs, original final text, input/output hashes and raw predictions.
- Batch returned eight quote-anchored supporting/contradicting responses and four insufficient-evidence responses; human references remain pending and accuracy remains null.
- Added scripts with explicit opt-ins, 24 offline tests, run receipts and an offline-compatible predictions packet. Full local suite: 195 passing tests.
- Disabled both branch-scoped single-request triggers. No default-branch auto-inference trigger or billed Meta Platforms API use.
- Added a clearly labeled recorded-run download to Streamlit; HF rebuild and the complete live research pipeline remain pending.

## 2026-10-28 · First verified Meta Muse Glimmer final response

- Used the connected GitHub integration to create a branch-scoped one-shot trigger for the user's explicitly requested NVIDIA NIM trial; no browser login required.
- One synthetic request succeeded: meta/muse-glimmer-30b, finish_reason=stop, 10.535 seconds, 100 prompt + 149 completion = 249 tokens.
- Preserved the public receipt and verified both input and full short-output hashes against the script/log.
- Disabled the one-shot trigger after execution; default-branch manual workflow remains unchanged.
- Structured JSON, real-literature metrics and the complete live research pipeline remain unverified. No billed Meta Platforms API was used.

## 2026-10-28 · v0.13 — Published-excerpt pilot preparation

- Added 12 passage-level cases from four real antibody-engineering papers, with short attributed quotations and source snapshots.
- Kept AI-authored provisional reference labels separate from blind reviewer/model packets; no human gold or measured model accuracy is claimed.
- Added offline packet export and imported-prediction comparison; label metrics remain absent until complete researcher-supplied review.
- Preserved raw predictions and reported human corrections separately from automatic quote checks.
- Added reviewer-packet download to Streamlit and 15 software tests; 171 tests pass locally.
- No live model request, new secret workflow or HF deployment. Genuine Meta inference remains blocked pending manual trial launch.

## 2026-10-28 · v0.12 — Method evaluation before planning

- Added source-bound candidate comparison, six reproducibility-documentation checks, uncertainty and explicit researcher selection or deferral.
- Added an optional local Meta Method Evaluation Agent proposal path; no genuine inference is claimed.
- Plans require a current evaluation, preserve selected-method constraints and include controls, metrics, replication and falsification.
- Changed human review or regenerated hypotheses invalidate downstream results.
- Added protein-design evaluation context from official Proteinbase materials; no claim about Meta admission reasons or biological success.
- Local suite passes 156 tests, including two Streamlit interaction tests. HF rebuild and live Meta model testing remain separate milestones.

## 2026-10-28 · Single-call inference receipt hardening

- Added UTC start time, elapsed time, input/output hashes and filtered GitHub run/revision identifiers to the manual NVIDIA smoke-test receipt.
- Truncated answers and missing model identities now fail the smoke test instead of receiving a success status.
- Added nine offline receipt tests; the client and smoke-test subset passes 20 tests locally.
- No live model result is claimed; manual-only execution and the single-request/no-retry policy remain in place.

## 2026-10-28 · v0.11 — Cross-stage research failure injection

- Created 12 fictional failure scenarios across evidence, computation, dataset holdout and human teachability.
- Bound prior human review decisions to full source record versions and research question.
- Added deterministic checks for source mismatch, misattributed quotations, spoofed tool output and peptide group overlaps.
- Added a simulated Research Failure Lab panel to Streamlit with JSON export.
- No scientifically validated findings, real Meta model execution or real human learning scores are claimed.

## 2026-10-28 · v0.10 — BioNeMo offline scientific-tool adapter

- Added BioNeMo tool registry with status flags; only Boltz-2 protein preflight is available.
- Added source-bound human authorization requirements for research preflight, separate from permission to transfer data to NVIDIA.
- Added deterministic, sequence-redacted manifest with request hash and no implied GPU inference.
- Added strict Boltz-2 response shape checks that do NOT mistake schema validity for scientific proof.
- Added standalone zero-network preflight script and negative regression tests.
- No new HF deployment, API key, GPU job, paid Meta inference or NVIDIA hosted inference.

## 2026-10-27 · v0.9 — Human gate before hypothesis synthesis

- Added source-bound review packet with deterministic IDs, human verdicts and rationale.
- Blocked live Skeptic/Hypothesis execution until all cases are reviewed and two distinct sources are SUPPORTED.
- Continued model synthesis and planning can cite ONLY reviewer-supported papers.
- Added Streamlit review form and portable JSON export, plus regression tests.
- No real NVIDIA/Meta inference, GPU quota or paid Meta API used in this update.

## 2026-10-27 · v0.8 — fail-closed live abstract passage grounding

- Live claim extraction now requires a verbatim 24–500 character evidence_quote from the cited abstract; ungrounded claims are blocked.
- Added excerpt-match flags to Claim records, exposed text in UI/export, and regression tests for wrong-paper, missing, tiny and fabricated quotations.
- Explicitly distinguishes quotation presence from scientific entailment.
- Synthetic demo remains intact, no genuine model inference and no billed Meta API triggered by this change.
- HF Space must be rebuilt to pick up the new code.

## 2026-10-27 · v0.7 — optional OpenCode reviewer

- Added OpenCode project config with default approvals, no model or provider key, read-only reviewer, and static security tests.
- Git push, shell secrets commands and unknown external directory access are blocked by OpenCode tool permissions, but no OS security boundary is claimed.
- NVIDIA Muse Glimmer live trial has NOT succeeded; earlier two invocations returned no final answer. Fixed output budget awaits a fresh manual run.
- Nothing installed or deployed in HF Space.

## 2026-10-27 · v0.6.1 — Correct empty Muse Glimmer trial answers

- Two user-triggered NVIDIA NIM trial runs (40527133709, 40527145564) received API responses but returned no final text with the former 192-token budget.
- Per NVIDIA official documentation, model reasoning consumes the same completion-token budget, so low budgets can end before user-facing output.
- Set low reasoning strength, recommended non-greedy temperature, and a 2048-token output budget; no automatic retries.
- Record only safe finish_reason/token counts on empty answer, never private reasoning or API credentials.
- Live model output remains pending one new manually triggered trial.

## 2026-10-27 · v0.6 — Claim-to-passage audit & opt-in NVIDIA Meta inference

- Added 10 synthetic hand-labeled examples illustrating source-ID, quotation and semantic support gaps.
- Added strict benchmark scoring and conflict recall based on independently supplied annotations.
- Added a fixed NVIDIA NIM Meta Muse Glimmer client and manual-only single-call trial (no Meta Platforms paid API).
- Added synthetic benchmark expander to the Streamlit UI; HF Space rebuild still required.
- No actual NVIDIA inference has run, and synthetic benchmark scores are NOT AI model accuracy.

## 2026-10-27 · v0.5 — Springer Nature Meta API v2 and three-source discovery

- Added Meta v2 bibliographic adapter, secure manual API test, and offline source parsing tests.
- Added DOI-normalized provenance-preserving deduplication and explicit missing-abstract accounting.
- Added opt-in GitHub Actions three-source Europe PMC / Springer Nature Meta / Open Access discovery run.
- No private keys are printed; published HF Space still does not have publisher API credentials.
- Live Meta v2 connection and three-source runs are pending manual invocation.

## 2026-10-27 · v0.4 — Springer Nature Open Access connector

- Added read-only Springer Nature OA metadata/abstract client, DOI provenance and bounded requests.
- Added offline parsing and security tests; missing secrets and HTTP failures do not expose request URLs.
- Added opt-in, manual-only GitHub Actions connection test referencing Open_Access_API.
- No live credential request has been made; public HF Space does not inherit GitHub Secrets.

## 2026-10-27 · v0.3 — local Meta open-weight inference preparation

- Introduced loopback-only llama.cpp client for official Muse Glimmer with real model-identity precheck.
- Removed executable paid Meta API access; no keys or billing endpoints used.
- Added free Kaggle/HF CPU resource preflight and explicit opt-in local serving script.
- Added offline tests for remote-endpoint blocking, non-Meta checkpoint rejection, and HF CPU memory shortfall.
- Meta checkpoint not yet loaded; live model inference and contest model-compliance evidence remain pending.

## 2026-10-27 · v0.2 — OpenClaw / OpenShell isolation experiment

- Added a simulated fail-closed capability gate, three offline tests, and a clearly labeled demo.
- Added a host preflight and manual OpenShell creation, effective-policy inspection, benign network probe and cleanup scripts.
- No real OpenShell runtime, network denial, inference or GPU allocation has been claimed.
- Billed Meta API remains disabled. Open-weight Meta model compliance is still outstanding.

# Changelog

## 2026-10-27 · v0.1.1 — cost-safe resource assessment
- Confirmed live Wolfram calculation and Undermind research access; saved four relevant cited papers in a separate workspace.
- Added deterministic scientific heterogeneity calculator and offline tests independently checked against Wolfram.
- Added no-cost Kaggle GPU capability diagnostic. Actual Kaggle GPU runtime has not been tested.
- Disabled all paid Meta API calls in Streamlit UI until credit-card concerns are resolved.
- Documented the requirement for real Meta open-weight model execution before competition submission.
- All online Meta inference, Muse Glimmer GPU deployment and Kaggle GPU usage remain UNVERIFIED.

## 2026-10-27 · v0.1 competition start

- Built Streamlit UI and modular evidence-grounded, citation-gated research workflow.
- Added Europe PMC retrieval adapter, Meta model client adapter, explicit claim and citation validation.
- Added disagreement detection, skeptical review, source-checked hypothesis stage and manual planning approval.
- Introduced fictional synthetic fixture clearly separated from real literature and live model output.
- Added eight passing offline unit tests, a Windows run script, and GitHub Actions test workflow.
- External API connectivity, hosted UI, factual validation and end-to-end live Meta model calls: NOT YET VERIFIED.


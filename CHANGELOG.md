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


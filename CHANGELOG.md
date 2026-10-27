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

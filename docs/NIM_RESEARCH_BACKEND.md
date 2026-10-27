# NVIDIA Meta backend in the research interface

Implemented in v0.15, October 28, 2026 (Asia/Taipei).

The fourth interface mode connects the existing research workflow to Meta Muse Glimmer through NVIDIA NIM. Each research run keeps its original model client through evidence extraction, human-reviewed synthesis, optional method suggestions and planning. The backend and request receipts are included in the exported Run.

The recorded one-case and twelve-case checks are separate from this integration. A complete live hosted research session is not claimed by passing software tests.

## Owner configuration

The research backend is off by default. On the server that runs Streamlit, configure NVIDIA_API_KEY and FRONTIERLAB_NIM_RESEARCH=YES, using that hosting service's secret/environment settings. Do not enter an API key into the research question or commit it to the repository. GitHub Secrets do not automatically configure Hugging Face Spaces.

Then choose **Live Europe PMC + Meta via NVIDIA** and explicitly allow the question and retrieved abstracts to be sent to NVIDIA. With that mode disabled or consent withdrawn, the app will not continue the run's remote synthesis or planning.

An enabled server shares a hard cap of eight attempted research calls across clients in that Python process. Failed calls count; there are no automatic retries. Restarting the server resets this in-memory cap, so it is not an account-wide credit or dollar limit. The initial NIM UI run is limited to two abstracts. A typical successful path takes two extraction calls, two synthesis calls, one optional method-proposal call and one planning call.

These controls are not a replacement for hosting authentication or provider billing controls. The public HF backend is not enabled by this code change, and no NVIDIA secret has been transferred to HF.

## Workflow behavior

1. Retrieve abstracts using the existing Europe PMC interface.
2. Extract claims with the selected backend and check quotations.
3. Stop for per-claim researcher review.
4. Resume skeptic/hypothesis calls only after all claims are reviewed and at least two sources are human-supported.
5. Compare methods and select a candidate with a rationale or defer.
6. Require a current evaluation and separate approval before drafting a plan.

Continuations use the saved client rather than choosing a new local client from a model-name string. A provider change is rejected by the live workflow. Each request records its role, model ID, input/output hashes, timing, finish reason and token usage without exporting the credential or hidden reasoning.

Strict JSON checks reject duplicate keys, nonfinite JSON values, non-object results, truncated output and missing model identity. A valid object still needs the existing stage-specific source, review and planning checks; it does not establish scientific correctness.

New research attempts clear an old displayed result first, so a failed request does not leave an earlier study looking like the new result.

## Verification boundary

Offline tests exercise the actual Streamlit controls through all five stages using a fake HTTP transport and artificial scientific/reviewer outputs. They confirm client reuse, six expected calls, provenance export, rejection behavior and revoking consent. These are software interaction tests, not real human annotation or a live scientific finding.

The bounded extraction runner uses two frozen published abstract excerpts and a two-call budget:

```bash
python -m scripts.nim_research_extract_trial
```

It also requires FRONTIERLAB_EXTRACTION_TRIAL=YES and the research backend owner opt-in. It always stops before reviewer judgments, hypotheses, method selection and plans. Its actual run status and receipt are linked in the README after execution. The two sources are fixed snapshots, so this test does not establish a fresh live literature search.

For a real full-session demonstration, configure the actual deployment, verify its source revision, have a researcher review the extracted claims and method comparison, then continue under the same backend. The existing 12-case pilot still awaits independently assessed reference labels.

## Reproduction

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
streamlit run app.py
```

No default-branch automatic inference workflow is introduced. Model-backed actions remain explicit and bounded. A separate HF rebuild is required before the new mode appears.

## Recorded bounded extraction result

[Run 40566722171](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40566722171) completed two real Evidence Extraction Agent calls: 863 and 939 tokens, 1,802 total, with normal final responses. Two source-quoted claims passed deterministic passage checks and the core stopped at HUMAN_CLAIM_REVIEW_REQUIRED. No reviewer label, hypothesis, evaluation or plan was generated automatically. The dedicated trigger is disabled.

[Full receipt](runs/nim_research_extraction_20261028.json) · [Pending reviewer packet](runs/nim_claim_review_pending_20261028.json).

This verifies the NIM-backed core extraction and pause boundary on fixed excerpts. All five interface stages are verified with mocked transport, while the actual reviewer-controlled continuation and HF deployment remain pending.

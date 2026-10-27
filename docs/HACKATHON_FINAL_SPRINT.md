# FrontierLab — Meta Hackathon Final Sprint

**Prepared 2026-10-28 (Asia/Taipei) · Planning memo, NOT proof of completed inference or submission.**

## Official submission boundary

- Official organizer schedule: https://dev.meta.ai/events/global-hackathon
- Project submissions due 2026-11-04 21:00 ET = **2026-11-05 10:00 Asia/Taipei** (US Eastern Standard Time applies after the November 1 DST change). Organizer may update dates.
- Track: Indie Developer; project theme: Push the Frontier.
- The organizer explicitly invites work with Meta Muse family, Meta open-weights and related tooling. A truly executed Meta inference capability must be demonstrable.
- Detailed Final Submission form / exact required demo-video duration must be rechecked in participant portal; a **3-minute** video is our internal production target, not asserted as a new official mandatory limit.

## Verified vs. unverified, as of this plan

| Deliverable | Status | Evidence / limitation |
| --- | --- | --- |
| Python research evidence/provenance pipeline | SOFTWARE VERIFIED | v0.11 main `08c3621`, GitHub Actions 116 passing tests; mainly mock/fictional guard tests |
| Manuscript-to-abstract source matching | SOFTWARE VERIFIED | Valid DOI and verbatim excerpt checks are not semantic entailment |
| Human review gate, version-bound annotations | SOFTWARE VERIFIED | Review decisions are not independent adjudicated expert ground truth |
| BioNeMo Boltz-2 request and response checks | OFFLINE PREFLIGHT ONLY | NO hosted Boltz-2 model computation, no validated binding function |
| HF public Streamlit Space | REBUILT AND RUNNING AS SHOWN BY USER | Updated v0.11 demo panel has NOT been separately confirmed deployed |
| Authentic Meta Muse Glimmer response | BLOCKED / NOT VERIFIED | Two earlier NVIDIA NIM workflow runs returned no final answer; revised v0.6.1 settings not yet exercised live |
| Live research claim-evaluation comparison | NOT STARTED | No authentic Meta output and independently adjudicated dataset yet |
| Three-minute competition video | NOT VERIFIED | Design storyboard not recording |
| Formal submission through Cerebral Valley | NOT SUBMITTED | GitHub + HF publication is not contest submission |

## Priority 1: genuine Meta inference — highest priority

1. Perform one **explicitly authorized** NVIDIA trial smoke call with the updated reasoning budget; no automatic retries or provider spending.
2. Preserve the official model ID, a short non-sensitive output, finish reason, token use, timing and exact git SHA in a reproducible run record. Never store API keys, headers or hidden reasoning.
3. If the trial cannot return an answer, evaluate a legitimate alternative open-weight Meta provider from the official partner list (Baseten / Modal / Fireworks) subject to confirmed participant entitlement and costs. Do NOT silently switch to a non-Meta model while claiming Meta usage.
4. Do not confuse 'API responded HTTP 200' with 'model gave an answer', or 'model gave an answer' with verified scientific judgment.

## Priority 2: small controlled claim-error benchmark

- Start with 12 preregistered cases: 4 supported, 4 contradicted, 4 insufficient, using legally reusable snippets. Cover exact quote but opposite interpretation, source-ID mismatch, stale version, claims that cannot be decided from abstract, and tool failure.
- Expert/researcher labels are separate from agent predictions. Blind dual review is desirable before publishing any gold standard.
- On the SAME queries and model compare (A) no evidence gate, (B) source+quote gate, (C) source+quote+human review. Keep human intervention explicit, rather than calculating fake fully autonomous accuracy.
- Record per-case outcome, citations, reject/abstain, latency, token usage, false positives and false negatives. A reviewer correction is not automatically evidence the model corrected itself.
- Do not present 12 offline fictional rule tests as model benchmark outcomes.

## Priority 3: judge-operable demo

- Build a 3-minute story: research question → live evidence retrieval → a model makes an overly strong claim → citation/excerpt check and/or researcher challenges it → app abstains or limits the conclusion → accessible provenance trail and download.
- Failure-path demo must remain honest if the model unexpectedly produces a correct response. Include a recorded genuine model trace and a replay only when transparently labeled 'recorded real run'.
- Public HF CPU Basic is the frontend. It does not have a loaded 30B model; hosting Meta inference needs an approved external provider/backend with secrets kept off GitHub and appropriate cost controls.
- Package a stable backup video that matches the application; do not call prewritten fake responses live model output.

## Priority 4: release and submission

- Stabilize HF Space and verify exact version SHA in frontend; fix any crashes and expose clear model-provenance labels.
- Show a concise README: problem, novel contribution, what is working today, verified evaluation numbers, limits and reproduction steps.
- Confirm actual current requirements within the logged-in Cerebral Valley participant portal; complete all mandatory fields, video, code and links.
- Target internal completion by 2026-11-04 in Taipei to leave room for portal and upload failures; formal deadline remains 2026-11-05 10:00 Taiwan time.

## Features deferred until after project submission

- Additional talking-only agents or elaborate agent orchestration not tied to measured results.
- Full BioNeMo hosted science execution, wet-lab binder optimization, or unlicensed private paper upload.
- Claims about AlphaZero-style human concept transfer without a proper participant study.
- Publication-scale biomedical benchmark or claims of superhuman AI scientific discovery.

**GO / NO-GO:** Do not claim a Meta-powered live end-to-end scientific product unless there is authentic dated Meta model output, a working endpoint, and a reproducible recorded trace. A transparent partial prototype is preferred over a false success claim.

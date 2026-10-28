# FrontierLab — Meta Hackathon Final Sprint

**Prepared 2026-10-28 (Asia/Taipei) · Planning memo, NOT proof of completed inference or submission.**

## Verified inference update — October 28, 2026

FrontierLab now has several dated genuine Meta Muse Glimmer / NVIDIA NIM records rather than only the original synthetic smoke test:

- the original synthetic one-shot returned final text with verified model identity;
- a published-excerpt strict-JSON check completed;
- a 12-case joint-context batch completed;
- the NIM-backed core executed two real Evidence Extraction Agent calls on frozen published excerpts and stopped at the mandatory human-review gate;
- both core claims were subsequently reviewed by Jaycee871 as SUPPORTED with written rationales;
- a source-bound continuation runner now revalidates that completed review and permits exactly two further calls: Adversarial Skeptic Agent and Hypothesis Agent.

The reviewed continuation has been executed successfully in GitHub Actions run 40574846326. Two citation-linked hypotheses were preserved from the exact live artifact. The researcher has now selected M2, and the canonical method evaluation passes the Planning eligibility reconstruction check. Planning remains deliberately unapproved. GitHub Actions run 40578886168 passed 224 tests.

## Official submission boundary

- Official organizer schedule: https://dev.meta.ai/events/global-hackathon
- Project submissions due 2026-11-04 21:00 ET = **2026-11-05 10:00 Asia/Taipei** (US Eastern Standard Time applies after the November 1 DST change). Organizer may update dates.
- Track: Indie Developer; project theme: Push the Frontier.
- The organizer explicitly invites work with Meta Muse family, Meta open-weights and related tooling. A truly executed Meta inference capability must be demonstrable.
- Detailed Final Submission form / exact required demo-video duration must be rechecked in participant portal; a **3-minute** video is our internal production target, not asserted as a new official mandatory limit.

## Verified vs. unverified, as of this plan

| Deliverable | Status | Evidence / limitation |
| --- | --- | --- |
| Python research evidence/provenance pipeline | SOFTWARE VERIFIED | v0.19 codebase; GitHub Actions run 40578886168 passed 224 tests, including exact method-evaluation reconstruction and Planning-gate eligibility |
| Manuscript-to-abstract source matching | SOFTWARE VERIFIED | Valid DOI and verbatim excerpt checks are not semantic entailment |
| Human review gate, version-bound annotations | SOFTWARE + RECORDED REVIEW VERIFIED | Two real core claims have explicit researcher SUPPORTED judgments; these are not independent expert gold labels |
| BioNeMo Boltz-2 request and response checks | OFFLINE PREFLIGHT ONLY | NO hosted Boltz-2 model computation, no validated binding function |
| HF public Streamlit Space | v0.16 DEPLOYED AND VERIFIED RUNNING | CPU Basic frontend is revision-bound and shows the completed human review; NIM remains owner-disabled there |
| Authentic Meta Muse Glimmer response | MULTIPLE RECORDED NIM RUNS | Synthetic smoke, strict JSON, 12-case batch and two-call core extraction recorded; no scientific accuracy claim |
| Human-reviewed live continuation | EXECUTED AND RECORDED | Run 40574846326 completed the bounded skeptic → hypothesis continuation; artifact provenance validated and exact outputs preserved |
| Researcher method selection | COMPLETED | M2 selected; M1 retained as comparator; canonical evaluation bound to exact live hypotheses and human rationale stored separately |
| Live research claim-evaluation comparison | NOT COMPLETED | 12-case real model outputs exist, but independently adjudicated reference labels and controlled A/B/C comparison remain pending |
| Three-minute competition video | NOT VERIFIED | Design storyboard not recording |
| Formal submission through Cerebral Valley | NOT SUBMITTED | GitHub + HF publication is not contest submission |

## Priority 1: prepare Stage 5 Planning gate — highest priority

1. Preserve M2 as the selected method and keep M1 as a comparator for histidine-independent alternatives.
2. Carry M2's unresolved checks into Planning: design-input provenance, executable/alternative ADAPT implementation, computational environment and protonation/modeling parameters.
3. Require orthogonal affinity validation where feasible, such as SPR on monomeric Fab, to separate intrinsic affinity from avidity/stoichiometry effects.
4. Do **not** invoke the Planning Agent until the researcher explicitly approves Stage 5 planning.
5. Continue to distinguish a validated execution trace and a reasoned method choice from validated scientific truth.

## Priority 2: controlled claim-error benchmark

- Start with 12 preregistered cases: 4 supported, 4 contradicted, 4 insufficient, using legally reusable snippets. Cover exact quote but opposite interpretation, source-ID mismatch, stale version, claims that cannot be decided from abstract, and tool failure.
- Expert/researcher labels are separate from agent predictions. Blind dual review is desirable before publishing any gold standard.
- On the SAME queries and model compare (A) no evidence gate, (B) source+quote gate, (C) source+quote+human review. Keep human intervention explicit, rather than calculating fake fully autonomous accuracy.
- Record per-case outcome, citations, reject/abstain, latency, token usage, false positives and false negatives. A reviewer correction is not automatically evidence the model corrected itself.
- Do not present 12 offline fictional rule tests as model benchmark outcomes.

## Optional frontier extension: Muse Spark Open frontier backend

- Provider-neutral software adapter is implemented for Meta Muse Spark Open, including text/image/audio/video request contracts and provenance controls.
- Do not make Spark a submission blocker: the verified Glimmer path remains the stable demo baseline.
- If hosted Spark access is obtained, use one bounded multimodal evidence case tied to M2 (for example, a structure or assay figure) and preserve the provider/model receipt.
- Liquid d1-2B remains a lightweight evidence-verification option; Spark is the Meta-native frontier reasoning layer.
- No live Spark inference is currently claimed.

## Priority 3: judge-operable demo

- Build a 3-minute story: research question → live evidence retrieval → a model makes an overly strong claim → citation/excerpt check and/or researcher challenges it → app abstains or limits the conclusion → accessible provenance trail and download.
- Failure-path demo must remain honest if the model unexpectedly produces a correct response. Include a recorded genuine model trace and a replay only when transparently labeled 'recorded real run'.
- Public HF CPU Basic is the frontend. It does not have a loaded 30B model; hosting Meta inference needs an approved external provider/backend with secrets kept off GitHub and appropriate cost controls.
- Package a stable backup video that matches the application; do not call prewritten fake responses live model output.

## Current official schedule check — October 28, 2026

The current Meta and Cerebral Valley event pages both still list **November 4, 2026 at 9:00 PM ET** as the project submission deadline. The official Meta page describes the Indie Developer Track as being judged on creativity, technical ambition and whether the project works; the Push the Frontier theme explicitly includes accelerating scientific experiments.

Official references:
- https://dev.meta.ai/events/global-hackathon
- https://events.cerebralvalley.ai/e/meta-ai-developer-hackathon

The participant portal may contain additional submission-form fields that are not visible on the public event pages, so the logged-in final form still needs a separate check.

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

# FrontierLab — Meta Hackathon Final Sprint

**Updated 2026-10-29 (Asia/Taipei) · Planning memo, NOT proof of completed inference or submission.**

## Verified inference update — October 28, 2026

FrontierLab now has several dated genuine Meta Muse Glimmer / NVIDIA NIM records rather than only the original synthetic smoke test:

- the original synthetic one-shot returned final text with verified model identity;
- a published-excerpt strict-JSON check completed;
- a 12-case joint-context batch completed;
- the NIM-backed core executed two real Evidence Extraction Agent calls on frozen published excerpts and stopped at the mandatory human-review gate;
- both core claims were subsequently reviewed by Jaycee871 as SUPPORTED with written rationales;
- a source-bound continuation runner now revalidates that completed review and permits exactly two further calls: Adversarial Skeptic Agent and Hypothesis Agent.

The reviewed continuation was executed successfully in GitHub Actions run 40574846326. Two citation-linked hypotheses were preserved from the exact live artifact. M2 is selected, its canonical Method Evaluation still reconstructs exactly, and a zero-call Stage-5 readiness contract now carries all open reproducibility checks and planning obligations forward. Planning remains deliberately **unapproved and ungenerated**.

## Official submission boundary

- Official organizer schedule: https://dev.meta.ai/events/global-hackathon
- Project submissions due 2026-11-04 21:00 ET = **2026-11-05 10:00 Asia/Taipei** (US Eastern Standard Time applies after the November 1 DST change). Organizer may update dates.
- Track: Indie Developer; project theme: Push the Frontier.
- The organizer explicitly invites work with Meta Muse family, Meta open-weights and related tooling. A truly executed Meta inference capability must be demonstrable.
- Detailed Final Submission form / exact required demo-video duration must be rechecked in participant portal; a **3-minute** video is our internal production target, not asserted as a new official mandatory limit.

## Verified vs. unverified, as of this plan

| Deliverable | Status | Evidence / limitation |
| --- | --- | --- |
| Python research evidence/provenance pipeline | SOFTWARE VERIFIED | v0.35 candidate; 348-test branch suite passed after Stage-5 readiness UI integration. Test count is software coverage, not model accuracy. |
| Manuscript-to-abstract source matching | SOFTWARE VERIFIED | Valid DOI and verbatim excerpt checks are not semantic entailment |
| Human review gate, version-bound annotations | SOFTWARE + RECORDED REVIEW VERIFIED | Two real core claims have explicit researcher SUPPORTED judgments; these are not independent expert gold labels |
| BioNeMo Boltz-2 request and response checks | OFFLINE PREFLIGHT ONLY | NO hosted Boltz-2 model computation, no validated binding function |
| HF public Streamlit Space | v0.16 DEPLOYED AND VERIFIED RUNNING | CPU Basic frontend is revision-bound and shows the completed human review; NIM remains owner-disabled there |
| Authentic Meta Muse Glimmer response | MULTIPLE RECORDED NIM RUNS | Synthetic smoke, strict JSON, 12-case batch and two-call core extraction recorded; no scientific accuracy claim |
| Human-reviewed live continuation | EXECUTED AND RECORDED | Run 40574846326 completed the bounded skeptic → hypothesis continuation; artifact provenance validated and exact outputs preserved |
| Researcher method selection | COMPLETED | M2 selected; M1 retained as comparator; canonical evaluation bound to exact live hypotheses and human rationale stored separately |
| M2 planning readiness | COMPLETED, NOT AUTHORIZED | Zero-call packet validates current context and carries data/code/environment gaps plus SPR/avidity/search-bias/replication obligations. `planning_approved=false`; no plan generated. |
| Gate-ablation comparison | PARTIALLY EXECUTED | Recorded 12-case post-generation replay is implemented: 8 decisive / 4 abstaining outputs, 0 new abstentions from the source/quote post gate, 8 human reviews pending. A true same-model/same-cases two-call prompt-level workflow is prepared but not yet executed. No accuracy claim. |
| Three-minute competition video | NOT VERIFIED | Design storyboard not recording |
| Formal submission through Cerebral Valley | NOT SUBMITTED | GitHub + HF publication is not contest submission |

## Priority 1: explicit Stage 5 decision — highest priority

1. The M2 readiness packet is now implemented and machine-checks the current reviewed context before Stage 5.
2. The packet carries all unresolved checks forward: design-input provenance, executable/alternative ADAPT implementation, environment/dependencies and protonation/modeling settings.
3. It also requires matched-pH controls, Fab-level validation, monomeric-Fab SPR where feasible, avidity/stoichiometry caveats, structure/search-bias disclosure, replication and falsification.
4. **Do not invoke the Planning Agent until the researcher explicitly approves Stage 5 planning.** Readiness is not approval.
5. If approval is given later, the generated plan must remain a cited conceptual draft and then pass the existing evidence-graph plan-step gate.

## Priority 2: controlled gate ablation and claim-error benchmark

- Start with 12 preregistered cases: 4 supported, 4 contradicted, 4 insufficient, using legally reusable snippets. Cover exact quote but opposite interpretation, source-ID mismatch, stale version, claims that cannot be decided from abstract, and tool failure.
- Expert/researcher labels are separate from agent predictions. Blind dual review is desirable before publishing any gold standard.
- The zero-call post-generation replay is now implemented and visible in the app. It must be described as a replay because the original prompt already requested evidence quotes.
- The manual two-call prompt-level workflow now holds the model and case/source payload fixed while changing only the task instruction: (A) label-only, (B) quote-grounded + deterministic source/quote gate; (C) remains human review.
- Keep human intervention explicit rather than calculating fake fully autonomous accuracy.
- Record per-case outcome, citations, reject/abstain, latency, token usage, false positives and false negatives. A reviewer correction is not automatically evidence the model corrected itself.
- Do not present 12 offline fictional rule tests as model benchmark outcomes.

## Optional frontier extension: Muse Spark Open frontier backend

- Provider-neutral software adapter is implemented for Meta Muse Spark Open, including text/image/audio/video request contracts and provenance controls.
- Do not make Spark a submission blocker: the verified Glimmer path remains the stable demo baseline.
- If hosted Spark access is obtained, use one bounded multimodal evidence case tied to M2 (for example, a structure or assay figure) and preserve the provider/model receipt.
- Liquid d1-2B remains a lightweight evidence-verification option; Spark is the Meta-native frontier reasoning layer.
- No live Spark inference is currently claimed.

## Optional edge extension: Muse2-230M edge worker

- Keep Muse2-230M strictly in the preprocessing layer: metadata normalization, log-to-JSON, schema formatting and routing.
- Do not use it for evidence support/contradiction labels, scientific entailment or clinical decisions.
- No model download or live Muse2 inference is required for the competition submission; the stable Meta reasoning path remains primary.

## Optional baseline extension: Llama 3.1 8B baseline

- Use Llama 3.1 8B only as a medium-size local baseline / worker, not as a replacement for the verified Muse Glimmer path.
- A future controlled benchmark can compare Muse2-230M, Llama 3.1 8B and Muse Glimmer on the same structured evidence task, with Muse Spark reserved for frontier multimodal reasoning.
- Report JSON validity, abstention, citation validity, quotation validity, researcher intervention, latency and cost/size proxies separately.
- Do not turn the competition demo into a model leaderboard; the core story remains evidence-grounded, human-gated scientific research.

## Optional audit extension: DetectorScope output-audit lens

- Use DetectorScope only to explain detector features in model-generated scientific prose; it is outside the scientific truth path.
- Never use its label or `p_ai` for academic-integrity, authorship, publication, hiring or person-level decisions.
- A future controlled model-scale study may compare recurring interpretable linguistic features across Muse2-230M, Llama 3.1 8B, Muse Glimmer and Muse Spark outputs.
- Keep this extension non-blocking for submission; the five-stage evidence/human-review pipeline remains the core demo.

## Priority 3: judge-operable demo

- Use [`DEMO_RUNBOOK.md`](DEMO_RUNBOOK.md) as the canonical ~3-minute recording story. Keep the narrative on the scientific problem, genuine recorded Meta inference, governance effect, human decision and provenance—not the number of optional models.
- Failure-path demo must remain honest if the model unexpectedly produces a correct response. Include a recorded genuine model trace and a replay only when transparently labeled 'recorded real run'.
- Public HF CPU Basic is the frontend. It does not have a loaded 30B model; hosting Meta inference needs an approved external provider/backend with secrets kept off GitHub and appropriate cost controls.
- Package a stable backup video that matches the application; do not call prewritten fake responses live model output.

## Current official schedule check — October 30, 2026

The current Meta and Cerebral Valley event pages both still list **November 4, 2026 at 9:00 PM ET** as the project submission deadline. The official Meta page describes the Indie Developer Track as being judged on creativity, technical ambition and whether the project works; the Push the Frontier theme explicitly includes accelerating scientific experiments.

Official references:
- https://dev.meta.ai/events/global-hackathon
- https://events.cerebralvalley.ai/e/meta-ai-developer-hackathon

The participant portal may contain additional submission-form fields that are not visible on the public event pages, so the logged-in final form still needs a separate check.

## Priority 4: release and submission

- Follow [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md): manually deploy current main to the existing HF Space, then verify exact source SHA, current central version, RUNNING runtime, health endpoint and rendered marker.
- Use [`SUBMISSION_COPY.md`](SUBMISSION_COPY.md) as the source of truth for public one-line/short/long descriptions and limitations; edit only when shipped behavior changes.
- Confirm actual current requirements within the logged-in Cerebral Valley participant portal; complete all mandatory fields, video, code and links.
- Target internal completion by 2026-11-04 in Taipei to leave room for portal and upload failures; formal deadline remains 2026-11-05 10:00 Taiwan time.

## Features deferred until after project submission

- Additional talking-only agents or elaborate agent orchestration not tied to measured results.
- Full BioNeMo hosted science execution, wet-lab binder optimization, or unlicensed private paper upload.
- Claims about AlphaZero-style human concept transfer without a proper participant study.
- Publication-scale biomedical benchmark or claims of superhuman AI scientific discovery.

**GO / NO-GO:** Do not claim a Meta-powered live end-to-end scientific product unless there is authentic dated Meta model output, a working endpoint, and a reproducible recorded trace. A transparent partial prototype is preferred over a false success claim.


## Post-submission Information Management research direction

FrontierLab now documents a project-origin Information Management extension around **maintainability, provenance and governance**.

This is not a claim that Paper2Agent or another cited paper already validated those three pillars. It is a FrontierLab / Pack Kwan Low research direction motivated by the move from passive research artefacts to operable agents.

Post-submission priorities:

- run the proposed maintainability benchmark using controlled dependency/API/environment failures;
- extend provenance from paper/model/human records to code/data/environment artefacts;
- study institutional tool/data authorization and responsibility boundaries;
- evaluate a Research Operating Interface that manages Paper / Code / Data, MCP-style tools/resources/prompts, Evidence Trace, Governance and Maintainability;
- study the proposed **Agent Availability** reporting statement as a complement to Data/Code Availability.

These items are research agenda, not current hackathon deliverables.

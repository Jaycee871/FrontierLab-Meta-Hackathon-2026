# FrontierLab — release & submission checklist

**Target public release:** current main after v0.35 and submission-package docs.  
**Public event deadline rechecked 2026-10-30 Asia/Taipei:** Nov 4, 2026 at 9:00 PM ET = **Nov 5, 2026 at 10:00 AM Asia/Taipei**. Organizer dates may change.

Official public references:

- https://dev.meta.ai/events/global-hackathon
- https://cerebralvalley.ai/e/meta-ai-developer-hackathon

## A. Repository freeze

- [ ] All intended PRs are merged.
- [ ] Main Git SHA is recorded.
- [ ] Main test workflow is green.
- [ ] README version matches `frontierlab/version.py`.
- [ ] README test count points to a real CI run.
- [ ] No open PR is required for the recorded demo.
- [ ] No secret/token/API key is committed.
- [ ] Historical run records are left immutable.

## B. Hugging Face deployment

The deployment workflow is manual (`workflow_dispatch`).

- [ ] Manually trigger **Deploy FrontierLab to existing HF Space** from current main.
- [ ] Confirm the deployment workflow's software tests pass.
- [ ] Confirm `deployment.json.version` equals the current central version.
- [ ] Confirm `deployment.json.source_sha` equals the intended main SHA.
- [ ] Confirm the HF Space commit receipt matches the new deployment.
- [ ] After the image rebuild, verify runtime status is RUNNING.
- [ ] Verify Streamlit health endpoint responds successfully.
- [ ] Verify rendered UI shows the current version and source marker.
- [ ] Verify CPU Basic hardware was not changed.
- [ ] Verify no NVIDIA credential or model opt-in was transferred to the Space.
- [ ] Preserve a new dated deployment receipt.

Do not equate "source committed to the Space repo" with "runtime verified healthy."

## C. Demo-state verification

Before recording:

- [ ] Published-literature pilot loads.
- [ ] RECORDED REAL META RUN panel displays.
- [ ] Gate-ablation replay shows 8 decisive / 4 abstaining / 0 new post-gate abstentions.
- [ ] Completed two-claim human-review record displays.
- [ ] Reviewed Skeptic → Hypothesis record is available.
- [ ] Method Evaluation shows M2 selected.
- [ ] Planning-readiness panel shows data/code/environment open.
- [ ] Planning-readiness panel shows Planning approved = NO.
- [ ] Evidence Graph renders or provides graph.json.
- [ ] Trajectory Audit Graph renders its statistics and provides trajectory.json.
- [ ] Complete provenance JSON downloads.
- [ ] No panel labels a recorded replay as live inference.

## D. Optional experiments

These improve the evaluation story but are not allowed to destabilize the submission.

### 12-case researcher review

- [ ] Download reviewer packet.
- [ ] Edit only labels and rationales.
- [ ] Upload it through the app.
- [ ] Verify source/case binding passes.
- [ ] Download canonical review packet.
- [ ] Report researcher corrections as intervention, not independent accuracy.

### Two-call prompt-level gate ablation

- [ ] Trigger only if NVIDIA NIM usage is explicitly authorized.
- [ ] Confirm exactly two calls were attempted.
- [ ] Confirm same model + same fixed payload.
- [ ] Preserve the artifact.
- [ ] Validate result before adding it to README/video.
- [ ] Do not retry automatically if the run fails.

## E. Stage 5 decision

Current default:

- [x] M2 selected.
- [x] Method Evaluation current.
- [x] Planning readiness contract current.
- [ ] **Researcher explicitly approves Stage 5 Planning.**
- [ ] Planning Agent runs.
- [ ] Draft plan reviewed.
- [ ] Individual plan steps pass Evidence Graph gate and researcher approval.

If Stage 5 is not approved before submission, say exactly that. A visible human boundary is part of the product design.

## F. Video

- [ ] Target approximately 3 minutes unless the logged-in portal specifies another requirement.
- [ ] Use the demo runbook.
- [ ] Show at least one genuine Meta execution record.
- [ ] Show a gate/human decision, not only happy-path output.
- [ ] Show one provenance view.
- [ ] Show the Stage 5 readiness/approval distinction.
- [ ] Check text readability at the final upload resolution.
- [ ] Do not use unsupported "autonomous scientist" language.

## G. Submission form

Public pages do not expose every logged-in final-submission field.

- [ ] Open the authenticated participant portal.
- [ ] Recheck mandatory fields and accepted link/video formats.
- [ ] Select Indie Developer track.
- [ ] Select / describe Push the Frontier accurately.
- [ ] Paste final project description only after matching it to the shipped revision.
- [ ] Add public GitHub link.
- [ ] Add verified public HF Space link.
- [ ] Add demo video link/file as required.
- [ ] Accept any required rules/waivers.
- [ ] Submit before the portal deadline.
- [ ] Capture submission confirmation.

## H. Claims audit

Before submission, search the README/video/copy for these risky phrases:

- "scientifically verified"
- "autonomous scientist"
- "accuracy" (unless independent gold actually exists)
- "live" next to recorded replay
- "deployed" when only a source upload is known
- "completed plan" when Stage 5 remains unapproved

Replace them with the narrowest true statement: software-verified, model-executed, researcher-reviewed, source-anchored, prepared, or scientifically unverified.

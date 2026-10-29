# FrontierLab — 3-minute demo runbook

**Internal recording target:** ~3:00.  
**Public claims must match shipped behavior.**

The judging story is deliberately narrow:

> A scientific AI should not jump from papers to a confident plan. FrontierLab makes every important transition inspectable, source-bound and researcher-controlled.

## Before recording

Use a revision that has passed CI and note the exact source SHA.

Current software baseline at preparation time:

- FrontierLab v0.35
- main source: `58f82df6043070654ec7e1dc16e25bfbcfcbd57b`
- 348 tests passed on main
- Stage 5 status: **readiness complete; planning not approved or generated**
- latest public Space deployment must be re-verified separately before recording

Do not call a recorded result "live". Do not call researcher review "independent gold". Do not call software tests model accuracy.

## 0:00–0:20 — The problem

**Screen:** FrontierLab landing page / five-stage pipeline.

Say, in substance:

> Scientific assistants can cite a real paper and still overstate what it says. FrontierLab turns literature-to-plan reasoning into a five-stage, human-gated process: Research, Evidence, Hypothesis, Evaluation and Planning.

Keep the point on **scientific traceability**, not the number of models in the repository.

## 0:20–0:50 — Genuine Meta inference

**Screen:** Published-literature pilot.

Show the panel labeled:

**RECORDED REAL META RUN**

Explain:

- Meta Muse Glimmer 30B was executed through NVIDIA NIM.
- The recorded 12-case batch used four published antibody-engineering sources.
- It returned 12 structured decisions: 8 decisive outputs and 4 insufficient-evidence abstentions.
- The displayed record is replayed from the preserved genuine run; opening the panel makes no new model call.

Optional one-line provenance:

> The record preserves model identity, hashes, token usage and elapsed time.

Do not claim scientific accuracy; the 12-case independent reference set is not established.

## 0:50–1:15 — What the gate actually does

**Screen:** Gate ablation expander.

Point to:

- Raw decisive: 8
- Quote-gated decisive: 8
- New abstentions from gate: 0
- Human reviews pending: 8

Say:

> This is a post-generation replay, not a causal prompt experiment. In this clean recorded batch, every decisive output already included a valid anchored quote, so the deterministic gate added zero new abstentions. That null effect is useful: the gate is an enforceable boundary, not a metric we force to look impressive.

Then mention:

> A stricter two-call same-model/same-cases prompt ablation is implemented as a manual workflow, but I do not present it as executed unless I actually run it.

## 1:15–1:45 — Human review changes what can advance

**Screen:** completed two-claim core review, then reviewed continuation.

Show that the two core claims have researcher judgments and rationales.

Say:

> Quote presence is not semantic entailment. These two core claims were reviewed by the researcher before synthesis could resume.

Then show the recorded Skeptic → Hypothesis continuation.

Say:

> Only after review did FrontierLab permit exactly two additional Glimmer calls: an adversarial skeptic and a hypothesis agent. It then stopped again before method selection and planning.

## 1:45–2:15 — Method selection and Stage 5 readiness

**Screen:** Method Evaluation → Planning readiness.

Show M2:

**Structure-based dual-pH histidine-scanning computational design**

Point to the planning-readiness panel:

- open checks: data, code, environment
- required obligations: 9
- Planning approved: NO

Say:

> The researcher selected M2, but readiness is not approval. FrontierLab carries unresolved reproducibility checks into Stage 5 and requires the future draft to address structure provenance, executable design tooling, matched-pH controls, Fab-level validation, replication and falsification.

Call out the most important interpretation safeguard:

> Where feasible, monomeric-Fab SPR is required as an orthogonal check so apparent cell-binding changes are not automatically interpreted as intrinsic affinity instead of avidity or stoichiometry.

Do not tick the planning-approval checkbox merely for the video unless Stage 5 has actually been approved.

## 2:15–2:45 — Two different provenance questions

**Screen:** Evidence Graph, then Trajectory Audit Graph.

Say:

> FrontierLab keeps scientific evidence provenance separate from process provenance.

**Evidence Graph**

> Can this plan step trace back through checked passages and reviewed sources?

Mention that EXTRACTED means the passage/ID linkage was checked, **not** that semantic truth was proven.

**Trajectory Audit Graph**

> What happened during the run—model calls, human interventions, method evaluation, rejected claims and blocking signals?

Emphasize that trajectory nodes never count as scientific evidence.

## 2:45–3:00 — Close on the competition thesis

**Screen:** clean architecture / hero.

Suggested close:

> FrontierLab is intentionally a Level 1 Assisted Pipeline, not an autonomous scientist. The frontier I am pushing is accountable scientific agency: Meta models can reason, critique and propose, while evidence gates and researcher decisions determine what is allowed to become the next scientific action.

## Optional insert only if later executed

If the manual two-call gate-ablation workflow is genuinely executed before recording, a short result may replace part of the 0:50–1:15 segment.

Only show it when the record proves:

- same Meta model;
- same 12 cases and source payload;
- exactly two model calls;
- Arm A label-only instruction;
- Arm B quote-grounded instruction plus deterministic gate;
- no automatic retry;
- human review status stated separately.

## Recording failure policy

If a live retrieval or UI action fails during recording:

- do not substitute a prewritten response and call it live;
- switch visibly to the recorded genuine run;
- state that it is a preserved real execution;
- keep the failure if it helps demonstrate the audit/error taxonomy.

A credible failure path is stronger than a fake perfect demo.

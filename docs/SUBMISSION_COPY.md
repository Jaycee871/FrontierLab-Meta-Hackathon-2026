# FrontierLab — submission copy

This file contains reusable public-facing copy. Update only claims that have actually changed.

## One-line description

**FrontierLab is an evidence-grounded, human-gated scientific research pipeline that uses Meta models to turn literature into reviewable hypotheses and plans without hiding the evidence, uncertainty or researcher decisions in between.**

## Short description

FrontierLab uses Meta Muse Glimmer 30B inside a five-stage scientific workflow: Research → Evidence → Hypothesis → Evaluation → Planning. Model claims must cite exact source passages, critical transitions require researcher review, and evidence/process provenance are exported separately. The system is designed to make scientific AI more auditable rather than more theatrically autonomous.

## Project description

Scientific language models can cite a real paper while still overstating what the source supports. FrontierLab addresses that failure mode by treating literature-to-plan reasoning as an auditable process instead of a single generation step.

A Meta Muse Glimmer 30B backend proposes source-linked claims, receives adversarial critique and produces falsifiable hypotheses. Deterministic source/quote checks reject unanchored claims, while explicit researcher gates control semantic review, method selection and planning authorization. A provenance-tagged Evidence Graph traces scientific artifacts back to source passages; a separate Trajectory Audit Graph records model calls, human interventions, rejected claims and process failures without treating those events as scientific evidence.

The current biomedical demonstration uses published pH-dependent antibody-engineering literature. The researcher selected a structure-based dual-pH design route, while FrontierLab carries unresolved reproducibility checks and orthogonal-validation requirements into a pre-planning contract. Planning remains deliberately human-authorized.

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
- Meta Muse Glimmer 30B through NVIDIA NIM for the verified model-backed research path;
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
- deterministic M2 planning-readiness contract.

Optional adapters for Muse Spark Open, Llama 3.1 8B, Muse2-230M, Liquid d1-2B and DetectorScope are intentionally separated from the verified Glimmer path.

## Meta-model usage that is genuinely demonstrated

The repository preserves several dated genuine Meta Muse Glimmer / NVIDIA NIM executions, including:

- a smoke/identity check;
- strict structured output;
- a 12-case published-excerpt batch;
- two Evidence Extraction Agent calls on the core biomedical case;
- a human-reviewed two-call continuation: Adversarial Skeptic Agent → Hypothesis Agent.

These are model-execution records, not claims of scientific accuracy.

## Current evaluation story

Software verification and scientific evaluation are reported separately.

Current software baseline:

- v0.35;
- 348 tests on main;
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
- process metrics/error taxonomy;
- gate-ablation replay;
- 12-case review packet round trip;
- M2 planning readiness.

## What remains deliberately incomplete

- the 12-case benchmark does not yet have an independently verified gold standard;
- the manual two-call prompt-level ablation should be called "prepared" until executed;
- M2 data/code/environment reproducibility checks remain open;
- Stage 5 Planning is not approved or generated unless the researcher explicitly authorizes it;
- no wet-lab experiment has been executed or scientifically validated by FrontierLab;
- optional Spark/d1/Llama/Muse2/DetectorScope adapters do not imply live model runs.

## Autonomy statement

FrontierLab is a **Level 1 Assisted Pipeline by design**.

Models fill bounded research roles. Code and the researcher control transitions. The verified NIM path has no automatic retries or autonomous repair loop. FrontierLab should not be described as a closed-loop autonomous scientist.

## Suggested final sentence

**The goal is not to remove the scientist from the loop; it is to make every model-assisted scientific step strong enough to inspect, challenge and reproduce.**

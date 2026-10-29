# Agentic AI landscape and FrontierLab self-assessment

FrontierLab is best described as a **Level 1 Assisted Pipeline**: models fill fixed research roles, while code and the researcher control stage transitions. It is not a closed-loop autonomous scientist.

This document summarizes the autonomy framework discussed by Zhao, Fang, Mao et al. (npj Drug Discovery, 2026) in our own words and maps it to FrontierLab's current implementation. It does not reproduce the paper's figures or tables.

## 1. Why Level 1

FrontierLab uses LLMs inside a fixed, human-orchestrated workflow.

| Dimension | FrontierLab today |
| --- | --- |
| Scientific path selection | Fixed roles: Evidence Extraction, Skeptic, Hypothesis, optional Method Proposal and Planning. |
| Tool choice | Retrieval and model backends are selected by code/configuration; the model does not dynamically choose tools in the core pipeline. |
| Persistence | `Run` stores in-session state and invalidates stale downstream artifacts, but there is no cross-session research memory. |
| Error recovery | The verified NVIDIA NIM path has no automatic retry and uses a bounded call budget. |
| Human role | Human review, method selection, plan authorization and plan-step approval are explicit transitions. |

This makes FrontierLab a deliberately constrained research co-pilot rather than a Level 2+ task controller.

## 2. Workflow topology

FrontierLab is a **sequential workflow**, not a swarm or supervisor architecture.

```text
Research question
  -> Evidence retrieval
  -> Evidence Extraction Agent
  -> source/quote checks
  -> human claim review
  -> Adversarial Skeptic Agent
  -> Hypothesis Agent
  -> researcher Method Evaluation
  -> explicit Planning approval
  -> Planning output
  -> per-step evidence-graph approval
```

The Skeptic output is passed into the Hypothesis prompt. Optional method proposals feed researcher evaluation rather than choosing the path themselves. One `Run` object serves as shared in-session state.

## 3. What is actually validated

FrontierLab uses artifact-specific controls rather than treating every model sentence as independently verified.

- Evidence claims must cite a known source and include an anchored passage before they advance.
- Human reviewers label accepted claims SUPPORTED, CONTRADICTED or INSUFFICIENT.
- Hypotheses and plans are checked against allowed source IDs and current workflow state.
- The Skeptic decision is rule-controlled, while its explanation and uncertainty prose remain model output.
- `EXTRACTED` in the evidence graph means source/passage linkage was checked. It does not mean semantic entailment was proven.

## 4. Failure-state semantics

FrontierLab is not a transactional rollback engine.

Later-stage scientific artifacts are generally assigned after validation, but partial state changes can still occur. A Skeptic completion event can be recorded before a later Hypothesis call fails. Initial extraction also does not create a complete `Run` until its extraction work finishes.

The accurate claim is: FrontierLab preserves and invalidates research artifacts deliberately, but it does not provide atomic rollback or autonomous recovery.


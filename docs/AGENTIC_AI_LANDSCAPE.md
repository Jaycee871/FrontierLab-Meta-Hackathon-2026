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


## 5. Traceability after evidence-graph schema v2

Current `main` includes evidence-graph schema v2, merged in commit `b3cdef7`. GitHub Actions run 40905004672 passed **304 tests**.

| Area | Current capability | Remaining limitation |
| --- | --- | --- |
| Artifact graph | `Paper <- Passage <- Claim <- Hypothesis <- PlanStep` with EXTRACTED / INFERRED / AMBIGUOUS edges. | Model calls, Method Evaluation and failed/rejected paths are not first-class graph nodes. |
| Step gate | A plan step is approvable only when its reachable evidence path is fully EXTRACTED and cited sources are reached. | Path anchoring is not proof of scientific entailment. |
| Approval integrity | Reviewer + rationale are required; `approved_at_utc` and `approval_digest` bind the approval to the step and cited source state. | Reviewer identity is not authenticated. |
| Source integrity | Paper nodes carry `source_fingerprint`; `load_graph()` validates them and can compare them with trusted run fingerprints. | Standalone graph files still depend on a trusted run for stronger source comparison. |
| Model-call provenance | Verified NIM receipts contain role/model identity, input/output hashes, timing, token counts and finish reason. | Hash-only receipts are not replayable prompts/outputs; optional adapters use separate provenance contracts. |
| Failure trace | `run.log` and explicit statuses capture several events. | No shared error taxonomy and failed paths are still under-modeled. |

Schema v2 closes two gaps identified in the earlier draft of this assessment:

- approvals are revalidated on load and bound to the exact step/source state;
- paper records are fingerprint-checked and can be compared with a trusted `Run`.

Graphs written under v1 are rejected rather than silently migrated because their older approval records cannot be verified to the same standard.

## 6. Process metrics

FrontierLab does not yet publish formal HIC, AERR or SCR metrics.

- **Human Intervention Count (HIC):** a future implementation should distinguish approvals, corrections and takeovers rather than counting every click equally.
- **Autonomous Error Recovery Rate (AERR):** if a run has no runtime errors, AERR is **N/A** because the denominator is zero. If runtime errors occur under the current no-retry NIM path, autonomous recoveries are zero, so the rate is 0% for that nonzero-error denominator.
- **Sub-task Completion Rate (SCR):** the five stages provide natural milestones, but no formal SCR report is generated yet.
- **Cost / efficiency:** NIM receipts expose token and wall-clock information, but there is no normalized project-level cost panel.

## 7. Highest-value remaining work

| Priority | Work | Reason |
| ---: | --- | --- |
| 1 | Normalize human interventions into attributable, timestamped events bound to artifact IDs. | Enables defensible intervention metrics and responsibility tracing. |
| 2 | Add a process-metrics export for HIC, SCR, AERR semantics and NIM token/latency totals. | Converts provenance into measurable process evidence. |
| 3 | Add a shared error taxonomy for BLOCKED / FAILED events and rejected artifacts. | Makes failure analysis consistent. |
| 4 | Run the controlled gate ablation: no gate -> source/quote gate -> source/quote + human review, using the same model and cases. | Measures governance value instead of autonomy claims. |
| 5 | Add model-call, evaluation and rejected-artifact nodes to the evidence graph. | Enables fuller trajectory and fault attribution. |
| 6 | Add verified reviewer identity if stronger identity assurance is required. | Separates record integrity from identity. |
| 7 | Add open-access full-text evidence behind the same quotation gate. | Improves evidence depth beyond abstracts. |

A bounded move toward Level 2, such as model-proposed query refinement plus one logged repair attempt, should be treated as a separate owner-approved experiment because it changes the current no-retry design.

## 8. Claims FrontierLab should not make

- It is not a closed-loop autonomous scientist.
- It is not Level 2+ under this framework.
- `EXTRACTED` does not equal scientific truth.
- 304 passing software tests do not measure model accuracy.
- Human review records are not equivalent to independently adjudicated scientific ground truth.

## Reference

Zhao D., Fang M., Mao L. et al. *The rise of agentic AI in drug discovery: from static tools to autonomous virtual scientists.* npj Drug Discovery 3, 43 (2026). DOI: 10.1038/s44386-026-00075-0.

Related FrontierLab docs: [Evidence graph](EVIDENCE_GRAPH.md) · [Human review gate](HUMAN_REVIEW_GATE.md) · [Verbatim evidence gate](VERBATIM_EVIDENCE_GATE.md) · [Method evaluation](METHOD_EVALUATION.md).

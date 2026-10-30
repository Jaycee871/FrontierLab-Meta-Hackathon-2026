# Research Operating Interface — conceptual architecture

## Purpose

The Research Operating Interface is FrontierLab's Information Management view of scientific agents.

It treats papers, code, data and agent tools as managed research resources and adds three control functions:

```text
                    Research Operating Interface
                              |
          ---------------------------------------------
          |                    |                      |
   Research artefacts      Agent interfaces      IM control layer
   Paper / Code / Data   MCP Tools/Resources/     Maintainability
                              Prompts              Provenance
                                                   Governance
```

This document is a concept architecture, not a claim that every module below is already deployed.

## Module map

| Module | Information-management role | FrontierLab status |
| --- | --- | --- |
| Paper | literature/knowledge input | implemented for current biomedical literature workflow |
| Code | executable research method | represented in reproducibility evaluation; general code orchestration is future work |
| Data | datasets / APIs | literature/source data implemented; general institutional data integration is future work |
| MCP Tools | executable agent capabilities | conceptual/integration direction |
| MCP Resources | managed references/data resources | conceptual/integration direction |
| MCP Prompts | reusable task contracts | analogous structured role/task contracts exist; generalized MCP prompt management is future work |
| Evidence Trace | claim-to-source provenance | implemented through Evidence Graph + measured Trace Coverage |
| Process Trace | who/what happened during execution | implemented through Trajectory Audit Graph + human events |
| Governance | permissions, approvals, accountability | partial prototype through human gates, budgets and audit rules |
| Maintainability | failure detection, regression, rebuild/repair | CI/error taxonomy exist; autonomous repair/rebuild is future work |

## Relationship to the current five-stage pipeline

The interface is a management layer over the current workflow:

```text
Research Operating Interface
        |
        +-- Research materials / tools / policy
        |
        +--> FrontierLab scientific workflow
             Research
               ↓
             Evidence
               ↓
             Hypothesis
               ↓
             Evaluation
               ↓
             Planning
```

## Observable interface concepts

### Current Activity

Expose the current stage, active sources, tool/backend identity, blocked state and human-review status.

### Active Sources

Show the sources currently contributing to the run.

A future multi-source interface may include PubMed/Europe PMC, arXiv, IEEE, Nature or institutional systems, but FrontierLab must display only sources actually connected in a given deployment.

### Evidence Graph

Display relationships between sources, passages, claims, hypotheses and plan steps.

### Source Audit

Expose citation/source existence and quotation anchoring checks.

### Trace Coverage

Implemented in `frontierlab/traceability.py` and exposed through the Research Operating Interface.

Two values are reported:

- **Source Trace Coverage** — fraction of in-scope downstream artifacts that reach at least one known Paper;
- **Strict Extracted Coverage** — fraction whose complete reachable path is EXTRACTED, resolves to Paper nodes, and has no unresolved sources or dead ends.

Recorded reviewed M2 core measurement:

- 4 / 4 in-scope artifacts source-traceable = **100% Source Trace Coverage**;
- 2 / 4 fully EXTRACTED = **50% Strict Extracted Coverage**.

The difference is intentional. The PMC4314675 path preserves an original model stance of `inconclusive` even though the later researcher review judged the claim SUPPORTED, so that path remains AMBIGUOUS rather than being rewritten into strict evidence.

These are provenance metrics, not model accuracy or scientific truth. See [Trace Coverage](TRACE_COVERAGE.md).

### Governance panel

Expose:

- permissions;
- approval requirements;
- model/tool budgets;
- sensitive-data policy;
- reviewer responsibility;
- prohibited actions.

### Maintainability panel

Future panel may expose:

- dependency drift;
- last regression-test result;
- tool health;
- environment rebuild status;
- repair attempts;
- quarantine status;
- maintainer approval.

## Design principle

The interface should answer three questions at any moment:

1. **What is the system doing?**
2. **Where did its scientific output come from?**
3. **Who or what authorized the next action?**

For a maintainable system, it should eventually answer a fourth:

4. **If a tool breaks tomorrow, can we detect, reproduce and repair the failure without losing scientific provenance?**

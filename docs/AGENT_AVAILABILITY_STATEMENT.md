# Agent Availability statement — FrontierLab proposal

> **Status:** proposed research-reporting template. This is not a current journal requirement or established standard.

The goal of an Agent Availability statement is to make an interactive research agent inspectable in the same spirit that Data Availability and Code Availability statements make datasets and software discoverable.

## Proposed template

### Agent identity

- Agent/project name:
- Version / release:
- Associated paper / DOI:
- Repository:
- Hosted endpoint:
- Release date:

### Research artefacts represented

- Paper version:
- Code revision:
- Dataset version(s):
- Model weights / provider:
- Prompt/tool contract version:
- Environment/container revision:

### Capabilities

- Supported scientific tasks:
- Executable tools:
- MCP tools/resources/prompts:
- Read-only capabilities:
- Write / execution capabilities:
- External APIs:

### Validation

- Regression-test suite:
- Scientific reference tests:
- Last validated date:
- Known failing tests:
- Reproducibility status:
- Independent validation available: yes / no

### Provenance

- Source/version hashes available: yes / no
- Model-call receipts available: yes / no
- Human-intervention log available: yes / no
- Evidence graph available: yes / no
- Process/trajectory graph available: yes / no
- Export format:

### Governance

- Authentication:
- Role/permission model:
- Sensitive-data access:
- Human approvals required:
- Actions prohibited:
- Audit retention:
- Institutional policy / IRB constraints:

### Maintainability

- Maintainer:
- Dependency monitoring:
- Automated regression tests:
- Failure detection:
- Automated repair permitted: yes / no
- Human approval required before repaired release:
- Last maintenance check:
- End-of-support policy:

### Limitations

- Known scientific limitations:
- Known technical limitations:
- Model/provider dependencies:
- Unsupported use cases:

## FrontierLab example — current prototype

- Agent/project name: FrontierLab
- Current software version: v0.37 candidate
- Domain demonstration: biomedical literature-to-hypothesis/method-planning workflow
- Verified Meta-backed path: Meta Muse Glimmer 30B via NVIDIA NIM
- Human approvals required: claim review, method selection, Stage 5 planning, plan-step approval
- Evidence provenance: Evidence Graph schema v2
- Process provenance: Trajectory Audit Graph
- Human intervention log: available
- Process metrics/error taxonomy: available
- Dependency/environment canary: **implemented** (regression testing + provenance + quarantine policy)
- Autonomous repair: **not implemented**
- Institutional patient-data access controls: **not implemented**
- Scientific accuracy / wet-lab validation: **not established**

This example is descriptive of the current FrontierLab prototype and should be updated whenever the shipped implementation changes.

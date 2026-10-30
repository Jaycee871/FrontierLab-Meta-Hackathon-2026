# FrontierLab — Information Management extension

## Claim boundary and research origin

This document records an **Information Management (IM) research extension proposed by Pack Kwan Low / Jaycee871** while developing FrontierLab.

It is informed by Paper2Agent and related work on interactive scientific agents, but the three-pillar framework below — **maintainability, provenance and governance** — is **not presented as a conclusion already validated by Paper2Agent or by another cited paper**.

Paper2Agent established an important prior step: research papers, code, data and methods can be converted into tested interactive agents and MCP-based tools. FrontierLab extends the question from:

> Can a paper become an operable agent?

to:

> If research artefacts become operable agents, how should institutions maintain, trace and govern them over time?

That second question is the Information Management contribution developed here.

---

## 1. From research paper to research operating interface

A **research artefact** is broader than the article PDF. It includes the paper, code, data, model/tool interfaces, parameters, environments, prompts, tests and outputs that make the research usable.

FrontierLab treats those artefacts as potentially **operable** rather than passive.

The long-term concept is a **Research Operating Interface**: a management layer that makes paper agents, code, data and scientific tools visible, inspectable and governable from one place.

The operating-system analogy is intentional:

- an operating system does not replace every application;
- it manages resources, permissions, execution and state across applications;
- similarly, a research operating interface would not replace papers, repositories or databases;
- it would manage how research artefacts are invoked, connected, audited and authorized.

This is a conceptual research direction, not a claim that FrontierLab already implements a complete research operating system.

---

## 2. Three Information Management pillars

### 2.1 Maintainability

**Question:** when a scientific agent or tool breaks, can the system detect the breakage and restore a usable state before the failure reaches the researcher?

Examples:

- a package upgrade breaks a paper agent;
- a remote API changes;
- a model version changes its output schema;
- an MCP tool stops satisfying its contract;
- a dependency becomes unavailable;
- a previously passing scientific workflow stops reproducing its expected artefacts.

A maintainable scientific-agent system should ideally support:

1. dependency/version observation;
2. automated regression tests;
3. failure classification;
4. bounded repair or environment rebuild;
5. re-validation against reference outputs;
6. human approval before repaired components are promoted back into trusted use.

A possible maintenance loop is:

```text
Dependency/tool change
  -> automated regression test
  -> failure detected
  -> classify failure
  -> bounded repair / rebuild attempt
  -> re-run reference tests
  -> human review
  -> promote or quarantine
```

### FrontierLab today

FrontierLab already has pieces of this layer:

- CI regression testing;
- centralized codebase version metadata;
- explicit error taxonomy;
- source/evaluation invalidation when upstream state changes;
- reproducibility checks for data, code, environment, parameters, protocol and metrics;
- no automatic retry in the verified NIM research path.

### Not yet implemented

FrontierLab does **not** currently claim:

- autonomous dependency repair;
- autonomous environment rebuilding after package failure;
- autonomous code patching and promotion;
- unattended recovery of broken scientific tools.

Those are future maintainability experiments.

---

### 2.2 Provenance

**Question:** can a reviewer reconstruct where a scientific output came from?

The analogy is a production or food traceability record: the final product should be traceable back to the inputs, tools, versions and processing history that produced it.

For a scientific agent, useful provenance includes:

- paper/source identity;
- exact passage or data snapshot;
- dataset version;
- tool and package version;
- model identity;
- prompt/task contract;
- parameters;
- environment;
- human decisions;
- intermediate artefacts;
- final outputs;
- hashes and timestamps.

A reviewer citing an agent-produced figure should be able to ask:

> Which paper, data, tool version, model, parameters and human decisions produced this figure?

### FrontierLab today

This pillar is already partially operationalized:

- Evidence Graph: Paper ← Passage ← Claim ← Hypothesis ← PlanStep;
- source fingerprints;
- EXTRACTED / INFERRED / AMBIGUOUS provenance labels;
- content-bound plan-step approvals;
- model-call receipts with model identity, hashes, timing and token usage;
- normalized human-intervention events;
- separate Trajectory Audit Graph for process history;
- downloadable provenance JSON;
- deterministic process metrics.

### Remaining provenance gaps

Future work includes:

- replayable versioned environments;
- direct code/data artefact hashes throughout every research step;
- stronger cross-system identity binding;
- signed reviewer approvals;
- richer provenance across external MCP tools and institutional systems.

---

### 2.3 Research governance

**Question:** who is allowed to do what, with which data and tools, and who remains accountable when something goes wrong?

Scientific agents can potentially:

- read protected health information;
- execute code;
- query institutional databases;
- invoke third-party APIs;
- change files;
- launch costly compute;
- propose or execute experiments.

Governance therefore needs explicit rules for:

- tool permissions;
- data-access scope;
- role-based authorization;
- approval gates;
- institutional policy;
- audit retention;
- exception handling;
- responsibility and accountability.

Example governance questions:

- May a literature agent access patient-level data?
- Which tools are allowed for students, clinicians, external collaborators or autonomous services?
- Which actions require researcher approval?
- Who is accountable for a model-generated scientific claim?
- Who is responsible when a tool implementation or upstream dataset is wrong?
- How should a research institution record and audit agent actions?

### FrontierLab today

FrontierLab implements a narrow governance prototype:

- human claim-review gate;
- researcher-owned method evaluation;
- explicit Stage 5 planning authorization;
- plan-step approval;
- bounded model-call budgets;
- no automatic retry on the verified NIM path;
- process error taxonomy;
- audit/provenance export;
- clear distinction between software verification, model execution, researcher review and scientific validation.

It does **not** yet implement institutional RBAC, patient-data access control, IRB policy enforcement or legal accountability assignment.

---

## 3. Research Operating Interface

The proposed interface organizes research artefacts into three groups.

### Group A — Research materials

- **Paper** — literature and knowledge input;
- **Code** — executable analysis methods;
- **Data** — datasets, databases and external data APIs.

### Group B — Agent / MCP integration

- **MCP Tools** — executable functions exposed to an agent;
- **MCP Resources** — reference files, databases and structured information;
- **MCP Prompts** — reusable task/instruction contracts.

MCP can be understood as a standardized connection layer between agents and external capabilities. In FrontierLab, this remains an integration direction rather than a claim that every current tool is already exposed through MCP.

### Group C — Information Management control layer

- **Evidence Trace** — where each scientific claim came from;
- **Governance** — who can use which capabilities, under what rules;
- **Maintainability** — whether tools remain usable as environments and dependencies change.

These control functions are what transform a collection of paper agents into a manageable research infrastructure.

---

## 4. Research workflow

A future Research Operating Interface can expose a simple four-step workflow:

1. **Interpret Query**  
   Clarify the scientific question, entities, scope and uncertainty.

2. **Search & Retrieve**  
   Query multiple approved sources rather than relying on one database.

3. **Analyze & Synthesize**  
   Build source-bound claims and an evidence graph; surface conflicts rather than hiding them.

4. **Generate Output**  
   Produce a structured output in which important claims remain traceable to sources and process history.

FrontierLab's current five-stage workflow is more conservative:

```text
Research -> Evidence -> Hypothesis -> Evaluation -> Planning
```

The four-step Research Operating Interface should therefore be treated as a higher-level management view over the more detailed FrontierLab scientific workflow, not as a replacement.

---

## 5. System-status concepts

A future interface can make research-agent state visible through operational indicators.

### Source Audit

Checks whether cited sources exist and whether the quoted passage is actually present in the source snapshot.

FrontierLab already implements a narrow version of this through source-ID and verbatim-quote gates.

### Trace Coverage

Proposed metric:

> the proportion of material claims in an output that can be traced through an approved provenance path to source evidence.

No percentage should be displayed unless measured from an explicit claim set. Values such as “98% trace coverage” are interface mock-up examples only until a real measurement pipeline exists.

### Execution Status

Shows what the system is currently doing, which sources/tools are active and which stage is blocked or complete.

This should expose **execution and decision provenance**, not private model chain-of-thought.

---

## 6. Five Information Management research questions

### 6.1 System integration

How should papers, code repositories, datasets, APIs, MCP tools and institutional information systems be connected without losing provenance or access boundaries?

### 6.2 Workflow governance

Which scientific transitions may be automated, and which require researcher or institutional approval?

### 6.3 Source auditing

Can an agent automatically verify that a citation exists, is current, and actually supports the quoted material?

### 6.4 Evidence traceability

Can every important conclusion be traced to a source, transformation and responsible human/model action?

### 6.5 Human-in-the-loop collaboration

How should a scientific agent generate alternatives while leaving consequential selection and accountability with the researcher?

FrontierLab currently operationalizes all five to different degrees, but none should be treated as a solved institutional problem.

---

## 7. Maintainability as the next FrontierLab experiment

A future FrontierLab maintainability benchmark could intentionally break a paper agent or research tool through controlled changes:

- dependency upgrade;
- changed API schema;
- missing package;
- incompatible model output;
- stale environment;
- missing data artefact.

The experiment can measure:

- detection rate;
- time-to-detection;
- correct failure classification;
- recovery success;
- repair attempts;
- regression-test pass rate;
- human intervention count;
- provenance completeness before/after repair;
- whether repaired outputs still match scientific reference artefacts.

A safe initial design would allow bounded repair only inside an isolated environment and require human approval before any repaired tool is promoted.

See [Maintainability benchmark — proposed experiment](MAINTAINABILITY_BENCHMARK.md).

---

## 8. Agent Availability — proposed future research-reporting statement

Modern journals increasingly request data- and code-availability statements.

This extension proposes studying whether interactive scientific-agent work may eventually need an additional reporting field:

> **Agent Availability**

Possible contents:

- Is an interactive research agent available?
- Where is it hosted?
- Which paper/code/data version does it represent?
- What tools may it execute?
- Is the environment reproducible?
- What model/provider does it require?
- What permissions/data scopes does it have?
- What tests validate it?
- What maintenance status does it have?
- What provenance/audit records can it export?
- What actions still require human approval?

This is a **forward-looking proposal by the FrontierLab project**, not an existing journal standard.

See [Agent Availability statement proposal](AGENT_AVAILABILITY_STATEMENT.md).

---

## 9. Relationship to Paper2Agent

Paper2Agent demonstrated that research papers and associated code/data/methods can be transformed into interactive agents, with environment setup, tool extraction and automated testing used to produce reliable MCP-based paper agents.

FrontierLab uses that development as prior art but asks a different Information Management question:

> What organizational and technical infrastructure is needed when many research artefacts become executable agents?

The extension therefore focuses on lifecycle and institutional concerns:

```text
Paper2Agent:
passive research artefact -> operable paper agent

FrontierLab IM extension:
operable research agents -> maintainable + traceable + governable research infrastructure
```

## References

- Miao, J., Davis, J. R., Zhang, Y., Pritchard, J. K. & Zou, J. **Reimagining research papers as interactive and reliable AI agents.** Nature (2026). DOI: 10.1038/s41586-026-11044-y.
- Paper2Agent repository: https://github.com/jmiao24/Paper2Agent


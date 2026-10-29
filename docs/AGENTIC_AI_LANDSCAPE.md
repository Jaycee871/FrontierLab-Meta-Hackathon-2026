# Agentic AI in drug discovery: what the field asks for, and where FrontierLab stands

Source paper: Zhao, Fang, Mao *et al.*, "The rise of agentic AI in drug discovery: from static tools to autonomous virtual scientists", *npj Drug Discovery* **3**, 43 (2026), Perspective. [doi:10.1038/s44386-026-00075-0](https://doi.org/10.1038/s44386-026-00075-0) · Related: [evidence graph](EVIDENCE_GRAPH.md) · [human review gate](HUMAN_REVIEW_GATE.md) · [verbatim evidence gate](VERBATIM_EVIDENCE_GATE.md) · [method evaluation](METHOD_EVALUATION.md)

This document does three jobs:

1. It distils the paper's framework: agent anatomy, topologies, the six-level autonomy spectrum, evaluation, and the call for full-chain traceability.
2. It places FrontierLab on that spectrum honestly, with evidence from the code.
3. It maps the paper's traceability argument onto what FrontierLab already does, names the real gaps, and ranks the changes that would close them.

It is a **docs-only** change. Nothing here is implemented, and no claim about FrontierLab goes beyond what the cited files do today.

> **Licence and quoting.** The paper is © the authors and published under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/), which does not permit sharing adapted material. So this document **does not redraw or adapt the paper's figures or tables**. Text in quotation marks, and the criteria cells in the autonomy table below, are verbatim and unmodified. Everything else is our own summary. Quoted material stays under the paper's licence and is excluded from this repository's MIT licence; see [NOTICE](../NOTICE) §9. Section names refer to the paper's own headings.

## 1. The paper in one paragraph

The paper argues that drug discovery is shifting from static, single-task models to LLM-driven agents that perceive, plan, call tools and remember across the Design–Make–Test–Analyze (DMTA) cycle. It gives a common vocabulary (anatomy, multi-agent topologies) and a six-level autonomy spectrum (Level 0–5). It then surveys systems stage by stage and assigns each one a level, and argues that today's benchmarks measure outcomes when they should be auditing processes. Its constructive core is a call for **full-link traceability infrastructure** (provenance, checkpoints, an error taxonomy) and **standardized process metrics** (Human Intervention Count, Autonomous Error Recovery Rate, Sub-task Completion Rate, cost). It concludes that no Level 5 system exists. In its view a "scientist-in-the-loop" co-pilot remains the practical model, and non-agent workflows are often better for deterministic routines (sections "Spectrum of agentic autonomy" and "Conclusion").

## 2. Vocabulary: anatomy and topologies

**Anatomy** (section "The anatomy of an AI agent", Fig. 2). The paper describes four modules:

| Module | What the paper covers | Paper's caution |
| --- | --- | --- |
| Perception | Text serialization (SMILES/SELFIES, sequences, SDF/CIF/PDB), vision-language models, and native scientific-modality models | Text serialization flattens 3D information. VLM benchmarks such as LiveProteinBench show bottlenecks in fusing modalities. |
| Reasoning & planning | Chain-of-thought, voting, tree search / MCTS, ReAct (reason → act → observe loop), Reflexion (task-level self-reflection stored as memory) | — |
| Tool use | Function calling, MCP, ToolUniverse, CodeAct (code as the action) | Biomni reports that CodeAct is more efficient on long-horizon tasks |
| Memory | Short-term memory (context window plus summarization) and long-term memory (vector DB / RAG, per-DMTA-cycle rationale and lessons) | — |

**Topologies** (Fig. 3). The paper names three:

- **Workflow** topologies: sequential, parallel, aggregation (voting or consensus) and iterative loop.
- **Swarm**: decentralized, peer-to-peer.
- **Supervisor**: a planner dispatches workers.

Its named failure modes are inter-agent misalignment, deadlock, communication cost and credit assignment. The remedies it proposes include agent-to-agent protocols, dynamic routing, and shared memory with consistency protocols, so that every agent works from a "single source of truth".

## 3. The six levels of agentic autonomy

The section "Spectrum of agentic autonomy" (Fig. 4, Table 1) builds on Gao *et al.* (Cell 2024, the paper's ref. 20). It grades systems along three dimensions: **scientific decision-making**, **system autonomy** and **human involvement**. The criteria below are quoted verbatim from Table 1:

| Level | Scientific decision-making | System autonomy | Human involvement |
| --- | --- | --- | --- |
| **0 · Task-Specific Tools** | No Planning: "Executes single deterministic algorithmic tasks." | Stateless: "Execution halts upon error; no tool-calling or orchestration capability." | Fully Driven: "Humans configure all parameters and initiate execution." |
| **1 · Assisted Pipelines** | No Planning: "LLM serves prediction/interpretation/evaluation/reporting modules, with no path decision-making." | Passive/Short-term: "Processes single-turn context only; relies entirely on human manual error correction." | Fully Driven: "Humans orchestrate the transitions and data flow between every step." |
| **2 · Task Controller** | Heuristic Planning: "Supports interactive multi-step reasoning (e.g., ReAct) and local decision-making." | Task-level Persistence: "Maintains task states; capable of API-level error recovery (e.g., automated retries)." | High-frequency: "Humans set goals and continuously monitor execution, providing real-time course correction." |
| **3 · Closed-loop Researcher** | Deep Planning: "Supports non-linear search and validation of local scientific hypotheses." | Feedback Self-correction: "Adjusts reasoning paths based on execution results or external evidence; memory integration is present." | Intervention at Key Junctures: "Humans provide goals and boundaries, intervening during result review or strategic shifts." |
| **4 · Self-evolving System** | Optimized Planning: "Continuously refines planning strategies and collaboration modes based on historical experience." | Evolutionary Experience: "Possesses cross-project experiential memory; autonomously creates or deploys new tools." | Periodic Oversight: "Humans intervene at key milestones or anomalous results to evaluate outputs and calibrate direction." |
| **5 · Virtual Scientist** | Full-stack Autonomy: "Proactively defines research questions, generates original hypotheses, and constructs entire trajectories." | Continuous Autonomy: "Long-term state maintenance; maintains exploration through re-planning and retrying despite failures." | Low-frequency Governance: "Humans focus on ethical review and strategic verification; daily execution is fully autonomous." |

Points from the surrounding prose that matter for us:

- Levels 0–1 are called pre-agentic, and "The real algorithmic divide appears at the Level 2."
- The key to Level 3 is "not in 'whether tools are used,' but in whether the system can continuously adjust strategies around a goal".
- The paper **defends Level 1** rather than dismissing it. It describes Level 1 as "neuro-symbolic synergy", in which the rigor of classical algorithms is used to curb LLM hallucination, and calls it "an irreplaceable and pragmatic pathway for the safe and interpretable integration" of LLMs.
- It reports that no Level 5 system exists and that the state of the art sits at Levels 2–4.
- *Naming caveat:* the paper does not label the levels consistently. Level 1 also appears as "augmented pipeline" and "Assistive Tools", and PharmAgents is labelled "Level 4 (Autonomous Scientist)". In this repository we use the Table 1 names only.

## 4. Where systems sit today (applications)

Table 2 and Fig. 5 assign levels to the systems the paper surveys. The examples below are the paper's own assignments, chosen because they are closest to what FrontierLab does:

| Stage | Examples and the level the paper assigns |
| --- | --- |
| Target discovery | AI co-scientist (L4), OriGene (L4), Robin (L3), AutoBA (L3). BioScientist Agent is **L1**: the LLM acts as a post-hoc interpreter and still produces gains. |
| Lead optimization | ChatChemTS (L2, ReAct), Fleming (L3). DeltaWave (L3) is an auditable platform that records the whole process in directed hypergraphs (ref. 58). |
| Retrosynthesis | LARC (**L1**, agent-as-a-judge), Synthegy (L1), RETRO-R1 (L2) |
| Automated experiments | Coscientist (L3). Without web search it hallucinated. |
| Integrated / general | PharmAgents (L4), Biomni (L3, CodeAct), STELLA (L4), Tippy (L3, DMTA over MCP) |

Each stage closes with a readiness assessment. For target discovery the verdict is "efficient research assistant", and humans remain indispensable for high-risk steps.

## 5. Evaluation, and why the paper wants full-chain traceability

**The benchmark ladder** (Fig. 7, Table 3) has four tiers:

- general cognition (GPQA, PubMedQA, HLE);
- task-specific (TDC, USPTO-50k, DUD-E);
- agent-specific (LAB-Bench, ScienceAgentBench, BixBench, RExBench);
- embodied (ScienceBoard, LabUtopia).

The paper argues that static Q&A scores can certify at most Level 1 or 2. It says evaluation must move "from a purely outcome-driven model to a process-auditable framework".

**"Process-oriented evaluation: fault analysis and full-link traceability."** The paper treats a white-box record of the execution process as "a critical criterion" for Level 3 and above, and cites three exemplars:

- **Claw-Eval** has 300 tasks. It cross-checks results against execution paths, server audit logs and environment snapshots, and reports that black-box evaluation misses 44% of safety violations.
- **TrajBench** injects more than 60k anomalies into trajectories. It finds that ReAct agents are poor at inspecting their own trajectories, and it tests rollback-and-retry.
- **AgentTrace** has 550 multi-agent fault scenarios. It builds a DAG of sequential, communication and data-dependency edges and traces back from a faulty node to its root cause. The paper calls this capability a prerequisite for Level 4.

The paper calls for traceability benchmarks specific to pharmaceutical research. On case studies, it warns that retrospective validation is exposed to data leakage and memorization, so evaluation should check "reasoning process validity" with causal evidence instead of matching a known answer.

**"Advocating for future infrastructure and standardized metrics."** This section makes the paper's concrete demands:

1. **Provenance tracking and checkpointing.** Record the whole process (for example as directed hypergraphs), keep state checkpoints, and support autonomous rollback.
2. **A standardized error taxonomy.** It has four classes: planning-level hallucination, tool-level interface failure, code-level syntax error and environment-level physical breakdown. Systems should emit fine-grained intermediate logs instead of terminal-only exceptions.
3. **Rigorous agentic ablation.** Compare the agent against a linear, non-agent pipeline that uses the same model and tools.
4. **Human Intervention Count (HIC)**, graded by severity: workflow approval, parameter correction and physical takeover.
5. **Autonomous Error Recovery Rate (AERR)** = self-corrected anomalies ÷ total runtime errors.
6. **Sub-task Completion Rate (SCR)**, with milestones.
7. **Cost and efficiency**: tokens, money and wall-clock time, compared with human experts.

**Safety** (Fig. 8) is organised into human, agent and societal layers. Developers should enforce "capability constraints, auditing mechanisms, and provenance tracking". On the user side the paper calls for "strict identity verification, behavioral monitoring". It also asks for toxicity screens that trigger refusal or human review, red-teaming, clear chains of responsibility, and safety benchmarks specific to drug discovery.

**Conclusion.** The paper wants HIC, AERR and SCR to become mandatory reporting. It describes the human role in a scientist-in-the-loop co-pilot as three duties: formalizing objectives and constraints, co-creating and auditing intermediate reasoning, and leading high-risk validation and authorization.

## 6. Honest self-assessment: FrontierLab is a Level 1 Assisted Pipeline

**Verdict: Level 1 (Assisted Pipelines), by design.** It is a deliberately constrained instance of the "neuro-symbolic synergy" that the paper defends. It is **not** Level 2. Below is each Table 1 criterion against the code:

| Criterion | What FrontierLab does | Evidence |
| --- | --- | --- |
| L1 decision-making: "LLM serves … modules, with no path decision-making" | **Met.** The model fills fixed roles: extraction, skeptic, hypothesis, method proposal and planning. Code decides the order, and every model output passes a deterministic gate. | [`research_backend.py`](../frontierlab/research_backend.py) `ROLES` allow-list; [`pipeline.py`](../frontierlab/pipeline.py) `run_research` → `continue_after_review` → `make_plan`; [`audit.py`](../frontierlab/audit.py) `validate_claims`, `enforce_citations` |
| L2 decision-making: ReAct-style multi-step reasoning, local decisions | **Not met.** The model never chooses a tool, a query or the next step. Retrieval is a plain function call on a query the user types. | `pipeline.run_research(question, query, …)`, `retrieve(query, max_papers)` |
| L1 autonomy: "relies entirely on human manual error correction" | **Met.** On any model failure the receipt is marked `FAILED_NO_RETRY` and the run raises. | `research_backend.py` (`"…no automatic retry"`); same policy in `llama31_baseline.py`, `muse_spark_open.py` |
| L2 autonomy: "API-level error recovery (e.g., automated retries)" | **Not met, deliberately.** FrontierLab does no retries, and a shared budget caps model calls at 8 per process. | `CallBudget(limit=8)` |
| L2 task-level persistence | **Partly.** `Run` holds the state of every stage, and changing the sources or the question invalidates downstream work. That state lives in one Streamlit session; nothing persists across sessions or projects. | [`models.py`](../frontierlab/models.py) `Run`; [`review.py`](../frontierlab/review.py) `save_review` resets hypotheses, evaluation and plan; `app.py` `st.session_state` |
| L3 memory / feedback self-correction | **Not met.** There is no long-term memory and no strategy adjustment based on results. A rejected claim is dropped; the system does not learn from it. | No memory module exists in `frontierlab/` |
| L1 human involvement: "Humans orchestrate the transitions … between every step" | **Met exactly.** Every stage transition is a human action: run, save the claim review, resume synthesis, save the method evaluation, tick the plan-approval checkbox, approve a plan step. | `app.py` buttons, forms and checkbox |

**Topology.** FrontierLab is a **sequential workflow**, not a supervisor or swarm system. Its "agents" are role prompts to one backend (`_same_backend`). The only communication between agents is the Skeptic's JSON passed into the Hypothesis prompt, and the Skeptic's *decision* field is set by a rule, not by the model (`continue_after_review`). One `Run` serves as the shared state, which is the paper's "single source of truth" pattern in its simplest form.

**What the human role already matches.** All three human duties from the paper's conclusion are built in: objectives (the question and the method-evaluation scope), auditing intermediate reasoning (claim-level review with rationale), and authorization (the plan gate and per-step approval). This is a strength in the paper's own terms, but it is a **human-involvement** property, not an autonomy level. FrontierLab's human gates *look like* Level 3's "Intervention at Key Junctures", but they exist because the system cannot move forward alone, not because it acts autonomously between those junctures.

**What it would take to reach Level 2** without weakening any gate:

- Let the model choose among a small, bounded set of actions inside a task, for example "refine the Europe PMC query" or "fetch more sources" when `risk_decision` returns `INSUFFICIENT_EVIDENCE`.
- Add a bounded retry or repair step on interface failures, such as malformed JSON, logged as autonomous recovery. This would make AERR meaningful.
- Keep task state across these steps while the human keeps setting goals and monitoring.

All model output would still go through the same evidence, citation and review gates. This directly conflicts with the current no-retry, 8-call policy, so it is an **owner decision**, not a cleanup task.

Level 3 would also need memory and hypothesis-driven re-planning. That is not realistic for this project, and FrontierLab should not claim it.

**Claim to make publicly:** *"Level 1 Assisted Pipeline in the sense of Zhao et al. (2026): a neuro-symbolic, human-orchestrated workflow in which deterministic evidence, citation and review gates constrain every model output."* Do not describe FrontierLab as an "autonomous agent", a "closed-loop" system or a "virtual scientist".

## 7. Full-chain traceability: what FrontierLab already has, and the gaps

The paper's traceability demands are stricter than most Level 1 systems meet. FrontierLab already covers several of them. The table maps each demand (sections "Process-oriented evaluation…" and "Advocating for future infrastructure…") to the code:

| Paper's demand | FrontierLab today | Gap |
| --- | --- | --- |
| Provenance tracking (DeltaWave-style process graph) | [Evidence graph](EVIDENCE_GRAPH.md) Paper ← Passage ← Claim ← Hypothesis ← PlanStep. Each edge is tagged EXTRACTED, INFERRED or AMBIGUOUS. A plan step can be approved only if its whole path is EXTRACTED (`evidence_graph.step_gate`). | Only **artifact** provenance is recorded. The graph contains no agent-call nodes and no link from a claim, hypothesis or step to the model receipt that produced it. The method evaluation and the Skeptic output are not graph nodes. |
| AgentTrace-style backward tracing from a faulty node | `step_gate` walks back from a step and reports each non-EXTRACTED edge as a blocking reason. In effect this localizes evidence faults. | Model calls do not appear in the graph, so a fault cannot be attributed to a specific call. The step → hypothesis edge means only that the plan and the hypothesis **cite a shared source ID**; it does not show the step was derived from that hypothesis (`build_evidence_graph`: "Plan cites a source this hypothesis cites"). |
| Full trajectory auditing with independent evidence chains (Claw-Eval) | Per-call receipts record role, reported model, input and output SHA-256, tokens, finish reason and elapsed time (`research_backend.py`). `run.log` records stage events. The whole run can be exported as JSON. | Receipts store hashes, not prompts or outputs, so a run **cannot be replayed** from its record. Log entries are not linked to receipts or graph node IDs. Rejected hypotheses survive only as a warning count (`continue_after_review`), and a plan blocked by the citation gate only as a log line. Failed paths are therefore under-recorded. |
| Checkpointing and rollback | A stage raises an error before it changes `Run`, so the last committed stage survives a failure. Changing sources invalidates downstream work. | Checkpoints are implicit; there is no versioned history and no explicit rollback. A rebuilt graph **silently drops** approvals that are no longer valid (`build_evidence_graph`, `previous=` loop), without logging the drop. |
| Standardized error taxonomy | Status strings such as `BLOCKED`, `FAILED_NO_RETRY`, `INSUFFICIENT_EVIDENCE`, `REVIEW_CONFLICT` and gate rejection reasons | These strings are ad hoc. Nothing classifies them as planning-level hallucination (for example an unknown citation ID or an unanchored quote) or tool-level interface failure (for example a NIM error, a schema failure, a model identity mismatch or an exhausted budget). The environment level does not apply, because FrontierLab does no wet-lab execution. |
| Auditing plus provenance plus "strict identity verification" (Fig. 8) | The reviewer name is required for step approvals. Claim reviews are bound to source fingerprints (`review.source_fingerprint`, `dataset_id`). | Approval records hold only `{reviewer, note, papers}`: **no timestamp, no hash of the step text, no verified identity** (`approve_plan_step`). `save_review` records **no reviewer identity or time**. The plan gate is a bare `approved=True` boolean with no attribution (`make_plan`). Claim reviews are not written to `run.log`. The reviewer recorded in `docs/runs/nim_claim_review_completed_20261028.json` was added to that file by hand, not by code. |
| Tamper resistance of the exported record | `load_graph` re-anchors every passage and EXTRACTED edge and re-runs `step_gate` on every approval, failing closed. | We checked this locally against the code on `main` (0adcfb3). A hand-edited `graph.json` **can inject an approval with an empty reviewer and an empty note** onto any step that already passes the gate, and `load_graph` accepts it. An abstract, passage and quote rewritten **consistently** inside the graph also pass, because passages are checked against the abstract stored in the graph itself, not against `source_fingerprint`. (Injecting an approval onto a *blocked* step is correctly rejected.) |
| HIC, AERR, SCR, cost | The raw data exists: review labels and notes, the evaluation, approvals, and tokens and elapsed seconds in receipts. `llama31_baseline.py` lists `researcher_intervention_rate` as a benchmark dimension. | None of these metrics is computed or reported for a FrontierLab run. AERR would be **0 by design** (every runtime error halts), and it should be reported as such rather than omitted. |
| Rigorous agentic ablation against a linear pipeline | README milestone 3 plans a gate ablation: no gate, then source and quote checks, then checks plus human review, with the same model and cases. This is the comparison the paper asks for, applied to gates instead of agency. | It has not been run yet. FrontierLab is itself already a linear pipeline, so the honest ablation is *gates vs no gates*, not *agent vs non-agent*. |
| "Reasoning process validity" over outcome matching | A quote must be located verbatim, and the docs state that EXTRACTED is not entailment (`claim_verification.audit_predictions`, `scientific_entailment_verified: False`). | Evidence comes from **abstracts only**, which limits how deep a reasoning check can go. |

**Summary.** FrontierLab has the *skeleton* of the paper's traceability infrastructure: artifact provenance, path-level gating, hashed call receipts, invalidation on change and a white-box export. The genuine gaps are:

- **Attributable, timestamped human-intervention records**, which also block HIC.
- **Integrity of the exported record**: approval contents and upstream source binding are not re-checked when a graph is loaded.
- **Process-level coverage**: agent calls, failed paths, the method evaluation and the Skeptic output are missing from the graph, and the run cannot be replayed.
- **A shared error taxonomy and the process metrics** themselves.

## 8. Recommendations (ranked; not implemented here)

The ranking puts first whatever most improves traceability per hour without loosening any gate. The pre-deadline set fits before the submission deadline of **2026-11-05 10:00 (Asia/Taipei)** ([final sprint plan](HACKATHON_FINAL_SPRINT.md)). None of these items requires new model calls.

### Pre-deadline

| # | Change | Paper hook | Effort |
| --- | --- | --- | --- |
| 1 | **Close the `load_graph` approval hole.** Re-validate the reviewer and note on load. Add `approved_at_utc` and the SHA-256 of the step text plus gate papers to each approval record, and reject records whose hash does not match. | Auditing mechanisms; identity and provenance (Fig. 8) | ~1 h: about 20 lines plus 3 tests (empty-reviewer injection, hash mismatch, round trip) |
| 2 | **Record every human intervention as an attributable event in `run.log`** (claim review saved, method evaluation saved, plan gate approved, step approved, stale approval dropped). Each event carries a UTC time, a reviewer field and the artifact ID it binds (`dataset_id`, `evaluation_id`, step ID). | HIC; clear responsibility chains (Fig. 8) | ~1–2 h: touches `review.py`, `pipeline.make_plan`, `evidence_graph`, `app.py` |
| 3 | **Process metrics panel and export**, as a pure function of `Run`: HIC by severity (approval vs correction, where CONTRADICTED/INSUFFICIENT verdicts and edited methods count as corrections), SCR over the five stages, AERR reported as "0 of N runtime errors, no autonomous recovery by design", plus tokens and wall-clock time from the receipts. | HIC, AERR, SCR, cost | ~2–3 h, depends on #2 |
| 4 | **Error-taxonomy field** on every BLOCKED/FAILED log entry and on every rejected claim, hypothesis or plan. Use the paper's four classes, plus `EVIDENCE_INSUFFICIENT` and `HUMAN_REJECTED` kept separate, since those are outcomes rather than faults. | Standardized error taxonomy | ~2 h: an enum and mapping in one module, call sites, tests |
| 5 | **Bind the graph to its upstream sources.** Put `source_fingerprint` on paper nodes and the review `dataset_id` and `evaluation_id` in the graph header. Add an optional `load_graph(..., run=)` that verifies them against a live `Run`. | Provenance tracking | ~1–2 h |

### Future work

| # | Change | Paper hook | Effort |
| --- | --- | --- | --- |
| 6 | Run the planned **gate ablation** (README milestone 3) and report abstention, intervention and cost per arm | Rigorous agentic ablation | ½–1 day plus live model calls under the 8-call budget |
| 7 | Add **agent-call nodes** to the graph (receipt hash and role), with produced-by edges to claims, hypotheses and steps, and sequential edges between calls | AgentTrace DAG; fault attribution | ~½ day |
| 8 | Put the **method evaluation, Skeptic output, rejected hypotheses and blocked plan attempts** in the graph, so failed paths are first-class | Full trajectory auditing | ~½ day |
| 9 | Store prompts and raw outputs as content-addressed blobs next to the receipts, so runs can be **replayed**. Add explicit versioned checkpoints. | Checkpointing; replay | ~1 day; check the licence of stored abstracts first |
| 10 | Require plan steps to **cite hypothesis IDs explicitly**, and anchor them, instead of relying on shared source IDs | Reasoning process validity | ~½ day plus prompt and schema change |
| 11 | **Verified reviewer identity**, for example sign-in on the hosted Space, with signed approvals | "strict identity verification" | 1–2 days |
| 12 | A **domain safety screen** (dual-use and toxicity) before planning, routed to human review | Safety, Fig. 8 | 1–2 days plus policy design |
| 13 | **Full-text evidence** (open-access full text) behind the same verbatim gate | Perception depth | 2+ days |
| 14 | **Bounded Level 2 move**: model-proposed query refinement and one logged repair retry, still behind every gate. Owner decision, because it reverses the no-retry policy. | Level 2 criteria; makes AERR non-trivial | 1–2 days |
| 15 | Cross-run memory of rejected claims and reviewer lessons (a step toward Level 3), visible and gated | Level 3 memory integration | Research-scale; not recommended for this project |

## 9. What this document does not claim

- It does not claim any benchmark score, measured HIC, AERR or SCR for FrontierLab. None has been computed.
- The paper's level assignments for other systems (§4) are the paper's own. We have not verified them.
- The `load_graph` findings in §7 come from a local check against `main` at 0adcfb3. That check is not part of the test suite. Recommendation #1 would add it as tests.
- Effort estimates are rough guesses for one developer familiar with the codebase.

## Prior art and credit

- Zhao D., Fang M., Mao L., Zhu Y., Su Q., Shi H., Xu H., Li L., Hou T. & Hsieh C.-Y. "The rise of agentic AI in drug discovery: from static tools to autonomous virtual scientists." *npj Drug Discovery* **3**, 43 (2026). [doi:10.1038/s44386-026-00075-0](https://doi.org/10.1038/s44386-026-00075-0). Licensed [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/). Quoted verbatim with attribution; no figures or tables adapted.
- The autonomy spectrum in that paper builds on Gao S. *et al.*, Cell (2024), the paper's ref. 20. We cite it through the paper and have not read it independently.
- Claw-Eval, TrajBench, AgentTrace and DeltaWave are referenced as the paper describes them. We have not evaluated them.

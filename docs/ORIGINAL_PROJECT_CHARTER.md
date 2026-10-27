# FrontierLab · Original Project Charter

**Source of truth:** the applicant's original 2026 Meta Global AI Developer Hackathon project description, as documented in the user's 15-slide presentation script `Meta_Hackathon_2026_口頭報告講稿(1).docx`, particularly slides 6, 7, 12 and appendices. This file preserves the original intent; it does NOT rewrite the submitted application or assert that all stages are already implemented.

## Original project identity

- **Name:** FrontierLab.
- **Hackathon:** Meta Global AI Developer Hackathon 2026, Indie Developer Track, with a scientific/biomedical prototype aligned to the Push the Frontier theme.
- **Mission:** help a researcher turn a concrete scientific question into an evidence-grounded, testable research hypothesis and a researcher-reviewable experiment plan.
- **Agentic method:** different AI agents search literature, examine reproducibility, evaluate candidate methods and uncertainties, and help compose the workflow. The human must be able to inspect sources, intermediate steps and important decisions and intervene.
- **Initial demo domain:** biomedical research; the original presentation suggests assessing whether a protein design method merits further testing.

## The five-stage product contract — DO NOT REPLACE

| Original stage | Expected visible capability | Correctly bounded output |
| --- | --- | --- |
| 1. Research | User sets a scientific question and comparison scope | Clearly stated question, objective and assumptions |
| 2. Evidence | Retrieve relevant papers and source information, inspect supporting/contradictory evidence | Citation-linked literature catalog; provenance and uncertainty visible |
| 3. Hypothesis | Produce scientifically falsifiable hypotheses grounded in retrieved evidence | Each hypothesis links back to sources and flags unverified inferences; no fake scientific discovery |
| 4. Evaluation | Examine reproducibility, candidate methods, methodological limitations and uncertainty | Side-by-side candidate and risk assessment, explicit failure/insufficiency outcomes; scientific tool results must be proven to have actually run before treated as evidence |
| 5. Planning | Assemble a reviewed research plan | Experimental question, evaluation criteria, proposed controls, falsification paths and researcher approval; draft, NOT an executed wet-lab experiment |

## Original four design principles

1. **Transparent evidence:** expose references, provenance, reasoning inputs and intermediate decisions.
2. **Reproducibility:** make methods, settings, workflows and validation limitations inspectable.
3. **Uncertainty evaluation:** present insufficient evidence, conflicting results, limitations and uncertainty instead of ungrounded consensus.
4. **Researcher intervention:** reserve meaningful review/approval points; do not bypass a human decision.

## Applicant's prior technical experience — not a claim about current FrontierLab outputs

The original application showcased the applicant's work in an Anthropic × Adaptyv pH-switchable protein-binder challenge: RFdiffusion backbone generation, ProteinMPNN sequence design, Boltz-2 structure prediction / screening, PROPKA pH-related residue-property analysis, novelty checking and human/mouse target comparison. This was the **earlier project used to demonstrate skills**, not proof that FrontierLab has performed successful biological design or a new wet-lab validation.

## Current development mapping (v0.12, 2026-10-28)

| Original promise | Current verified implementation | Important gap |
| --- | --- | --- |
| Research question | Question input / modes in Streamlit | End-user usability to be checked on latest deployed image |
| Evidence | Europe PMC public abstracts, plus tested small Springer Nature discovery workflows; source-ID/quote checks | Source quality, full-text rights and claim semantics require independent review |
| Hypothesis | Synthetic illustration and human-gated live pipeline code | Genuine Meta model inference not yet verified |
| Evaluation | Verbatim excerpt gate, human annotations, source-bound method comparison, reproducibility-documentation review, selection/deferral, failure lab and offline BioNeMo preflight | Real model outputs, executed paper reproduction and independently validated method comparisons remain missing |
| Planning | Synthetic demonstration and human-approved draft path requiring a current method evaluation; selected-method constraints, controls, metrics, replication and falsification are retained | End-to-end live approved plan using genuine Meta outputs not yet demonstrated |

## How newer work must relate to the original contract

- **Evidence Gate and Human Review v0.8–v0.9:** essential supporting components for Evidence / Evaluation.
- **Research Failure Lab v0.11:** Eval test harness, **NOT** the entire competition product or a standalone scientific breakthrough.
- **NVIDIA BioNeMo v0.10:** optional scientific computation tool within Evaluation; not a replacement for Meta model inference or the five-stage workflow.
- **OpenCode v0.7 / OpenShell:** development tooling and isolation exploration, not product-level capabilities without running and verifying them.
- **Paper2Agent / AlphaZero teachability / advanced biomedical benchmarks:** literature-inspired future extensions; do not let these displace the hackathon's five stages.
- **Meta Muse Glimmer / eligible Meta open weights:** actual Meta model integration remains the highest-priority execution blocker for an authentic Meta-powered Demo.

## MVP acceptance criteria for actual entry

- A judge can pose a biomedical research question and observe the **entire Research → Evidence → Hypothesis → Evaluation → Planning** path, including justified stops when evidence is insufficient.
- At least one genuine, dated Meta model inference run has identity, authentic content, limitations and reproducible logs. Mocked output must be clearly marked.
- The Evaluation stage explicitly compares candidate methods or explains why a comparison is not currently supportable; a passed software test is not scientific validation.
- Researcher can review evidence and approve or veto the conceptual plan; no bypass.
- HF public Demo and a short video demonstrate only real implemented behavior. Cite code and original data, and report honest shortcomings.
- Original proposal remains unchanged: the project is NOT primarily a tool for breaking Agent rules, an autonomous wet lab, a protein binder submission, or a generic literature chatbot.

## Change-control check before accepting new features

**Question:** Which of the five original stages and four principles does this improve, and what measurable demonstration will show that? If neither can be answered, defer the feature until after the hackathon.

Original plan remembered and preserved, while research methodology and truthful verification may continue to evolve. Never equate this charter with completion of all promised features.

## v0.12 scope completion work

[Method evaluation and planning](METHOD_EVALUATION.md) adds the missing explicit fourth stage. Method documentation and comparisons are researcher-assessed; optional model suggestions remain unverified live. This closes a software workflow gap, not the empirical validation gap. Original five-stage scope and four principles remain unchanged.


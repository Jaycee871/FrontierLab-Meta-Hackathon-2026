# Method evaluation and research planning

Implemented in v0.12, October 28, 2026 (Asia/Taipei).

FrontierLab now has an explicit Evaluation step between hypotheses and planning. A researcher records alternative methods, their reproducibility documentation, applicability and uncertainty, then selects a method with a rationale or defers. A conceptual plan carries the saved decision and unresolved checks.

This implements a review workflow. It does not demonstrate executed paper reproduction, independent scientific assessment, real Meta inference or experimental protein performance.

## Why this belongs in FrontierLab

The original application described literature retrieval, hypothesis generation, reproducibility checks, candidate evaluation, uncertainty information and experiment planning. Evidence quotation checks alone do not answer whether a research method is sufficiently described or worth testing.

The applicant's protein-design experience gives this workflow a concrete context. The Anthropic × Adaptyv competition describes multi-criterion design selection, including novelty and diversity, with human approval and subsequent experimental characterization. FrontierLab uses that as domain context, not as evidence of why Meta accepted the application or as a claim of partnership.

Official sources consulted October 28, 2026:

- [Competition overview](https://proteinbase.com/competitions/anthropic-adaptyv-2026)
- [Design selection](https://proteinbase.com/competitions/anthropic-adaptyv-2026/selection)
- [EGFR challenge and experimental objectives](https://proteinbase.com/competitions/anthropic-adaptyv-2026/challenges/egfr)

The current comparison assesses research strategies, not individual sequences. Structural confidence does not establish affinity, pH selectivity, cross-species binding or receptor activation. Complementary tools such as RFdiffusion and ProteinMPNN should not automatically be treated as competing methods. No new protein sequences or scientific tool calls are produced by this module.

## What a candidate record contains

- A method ID and name.
- Source IDs from the reviewed literature set.
- Applicability: target, assay conditions, dataset or other comparison boundaries.
- Reproducibility documentation for data/inputs, code/model version, environment, parameters/seeds, protocol/controls and evaluation metrics.
- Expected research value, required resources, validation requirements, limitations and novelty/diversity evidence.

Each reproducibility item is **unknown**, **missing**, **documented** or **not applicable**. Documented items require an explanation and location/reference. Missing and not-applicable judgments require an explanation. Unknown is valid when the available material cannot answer the question.

These entries are researcher assertions. The application does not fetch and verify the referenced artifact, check licenses, provision an environment or run the original paper's code. Even complete documentation receives DOCUMENTED_NOT_EXECUTED, never a reproduction-success label.

The model can optionally propose up to two candidate descriptions using the current abstracts and reviewed claims. Proposals must use permitted source IDs; every reproducibility field still starts unknown. Suggestions do not save or approve an evaluation. Actual local Meta inference for this path remains unverified.

## Decisions and uncertainty

A comparative selection requires at least two candidate records, a known selected method and an explanatory rationale of at least eight characters. The researcher chooses; the software does not compute an automatic winner or a calibrated success probability.

With zero or one candidate, or with insufficient comparative evidence, the researcher can save a deferral and explanation. Planning remains blocked.

The evaluation exports source coverage, machine-flagged tensions, applicability, missing documentation and a clear separation between reviewer assessment and verified scientific execution. Unresolved documentation is allowed in a conceptual plan, provided it remains visible as work to address.

Source-ID validity is not proof that a cited paper describes the proposed method or establishes its superiority. That interpretation still needs researcher review, often using the full methods.

## Binding decisions to the current research state

Each evaluation binds to:

- Research question, mode and model label.
- Source snapshots and claims.
- Human review decisions and the generated hypotheses.
- Saved candidate records, selection and rationale.

Changing these makes the saved evaluation unusable for planning. Re-entering human review clears hypotheses, evaluation and plan; regenerating hypotheses clears evaluation and plan; saving a new evaluation clears the previous plan.

The evaluation digest detects a changed record in the workflow. It is not identity authentication, a signed expert judgment or provider attestation.

## Planning contract

Planning requires a current evaluation with a selected method and explicit researcher approval. The live model receives the selected method, rationale, open checks and uncertainty. A draft must include:

- Objective and proposed steps.
- Controls and evaluation metrics.
- Replication and falsification criteria.
- Citations covering the selected method's sources.
- Limitations.

The application attaches the saved evaluation ID, selected method, rationale and unresolved checks to the plan. Model text cannot overwrite those fields or turn the draft status into a validated finding. The schema checks do not prove that the generated prose adequately addresses every scientific issue.

## Try both paths without a model

1. Start Streamlit and run **Synthetic audit demonstration**.
2. In **4 · Method evaluation**, inspect the two explicitly fictional strategies.
3. Select M1 or M2, enter a rationale and save the evaluation.
4. Inspect the comparison table and unresolved checks.
5. Approve a draft and generate the synthetic plan; download the provenance JSON.
6. For the failure path, save DEFER with a rationale, optionally reducing the candidate count to zero. The plan button stays disabled.

The fictional comparison can illustrate matched-condition replication versus cross-assay confirmation. It is not a report of real laboratory work or an empirically established ranking.

## Verification

Run `python -m pytest -q`.

Tests cover omitted evaluation, insufficient comparison, invented references, undocumented material, changed evidence/hypotheses/decisions, downstream invalidation and plan constraints. Streamlit AppTest exercises actual synthetic-mode selection, draft generation and deferral without network or model calls.

The public HF Space needs a separate rebuild to display this version. No new API key, secret-enabled push workflow, billed Meta call or GPU job is introduced.


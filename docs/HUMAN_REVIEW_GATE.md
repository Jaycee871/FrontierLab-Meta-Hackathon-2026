# FrontierLab v0.9 — Human-Gated Claim Validation

Prepared 2026-10-27. This is a software workflow and UI implementation, **not** an experimentally validated science result. No live model inference has been run by this change.

## The change in research policy

Before, a generated claim with a matching source ID and verbatim excerpt could immediately enter hypothesis generation. Now the live pipeline stops at HUMAN_CLAIM_REVIEW_REQUIRED after extraction until manual semantic review.

Each source-bound review packet contains a deterministic case ID, paper DOI/title/URL, proposed claim and stance, exact abstract excerpt, and a separate reviewer-supplied semantic verdict. Verdicts: PENDING, SUPPORTED, CONTRADICTED, INSUFFICIENT. Rejected and insufficient items require explanatory notes.

SUPPORTED means that a human reviewer judges the excerpt to support that particular claim *within the cited scope*. It does not establish real-world scientific truth, methodological quality, or an independently adjudicated label.

## Three gates

1. All quote-matched model claims must have a non-PENDING verdict.
2. At least two distinct source papers must have a reviewer SUPPORTED label.
3. A genuine model connection must be available to resume provisional skeptical synthesis and hypothesis generation.

Only reviewer-supported source IDs are passed to further model agents or to a draft research plan. The raw algorithmic conflict/tension reports remain visible; conditional results across different assays are NOT necessarily logical contradictions.

## User interface and retention

The Streamlit UI now provides a per-claim review form and downloadable blank/annotated JSON packets. Session changes alone are not a durable private archive: use the JSON download. The human labels are not automatically verified as independent domain-expert judgments. The public HF CPU Space loads no model itself. Since v0.39–v0.40 it offers **Live Meta Muse (via Hugging Face)**: when the Space owner has set a Hugging Face token as a Space secret, it calls Muse Spark Open through Hugging Face Inference Providers, with Muse Glimmer as the configured fallback, under a 6-call per-session and per-process daily cap; without that token the mode is labelled unavailable. Claims from that live path enter this same review gate as PENDING. New code reaches the Space only through the manual `Deploy FrontierLab to existing HF Space` workflow, which uploads a revision-bound snapshot and triggers the Docker rebuild.

## Proposed future publishable evaluation

- Curate 30–50 legally reusable abstracts with pre-registered claim scope and hard negatives.
- Obtain two blinded domain-capable reviewer judgments per claim; adjudicate disagreements.
- Score 3-way claim entailment per class, quote coverage, abstention, contradiction transparency, human audit time and reviewer agreement.
- Preserve failed retrievals, null outputs, rate limits, inter-rater disagreement, and uncertainties instead of only successful cases.
- Never put Nature+ subscription full-text PDFs or secrets into a public Space.

## Verification

See frontierlab/review.py, frontierlab/pipeline.py, app.py, tests/test_human_review.py and tests/test_pipeline.py. Run python -m pytest -q. This code change uses neither Meta Platforms billed API nor NVIDIA NIM GPU/trial inference.

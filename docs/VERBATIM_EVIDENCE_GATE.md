# FrontierLab v0.8 — Verbatim abstract grounding before scientific synthesis

Date: 2026-10-27. Implemented in code; the published Hugging Face Space requires a Docker image rebuild before displaying this change.

## Why this matters

A DOI that exists and a model-generated statement are not proof that the statement is present in, or supported by, the paper. The prior live pipeline checked source IDs only. It might allow a fabricated "supported" claim (whose DOI happened to be valid) into skepticism and hypothesis generation.

## Live research mode: fail-closed extraction

The extraction agent is now instructed to return, for every claim:
- paper_id: EXACT source identifier supplied in the prompt
- claim_key, stance, statement, limitation
- evidence_quote: exact verbatim 24–500 character passage from that paper's supplied abstract

The deterministic gate checks:
1. Is the cited paper_id from the retrieved catalog?
2. Is the claim format valid?
3. Does the quoted passage appear contiguously (ignoring case and whitespace normalization) in that exact paper's abstract?
4. If absent, too short, malformed, from a different paper, or invented: reject the claim **BEFORE** it enters the skeptic or hypothesis stages.

A quote match is proof of source text presence ONLY. It does not establish that the paragraph entails the claim, that methodology is reliable, or that scientific consensus exists. Every live accepted claim stores `evidence_quote` and `passage_matched` for researcher inspection. All accepted claims require independent human review before use as actual science.

The built-in synthetic demo does not require quotes: it exists solely to show deterministic conflict flagging and cannot be passed off as live scientific evaluation.

## Limitations and next tests

- A model can cite a real quote and make the opposite inference. Code regression tests intentionally demonstrate this case. Reliable semantic entailment requires independent human annotations, and/or a validated claim-to-evidence NLI classifier with uncertainty calibration.
- Treat cross-assay disagreements as conditional tensions, not automatic logical contradictions.
- No guarantee that current real live model backend succeeds. The paid Meta Model API stays disabled. Existing NVIDIA Muse Glimmer trials returned no final answer; v0.6.1 low-reasoning and 2048-token correction is not yet tested live.
- No restricted Nature+ subscription articles are uploaded, used in public AI prompts or published in the repo.

## Verification

```bash
python -m pytest -q
```

Regression tests cover:
- valid cited quote, nonexistent quote, quote borrowed from a different study, missing quote, tiny quote and malformed quote
- maliciously asserted conclusions rejected if quote absent even when DOI is real
- quote present but scientific entailment still unverified
- original synthetic demo continues to work without affecting the real-world gate

Publish this change to HF Space only after successful GitHub CI, then rebuild the CPU Basic Docker image from the new main branch. No new secrets or paid hardware are needed.
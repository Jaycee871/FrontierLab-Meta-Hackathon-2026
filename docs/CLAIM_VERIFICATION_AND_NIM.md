# FrontierLab · Claim-to-Evidence Evaluation and Meta Model Path

Date: 2026-10-27. Code baseline status: synthetic benchmark and NVIDIA Muse Glimmer NIM client ready for **manual** trial. Two real NVIDIA API requests were made, but neither returned final-answer text; genuine model output is NOT yet verified.

## Research foundation (PDFs in Undermind workspace)

Undermind FrontierLab folder: https://app.undermind.ai/projects/362994e3-20f1-4bb8-9984-9a088a13c27f?path=/frontierlab-core-papers/
Reading notes: https://app.undermind.ai/projects/362994e3-20f1-4bb8-9984-9a088a13c27f?path=/frontierlab-core-papers/READING_NOTES.md

- Rasheed et al. (2026), DOI 10.48550/arXiv.2602.13855: proposes claim-level auditability as a research target, including provenance coverage/soundness, contradiction transparency, human audit effort. These are PROPOSED metrics, not independently proven by the paper's illustrative diagram.
- Tang et al. (EMNLP 2025), DOI 10.18653/v1/2025.emnlp-main.83: citation bibliographic match must be distinguished from claim-to-passage support; the paper shows that even real-looking references may be fabricated.
- Gottweis et al., Nature (2026), DOI 10.1038/s41586-026-10644-y: scientific Co-Scientist's multi-agent refinement/evaluation and human-in-the-loop safeguards; automated Elo is not ground truth.
- Mitchener et al. (2025), DOI 10.48550/arXiv.2511.02824: Kosmos scientific workflow and provenance.

## Implemented now

- frontierlab/claim_verification.py enforces real source-ID lookup and exact passage-in-abstract checks. Without the right exact source snippet, it rejects affirmative decisions (defaults to INSUFFICIENT).
- Test claims are labeled by a human author in frontierlab/claim_benchmark.py and are **entirely fabricated**. The two deliberately erroneous predictions demonstrate why source-ID checking and passage matching alone are not entailment.
- Against the hand-authored ten-case fixture, the test has 9/10 known IDs, 7/10 exact passage anchors, and 8/10 agreement with synthetic labels. These are code coverage / hand-authored agreement indicators, **not AI accuracy, scientific validation or independent annotation**.
- Conflict transparency is measured as recall against explicitly annotated contradiction pairs, never treated as 100% when no human gold labels exist. A disagreement across different assay conditions is a test case for CONDITIONAL tension, not proof of a logical contradiction.
- Public HF app will show the audit fixture only **after the HF Docker Space is rebuilt**. GitHub updates by themselves do not change a running Space image.

## Next: genuine Meta Muse Glimmer sample via NVIDIA (no Meta Platforms API)

NVIDIA's official listing provides an endpoint for meta/muse-glimmer-30b:
https://build.nvidia.com/meta/muse-glimmer-30b

Use the one-request, synthetic-only GitHub Actions workflow:
https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/workflows/nvidia-muse-trial.yml

It uses the existing repository secret **NVIDIA_API_KEY**. The workflow must be manually triggered. It sends one short FICTIONAL prompt to the fixed HTTPS endpoint https://integrate.api.nvidia.com/v1/chat/completions with max_tokens=2048, low reasoning effort, model-recommended sampling and no retries. No Nature+ paid full texts, HIPAA/PII, or actual secret values are sent in the prompt. There is no Meta Platforms API call. NVIDIA's developer free prototype tier may have quotas, changing terms and account-specific restrictions; verify your account does not permit overage charges before running.

If the run returns REAL_INFERENCE_RETURNED and a model label / cryptographic output digest, it shows a real Meta model call at NVIDIA's endpoint, but does **not** yet demonstrate research accuracy or hackathon compliance. A more complete benchmark must then perform blinded human-supported claim entailment on open-licensed source excerpts.

There is intentionally no automatic secret-enabled NVIDIA job on push/PR. Any possible trial error is redacted to prevent leaking Authorization headers.

Do NOT upload API keys or protected scientific PDFs into a public Hugging Face Space.

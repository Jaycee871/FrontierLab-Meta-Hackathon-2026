# Recorded Meta structured-output checks

Two genuine NVIDIA NIM requests were completed on October 28, 2026 (Asia/Taipei), using meta/muse-glimmer-30b. These establish a bounded data path from published excerpts to structured predictions and deterministic passage checks. They do not establish scientific accuracy or a complete live FrontierLab research run.

| Run | Input | Result | Elapsed | Tokens |
| --- | --- | --- | --- | --- |
| [Single-case JSON](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40563411852) | R07 / PMC4314675 abstract excerpt | Strict JSON, expected IDs and exact source quotation passed | 5.126 seconds | 328 input + 198 output = 526 |
| [Twelve-case batch](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40563954658) | All 12 pilot cases in one joint context | 12 structured predictions, 8 matched source quotations, 4 insufficient-evidence responses | 11.168 seconds | 838 input + 956 output = 1,794 |

Total for these two requests: 2,320 tokens. Token counts are not a dollar-cost estimate. No Meta Platforms billed Model API call was made.

## What was actually checked

The single-case check rejects unknown fields, duplicate JSON keys, wrong case/source IDs, invalid labels, malformed explanations, unmatched quotes, truncated output and missing model identity.

The batch check requires all twelve case IDs exactly once and preserves the model's raw labels. The passage auditor then checks the specified source and excerpt. Eight responses with SUPPORTED or CONTRADICTED labels carried matching quotations; four returned INSUFFICIENT without quotations. Those four are abstentions, not four quote failures or four wrong answers.

Draft AI-authored reference labels and rationales were excluded from both prompts. Researcher annotations remain pending, so accuracy/agreement metrics remain null. The twelve-case request is one joint-context batch, not twelve independent model trials, repeated-run reliability testing or a held-out generalization benchmark.

The excerpt data includes full citation and rights metadata in [the pilot dataset](../datasets/real_ph_excerpt_cases_v1.json). The selected single case is from the CC BY 3.0 Traxlmayr article, DOI 10.1002/biot.201300483. Historical antibody-engineering methods are background; no current de novo protein competition eligibility or biological effectiveness is inferred.

## Reproducible records

- [Single-case receipt](runs/meta_nim_json_20261028.json)
- [Batch receipt and original final output](runs/meta_nim_pilot_20261028.json)
- [Batch prediction packet](runs/meta_pilot_predictions_20261028.json)

Input and original final-output SHA-256 digests were reconstructed and checked locally against the logged receipts. The records include model identity, finish reason, usage, timing, input snapshot, code revision and GitHub run link. They contain no API credentials or hidden reasoning.

The generic imported-prediction auditor does not attest to provider execution. Its conservative provenance flags remain unchanged; the surrounding receipt provides the actual GitHub/NVIDIA run evidence.

Both dedicated branch-scoped triggers were disabled after queuing their single authorized request. They were not added to the default branch. The scripts on main require explicit environment opt-ins and make no retries; normal tests use stubs and make no model calls.

## Inspect with the existing offline evaluator

```bash
python -m scripts.real_literature_benchmark --kind evaluate --predictions docs/runs/meta_pilot_predictions_20261028.json
```

The report should show total=12, reviewed=0, quote_anchor_count=8, gate_abstentions=4 and metrics=null until a complete researcher review is supplied.

Next work is independent claim review, matched model/gate comparisons and integration of the tested model path into the five-stage researcher-controlled workflow. The local llama.cpp backend and the complete live Streamlit pipeline remain unverified. An HF rebuild is separate from a repository update; recorded outputs must remain clearly labeled when shown in a demo.

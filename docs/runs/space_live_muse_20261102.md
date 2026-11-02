# Live Meta Muse run on the deployed HF Space — 2026-11-02

**Source of this record:** transcribed from the *Model request receipts* panel and run summary in the public Space's browser UI. This is **not** an exported provenance receipt file (no `export_json` output was saved), so there are no input/output SHA-256 values or UTC timestamps here. The screenshot [`space_live_muse_20261102.png`](space_live_muse_20261102.png) shows the sidebar, the run summary and the top of the receipts panel.

| Field | Value |
| --- | --- |
| Recorded | 2026-11-02, about 16:13 Asia/Taipei, via the browser UI |
| Space | `Jaycee766/FrontierLab-Meta-Hackathon-2026`, Space commit `94bc1eb3cf8d216c17573fe958fa2ec01bef885d` |
| Deployed version / source | v0.40 / `6f0f7d2431548621c3f2481939823058d2b9a72d` (main, PR #37) |
| Sidebar mode | **Live Meta Muse (via Hugging Face)**, listed as available (no "unavailable" suffix); consent box ticked |
| Research question | app default ("How might pH-dependent protein binder affinity be evaluated reproducibly?") |
| Europe PMC query | `EXT_ID:42959777 AND SRC:MED` |
| Maximum live abstracts | 1 |
| Paper | MED:42959777 — BIGH3 pH-dependent antibody engineering (2026) |
| Backend | `hf-inference-providers` (router `https://router.huggingface.co/v1`) |
| Primary model | `meta-models/Muse-Spark-Open-816B-A42B`, provider requested `baseten` |
| Reported model | `meta-models/muse-spark-open`; `model_identity: MATCHED` |
| Fallback | `meta-models/Muse-Glimmer-30B` configured, **not used** |
| Attempted calls | 1 |
| Status | `JSON_OBJECT_RETURNED`; `finish_reason: stop`; input not truncated |
| Elapsed | 23.07 s |
| Tokens | prompt 810 · completion 3,903 (of which 3,578 reasoning) · total 4,713 |
| Request settings | `max_tokens` 8192, temperature 0.2, `max_abstract_chars` 3000, session cap 6, daily cap 60 |
| Claims | 2 verified, both `supports`: `kd_ec50_ph_dependent_affinity_comparison`, `biophysical_in_vitro_ph_target_engagement` |
| Conflicts / rejected claims | 0 / 0 |
| Decision gate | `INSUFFICIENT_EVIDENCE` (single source; hypothesis generation correctly stopped) |
| Runtime failures | 0 |
| Call counters | session 6/6 → 5/6 left; daily 60/60 → 59/60 left |

## Interpretation limits

- The evidence quotes passed **passage grounding** against the cited abstract (verbatim match). Semantic entailment is **not** verified; researcher review of the claims is pending.
- One paper, one call: this is an execution record showing the live path works on the public Space, not an accuracy or benchmark result.
- `INSUFFICIENT_EVIDENCE` is the expected, correct outcome with a single source.

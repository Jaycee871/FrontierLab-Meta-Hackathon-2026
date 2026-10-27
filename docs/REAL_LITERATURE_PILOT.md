# Real literature excerpt pilot

Prepared October 28, 2026 (Asia/Taipei), v0.13.

This pilot contains twelve claim-interpretation cases grounded in short abstract excerpts from four published antibody-engineering papers. It prepares a small, inspectable test of source matching and semantic overreach for FrontierLab. No model has been run on these cases, and no scientific accuracy result is available.

## Sources and scope

| Source | DOI | Passage topic |
| --- | --- | --- |
| Zou and colleagues, online 2021 | 10.1007/s13205-021-03079-x | Number of pH-dependent antibodies isolated. |
| Sulea and colleagues, online 2019 / collection 2020 | 10.1080/19420862.2019.1682866 | Reported improvement in acidic-pH binding selectivity. |
| Traxlmayr and colleagues, 2014 | 10.1002/biot.201300483 | Histidine mutations absent from two of three Fcabs. |
| Schröter and colleagues, online 2014 / collection 2015 | 10.4161/19420862.2014.985993 | Screening conditions and exclusion of negative selection. |

Full bibliographic attribution, source and retrieval URLs, publication-year records and retrieval timestamps are preserved in [the dataset](../datasets/real_ph_excerpt_cases_v1.json). Article XML was retrieved from Europe PMC. Only one attributed abstract excerpt of at most 25 whitespace-delimited words per article is redistributed; full papers and full abstracts are not bundled. Recorded license links are included where present in the retrieved metadata; further reuse requires checking the original rights.

The twelve cases have four provisional supported, four contradicted and four insufficient-evidence labels, authored by AI during development. These labels and rationales are **unreviewed proposals**, not human gold data. Cases concern only the supplied excerpt. Insufficient means the excerpt cannot decide the claim, not that the entire paper disproves it.

These historical mutagenesis studies are background for evidence interpretation. They do not establish de novo eligibility for the current Anthropic × Adaptyv competition, prove any FrontierLab design works, or rank the applicant's submissions. No sequences, new designs or wet-lab instructions are generated.

## Review and model input

The reviewer packet and public case payload use an explicit whitelist: source records, case IDs, claims and scope. Provisional labels and draft rationales are excluded. A reviewer still needs to avoid looking at the separate draft references if a blind assessment is intended; the software cannot establish blinding or reviewer independence.

The packet starts with every case PENDING and annotation_origin=PENDING_RESEARCHER_ANNOTATION. After inspecting the original context, a researcher can enter SUPPORTED, CONTRADICTED or INSUFFICIENT plus a rationale of at least eight characters, and declare annotation_origin=RESEARCHER_SUPPLIED. The application records that declaration; it does not authenticate authorship or expert adjudication.

## Offline commands

Export a blank source-bound reviewer packet:

```bash
python -m scripts.real_literature_benchmark --kind review-packet > review.json
```

Export the prediction schema:

```bash
python -m scripts.real_literature_benchmark --kind predictions-template > predictions.json
```

After collecting actual model outputs in that schema:

```bash
python -m scripts.real_literature_benchmark --kind evaluate --predictions predictions.json
python -m scripts.real_literature_benchmark --kind evaluate --predictions predictions.json --review review.json
```

These commands make no model, publisher or NVIDIA request. PENDING predictions are rejected. Every packet must contain all dataset cases exactly once and match the current dataset snapshot.

The Streamlit expander also offers the blank reviewer packet. A new HF build is required to display it.

## What the comparison measures

- Raw predictions are preserved.
- The gate requires the case's own source ID and a 24–500-character quotation matching the supplied excerpt after whitespace/case normalization.
- Missing, misattributed or fabricated quotations produce INSUFFICIENT after the gate.
- Existing quotations do not establish semantic support: a confidently reversed interpretation can still pass the quotation gate.
- Label agreement and false-support counts are withheld until all references are reviewed and the researcher declaration is supplied.
- Reviewer corrections are counted as human intervention, not as fully autonomous model accuracy.

Imported outputs always retain IMPORTED_UNVERIFIED provenance. A model name or a self-reported execution flag in a JSON file cannot prove that a provider call happened. Source snapshots detect changed inputs, not scientific truth.

A proper model experiment still requires a genuine recorded inference run, matched settings and cases across conditions, independently assessed references and measured human effort. This small, selected pilot cannot establish biomedical generalization, clinical validity, paper-reproduction success or the effectiveness of a protein design.

## Software verification

The suite tests source hashes, packet completeness, hidden draft-label exclusion, pending-review behavior, source/quote mismatch, stale packets and the difference between quote validity and interpretation. Predictions and reviewer records in tests are explicitly artificial fixtures.

```bash
python -m pytest -q
```


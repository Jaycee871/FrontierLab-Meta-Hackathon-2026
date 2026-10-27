# Legacy Facebook Research MUSE · Multilingual Evidence Reference

**Status:** reference-only extension for FrontierLab  
**Upstream:** https://github.com/facebookresearch/MUSE  
**Upstream state:** archived  
**License:** CC BY-NC 4.0  
**Important:** this project is **not** Meta Muse Glimmer.

## Why this is here

FrontierLab currently uses **Meta Muse Glimmer 30B** as its Meta-model path for evidence extraction and research synthesis. Facebook Research also published an older project named **MUSE**, short for **Multilingual Unsupervised and Supervised Embeddings**. The names are similar, but the systems are unrelated.

The legacy MUSE project is preserved here only as a research reference for a possible future **multilingual evidence-discovery layer**. No upstream MUSE source code, checkpoints or dictionaries are bundled into FrontierLab, and FrontierLab does not claim to execute MUSE today.

## What the original MUSE project does

The archived Facebook Research repository provides methods and resources for aligning monolingual word embeddings into a shared multilingual vector space.

Its two principal alignment paths are:

1. **Supervised alignment** — uses a bilingual dictionary or identical strings as anchors and learns an iterative orthogonal Procrustes mapping.
2. **Unsupervised alignment** — learns an initial mapping without parallel data using adversarial training, then refines the mapping with iterative Procrustes alignment.

The upstream project also publishes aligned fastText embeddings and bilingual dictionaries for cross-lingual evaluation. Its README describes 30 languages aligned into a common space and 110 bilingual dictionaries.

## Possible FrontierLab role

A future multilingual extension could sit inside **Stage 2 · Evidence** before literature retrieval:

```text
Research question
      |
      v
Scientific term extraction
      |
      v
Cross-lingual term alignment / query expansion
      |
      +----> English literature query
      +----> Chinese literature query
      +----> Other supported-language query
      |
      v
Source-normalized retrieval
      |
      v
Existing FrontierLab evidence + human review gates
```

The useful idea is not to replace semantic retrieval with legacy word vectors. It is to use cross-lingual alignment as a **query-expansion or terminology-normalization aid**, then pass all retrieved records through FrontierLab's existing provenance, quotation and human-review checks.

## Why it is not a default dependency

The upstream repository is archived and reflects an older Python / PyTorch / fastText-era stack. Adding it directly to the hackathon runtime would create several avoidable problems:

- dependency and maintenance risk;
- a confusing naming collision with Meta Muse Glimmer;
- no demonstrated need for it in the current five-stage demo;
- extra licensing obligations if upstream code or data are redistributed;
- no evidence yet that legacy static word-embedding alignment improves FrontierLab's biomedical retrieval.

For the hackathon submission, the safer position is therefore:

> **MUSE is a future multilingual evidence-retrieval reference, not a current FrontierLab capability.**

## Evaluation plan if this extension is activated later

A real implementation should be tested against a fixed multilingual biomedical query set. At minimum, compare:

| Condition | Purpose |
| --- | --- |
| English-only retrieval | Baseline |
| Dictionary-based query expansion | Simple multilingual baseline |
| MUSE-style aligned-term expansion | Test whether aligned embeddings add useful terminology |
| Modern multilingual encoder retrieval | Stronger contemporary baseline |

Report retrieval recall / precision where labels exist, source-language coverage, duplicate rate, query drift, and the number of human corrections required. Any biomedical claim would still need the normal FrontierLab evidence and review gates.

## Licensing boundary

The upstream repository declares **Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**. FrontierLab therefore links to and documents the project rather than copying its source code or datasets into this repository.

Before redistributing upstream code, embeddings or dictionaries, review the upstream license and the licensing of any underlying datasets separately.

## Relationship to Meta Muse Glimmer

| Name | Project | Role in FrontierLab |
| --- | --- | --- |
| **MUSE** | Facebook Research multilingual word-embedding alignment | Optional legacy reference for future multilingual evidence discovery |
| **Muse Glimmer 30B** | Current Meta reasoning model used through the FrontierLab Meta-model path | Actual model integration used for recorded inference experiments |

Keeping this distinction explicit avoids overstating what the hackathon prototype currently runs.

## Upstream references

- Facebook Research MUSE: https://github.com/facebookresearch/MUSE
- MUSE README: https://github.com/facebookresearch/MUSE/blob/main/README.md
- MUSE license: https://github.com/facebookresearch/MUSE/blob/main/LICENSE

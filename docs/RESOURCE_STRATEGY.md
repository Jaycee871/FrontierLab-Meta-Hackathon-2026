# FrontierLab: connected research tooling & cost-safe implementation

Updated 2026-10-27. Research development notes; **not verified Hackathon submission**.

## Resource policy — no Meta billed API calls

The user has asked not to use Meta Model API because of payment-card risk. The Streamlit UI has **no active Meta API client and no API key field**. The repository's original Meta adapter exists for historical traceability, but is NOT called from the UI. We will not use paid Meta endpoints without new explicit permission.

GitHub Actions secrets for Hugging Face, Kaggle and NVIDIA belong to GitHub Actions and are not directly readable by ChatGPT's GitHub integration. They do not by themselves activate Kaggle GPU or provide deployment. Never print tokens in CI logs; never commit keys. This repository's tests workflow currently does not reference any secrets.

## Hackathon eligibility constraint

Organizer rules require **real, demonstrable use of a Meta model** (either an approved Meta Model API or an official Meta open-weight model). Other providers' proprietary models alone, Wolfram, literature search, and synthetic stubs do NOT satisfy this requirement. The viable non-Meta-billed route is **Muse Glimmer 30B** open weights, subject to live feasibility testing.

Meta official references:
- https://dev.meta.ai/models/muse-glimmer
- https://dev.meta.ai/docs/muse-glimmer/get-the-model
- https://dev.meta.ai/docs/muse-glimmer/quantization

The Meta-published 17GB GGUF checkpoint is about 16.8 GB on disk; recommended text + optional vision loading can need ~19 GiB VRAM. Kaggle T4x2 has two separate 16GB cards, NOT one unified 32GB GPU. Sharding, CPU offload, or another compatible provider is required and **not yet validated**. Do not spend Kaggle quota or download large checkpoints before a resource audit.

Kaggle's P100 has reportedly been retired (official notice September 15, 2026), so do not assume that option exists. Check which accelerator is actually available in the account.

## Wolfram — tested live in chat

Wolfram Language evaluator successfully computed fixed-effect inverse-variance meta-analysis on explicitly **FICTIONAL** effect sizes [0.4, -0.3] and SEs [0.15, 0.1]. Pooled estimate = -0.0846153846, Cochran Q = 15.0769230769, I² = 0.9336734694. No biological observation is claimed. A matching deterministic Python function and regression test reproduce this result without needing Wolfram access at app runtime.

## Undermind — tested live in chat

Created research workspace: https://app.undermind.ai/projects/362994e3-20f1-4bb8-9984-9a088a13c27f

Semantic literature search returned real pH-switchable protein binder studies. Four papers were saved to its /literature/ folder. These citations are metadata verified through Undermind, but **no full-text independent validation, evidence extraction, or conflict claim** has yet been made.

- Watanabe et al. (2009), *Optimizing pH Response of Affinity between Protein G and IgG Fc*, JBC, DOI: https://doi.org/10.1074/jbc.M809236200
- Watanabe et al. (2019), *Histidine-mediated intramolecular electrostatic repulsion for controlling pH-dependent protein-protein interaction*, ACS Chemical Biology, DOI: https://doi.org/10.1021/acschembio.9b00652
- Zou et al. (2021), *A stepwise mutagenesis approach using histidine and acidic amino acid to engineer highly pH-dependent protein switches*, 3 Biotech, DOI: https://doi.org/10.1007/s13205-021-03079-x
- Jensen (2008), *Calculating pH and salt dependence of protein-protein binding*, Current Pharmaceutical Biotechnology, DOI: https://doi.org/10.2174/138920108783955146

Undermind operates as a connected research service in chat; the standalone Streamlit prototype does NOT automatically have Undermind credentials.

## Next validation milestones

1. Kaggle notebook hardware report from scripts/kaggle_gpu_check.py (no GPU usage except inspection).
2. Muse Glimmer model/inference feasibility and license validation on available hardware or an approved no-Meta-billing inference provider. No API keys printed.
3. Implement an isolated open-weight inference adapter, ensure outputs are distinguished from deterministic gates.
4. Evaluate real source quotations and disagreements against full-text paper methods; never call a metadata-only validation 'scientifically verified'.
5. Obtain a working 3-minute demo with demonstrable **Meta open-weight model** inference, not just mocks.

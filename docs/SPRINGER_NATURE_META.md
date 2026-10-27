# Springer Nature Meta API v2 — FrontierLab

Created on 2026-10-27. Code and offline tests implemented. Live secret-backed test is NOT claimed complete until its manually triggered workflow succeeds.

Official: https://dev.springernature.com/docs/api-endpoints/meta-api/
Endpoint: https://api.springernature.com/meta/v2/json

The Springer Nature **Meta API** provides bibliographic metadata (not Meta Platforms' AI model inference). It is distinct from the Springer Nature Open Access API. Neither API automatically grants full text for paywalled papers.

You added GitHub repository secret Meta_API_Key. The workflow references secrets.META_API_KEY, as GitHub normalizes secret names case-insensitively. Please do not paste the secret in public code or an issue. It is not inherited by the Hugging Face Space.

## Operational tests

1. GitHub Actions → Springer Nature Meta API v2 Connection Check → Run workflow.
2. Confirm output status OK, count > 0, title/DOI and whether an abstract exists (not the key).
3. Optional full workflow: Actions → FrontierLab Three-Source Discovery Audit (manual) → Run workflow.
4. This second workflow calls Europe PMC, Springer Nature Meta and Open Access once each (two records/provider) and outputs DOI-merged metadata plus per-source status. A failed provider is reported FAILED, not silently treated as zero publications.

## Integrity

- The API returns records with DOIs, titles, authors, publication dates and abstracts when supplied; missing abstracts remain empty.
- The merger normalizes DOI capitalization/URL prefixes, deduplicates records and preserves the source list. It prefers the longer nonempty abstract but does not independently validate accuracy.
- Documents without abstracts cannot support evidence extraction by themselves.
- No external Meta Model API billing or automated paywalled full-text collection.
- The existing public Hugging Face CPU Space currently uses Europe PMC only; to enable publisher API calls there requires adding distinct Hugging Face Secrets and deploying a UI integration. GitHub secrets are not automatically copied.

Other sources:
https://dev.springernature.com/docs/advanced-querying/example-advanced-queries/

# Springer Nature Open Access API

Status 2026-10-27: offline client + mock tests prepared. Live secret-based check NOT YET RUN.

Official: https://dev.springernature.com/docs/api-endpoints/open-access/
Free plan: https://dev.springernature.com/subscription/

This API is provided by Springer Nature. It includes OA articles and chapters from several publishers and journals, not all Nature-branded articles. Metadata are available at /openaccess/json, with JATS XML full text for eligible publications at /openaccess/jats. A public API key is not a license to redistribute copyrighted full text or scrape subscription content.

The publicly advertised basic tier is 500 requests/day and 100/minute, subject to your specific account's actual plan. Client deliberately makes at most one request with up to 10 returned records.

The user added a GitHub Actions secret named Open_Access_API. GitHub Secrets are visible only to explicitly configured runner jobs; they do not automatically appear in the publicly hosted Hugging Face Space.

Manual verification:
1. Open GitHub repository, Actions, Springer Nature OA Connection Check.
2. Click Run workflow to make ONE small query using the secret.
3. The workflow prints only title, DOI and whether abstract is present. It never prints the key, full URL or response body.
4. Do not put credentials in source code or a public Streamlit text field.

Implementation: frontierlab/springer_oa.py returns Paper objects with stable DOI source IDs and explicit source provenance. papers lacking abstracts are retained as metadata, not used as inferred claims.

Current public HF Space continues to use Europe PMC only. Adding a separate HF Space Secret and enabling this connector in the UI would need deliberate action; no GitHub API key is automatically transferred. Do not bulk-download JATS full text before verifying Springer Nature license/TDM rights.

"""Read-only Springer Nature Meta API v2 bibliographic retrieval.

Distinct from Meta Platforms' paid model API. Secrets are never printed.
"""
from __future__ import annotations
import os
import requests
from .models import Paper
from .springer_oa import _parse

META_URL = "https://api.springernature.com/meta/v2/json"

def retrieve_metadata(query: str, *, page_size: int = 5, api_key=None, session=None) -> list[Paper]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Nonempty metadata query required")
    if not 1 <= page_size <= 10:
        raise ValueError("page_size must be 1..10")
    key = api_key or os.getenv("SPRINGER_NATURE_META_API_KEY") or os.getenv("META_API_KEY")
    if not key:
        raise ValueError("Springer Nature Meta credential not configured")
    s = session if session is not None else requests.Session()
    if hasattr(s, "trust_env"):
        s.trust_env = False
    try:
        response = s.get(META_URL, params={"q":query.strip(), "s":1, "p":page_size,
            "api_key":key}, timeout=20, allow_redirects=False,
            headers={"Accept":"application/json"})
    except requests.RequestException:
        raise RuntimeError("Springer Nature Meta connection error (request URL suppressed)") from None
    if response.status_code in (401, 403):
        raise RuntimeError("Springer Nature Meta authentication/authorization denied")
    if response.status_code == 429:
        raise RuntimeError("Springer Nature Meta API rate limit reached")
    if response.status_code != 200:
        raise RuntimeError("Springer Nature Meta returned HTTP " + str(response.status_code))
    try:
        payload = response.json()
    except (TypeError, ValueError):
        raise RuntimeError("Springer Nature Meta returned invalid JSON") from None
    records = payload.get("records", []) if isinstance(payload, dict) else []
    if not isinstance(records, list):
        raise RuntimeError("Unexpected Springer Nature Meta record format")
    out, ids = [], set()
    for item in records:
        if not isinstance(item, dict):
            continue
        if not item.get("doi"):
            ident = str(item.get("identifier") or "")
            if ident.lower().startswith("doi:"):
                item = {**item, "doi": ident[4:]}
        paper = _parse(item)
        if paper and paper.paper_id not in ids:
            ids.add(paper.paper_id)
            out.append(Paper(
                paper_id=paper.paper_id, title=paper.title, year=paper.year,
                authors=paper.authors, abstract=paper.abstract,
                url=paper.url, doi=paper.doi, source="Springer Nature Meta API v2"
            ))
    return out

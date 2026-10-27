"""Springer Nature Open Access API. No secrets in logs or public Space."""
import os
import requests
from .evidence import clean_html
from .models import Paper

OA_URL = "https://api.springernature.com/openaccess/json"

def _parse(record):
    if not isinstance(record, dict):
        return None
    doi = str(record.get("doi") or "").strip()
    title = clean_html(str(record.get("title") or ""))
    if not doi or not title:
        return None
    raw_abstract = record.get("abstract") or ""
    abstract = clean_html(raw_abstract)[:6000] if isinstance(raw_abstract, str) else ""
    creators = record.get("creators") or []
    names = []
    if isinstance(creators, list):
        for c in creators:
            value = c.get("creator") or c.get("name") or "" if isinstance(c, dict) else c
            if isinstance(value, str) and value.strip():
                names.append(clean_html(value))
    date = str(record.get("publicationDate") or "")
    return Paper(paper_id="DOI:" + doi.lower(), title=title,
        year=date[:4] if date[:4].isdigit() else "",
        authors=", ".join(names), abstract=abstract,
        doi=doi, url="https://doi.org/" + doi,
        source="Springer Nature Open Access API")

def retrieve_open_access(query, *, page_size=5, api_key=None, session=None):
    """Single OA metadata request, capped at 10 records; never expose key in errors."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Nonempty OA query required")
    if not 1 <= page_size <= 10:
        raise ValueError("page_size must be 1..10")
    key = api_key or os.environ.get("SPRINGER_NATURE_OA_API_KEY") or os.environ.get("Open_Access_API")
    if not key:
        raise ValueError("Springer Nature Open Access credential not configured")
    s = session if session is not None else requests.Session()
    if hasattr(s, "trust_env"):
        s.trust_env = False
    try:
        response = s.get(OA_URL, params={"q": query.strip(), "p": page_size,
            "s": 1, "api_key": key}, timeout=20, allow_redirects=False,
            headers={"Accept":"application/json"})
    except requests.RequestException:
        raise RuntimeError("Springer Nature OA transport failed; request URL suppressed") from None
    if response.status_code in (401, 403):
        raise RuntimeError("Springer Nature OA authentication/authorization rejected")
    if response.status_code == 429:
        raise RuntimeError("Springer Nature OA rate limit reached")
    if response.status_code != 200:
        raise RuntimeError("Springer Nature OA returned HTTP " + str(response.status_code))
    try:
        obj = response.json()
    except (ValueError, TypeError):
        raise RuntimeError("Springer Nature OA invalid JSON") from None
    rows = obj.get("records", []) if isinstance(obj, dict) else []
    if not isinstance(rows, list):
        raise RuntimeError("Unexpected Springer Nature OA schema")
    out, seen = [], set()
    for row in rows:
        paper = _parse(row)
        if paper and paper.paper_id not in seen:
            seen.add(paper.paper_id)
            out.append(paper)
    return out

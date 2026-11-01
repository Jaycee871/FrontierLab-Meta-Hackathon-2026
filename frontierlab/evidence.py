"""Evidence retrieval uses primary metadata; references are never model-generated."""
from __future__ import annotations
import html
import re
import requests
from .models import Paper

EPMC_ENDPOINT = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def clean_html(value: str) -> str:
    value = re.sub(r"<[^>]*>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def europepmc_error_message(exc: BaseException) -> str | None:
    """Return a friendly message when *exc* came from the Europe PMC request.

    Returns None for any other exception so callers keep their normal handling.
    """
    if not isinstance(exc, requests.RequestException):
        return None
    response = getattr(exc, "response", None)
    request = getattr(exc, "request", None)
    url = (getattr(response, "url", None) or getattr(request, "url", None) or "")
    if not str(url).startswith(EPMC_ENDPOINT):
        return None
    status = getattr(response, "status_code", None)
    if status == 429:
        detail = "Europe PMC is rate-limiting requests right now (HTTP 429)."
    elif status is not None and status >= 500:
        detail = f"Europe PMC is temporarily unavailable (HTTP {status})."
    elif status is not None:
        detail = f"Europe PMC rejected the search request (HTTP {status}). Try simplifying the query."
    elif isinstance(exc, requests.Timeout):
        detail = "Europe PMC did not respond in time."
    else:
        detail = "Europe PMC could not be reached from this server."
    return (detail + " No evidence was retrieved and no model was called. "
            "Please try again in a minute, or use the synthetic audit or the recorded replay meanwhile.")


def retrieve_papers(query: str, page_size: int = 6, session=None) -> list[Paper]:
    if not query.strip():
        raise ValueError("Research query must not be empty")
    if not 1 <= page_size <= 15:
        raise ValueError("page_size must be between 1 and 15")
    session = session or requests
    response = session.get(EPMC_ENDPOINT, params={
        "query": query,
        "format": "json",
        "pageSize": page_size,
        "resultType": "core",
    }, timeout=20, headers={"User-Agent": "FrontierLabHackathon/0.1 (research demo)"})
    response.raise_for_status()
    raw = response.json().get("resultList", {}).get("result", [])
    papers = []
    for item in raw:
        abstract = clean_html(item.get("abstractText", ""))
        if not abstract:
            continue
        source = item.get("source", "")
        identifier = item.get("id", "")
        if not identifier:
            continue
        paper_id = f"{source}:{identifier}"
        doi = item.get("doi", "") or ""
        url = f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/{source}/{identifier}"
        papers.append(Paper(
            paper_id=paper_id,
            title=clean_html(item.get("title", "Untitled")),
            year=str(item.get("pubYear", "")),
            authors=clean_html(item.get("authorString", "")),
            abstract=abstract[:6000],
            doi=doi,
            url=url,
        ))
    return papers

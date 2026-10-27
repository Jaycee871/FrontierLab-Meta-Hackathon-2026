"""Three-source bibliographic discovery with DOI normalization.

Publisher metadata is not verified scientific evidence. No paid Meta model API.
"""
from __future__ import annotations
from .evidence import retrieve_papers
from .springer_meta import retrieve_metadata
from .springer_oa import retrieve_open_access
from .multisource import merge_papers, source_summary

def discover(epmc_query: str, springer_query: str, *,
             per_source: int = 3, epmc=None, meta=None, oa=None) -> dict:
    if not 1 <= per_source <= 10:
        raise ValueError("per_source must be between 1 and 10")
    # Wrap providers with keyword-only page_size to keep a uniform interface.
    calls = [
        ("Europe PMC", epmc or (lambda q,n: retrieve_papers(q, page_size=n)), epmc_query),
        ("Springer Nature Meta API v2", meta or (lambda q,n: retrieve_metadata(q, page_size=n)), springer_query),
        ("Springer Nature Open Access API", oa or (lambda q,n: retrieve_open_access(q, page_size=n)), springer_query),
    ]
    groups, statuses = [], {}
    for name, fetch, query in calls:
        try:
            results = fetch(query, per_source)
        except Exception as exc:
            # Never put credential-bearing exception messages into public logs.
            statuses[name] = {"status":"FAILED", "error_type":type(exc).__name__}
        else:
            groups.append(results)
            statuses[name] = {"status":"OK", "records":len(results)}
    papers = merge_papers(groups)
    return {"papers":papers, "source_status":statuses, "summary":source_summary(papers)}

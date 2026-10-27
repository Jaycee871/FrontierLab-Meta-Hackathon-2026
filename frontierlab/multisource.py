"""Cross-source DOI-based deduplication: metadata is not verified science."""
from dataclasses import replace
from .models import Paper

def normalize_doi(raw: str) -> str:
    value = (raw or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value.strip()

def merge_papers(groups: list[list[Paper]]) -> list[Paper]:
    result, order = {}, []
    for items in groups:
        for item in items:
            doi = normalize_doi(item.doi)
            key = "DOI:" + doi if doi else item.paper_id
            if not key:
                continue
            if key not in result:
                result[key] = replace(item, paper_id=key, doi=doi)
                order.append(key)
                continue
            old = result[key]
            preferred = item if len(item.abstract.strip()) > len(old.abstract.strip()) else old
            sources = []
            for name in (old.source + " ; " + item.source).split(" ; "):
                name = name.strip()
                if name and name not in sources:
                    sources.append(name)
            result[key] = replace(preferred, paper_id=key, doi=doi,
                                  source=" ; ".join(sources))
    return [result[key] for key in order]

def source_summary(papers: list[Paper]) -> dict:
    return {
        "deduplicated": len(papers),
        "with_abstract": sum(bool(p.abstract.strip()) for p in papers),
        "metadata_only": sum(not p.abstract.strip() for p in papers),
        "sources": sorted({name.strip() for p in papers
                           for name in p.source.split(" ; ") if name.strip()}),
    }

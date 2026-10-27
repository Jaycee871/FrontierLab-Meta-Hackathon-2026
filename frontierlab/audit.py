"""Deterministic evidence gates; model responses are treated as untrusted inputs."""
from __future__ import annotations
from collections import defaultdict
from .claim_verification import normalize_excerpt
from .models import Audit, Claim, Paper

VALID_STANCES = {"supports", "contradicts", "mixed", "inconclusive"}


def validate_claims(papers: list[Paper], candidate_claims: list[dict], *, require_quote: bool = False) -> Audit:
    known = {p.paper_id: p for p in papers}
    audit = Audit()
    for item in candidate_claims:
        pid = str(item.get("paper_id", ""))
        stance = str(item.get("stance", "")).lower()
        key = str(item.get("claim_key", "")).strip().lower()
        statement = str(item.get("statement", "")).strip()
        reason = str(item.get("limitation", "")).strip()
        if pid not in known or stance not in VALID_STANCES or not key or not statement:
            audit.rejected_claims.append({"claim": item, "reason": "invalid / unknown citation or claim format"})
            continue
        raw_quote = item.get("evidence_quote", item.get("quote", ""))
        quote = raw_quote.strip() if isinstance(raw_quote, str) else ""
        # This only proves the quote exists in THIS SOURCE'S abstract.
        # Never treat matching text as scientific support or independent entailment.
        matches = bool(
            quote and 24 <= len(quote) <= 500 and
            normalize_excerpt(quote) in normalize_excerpt(known[pid].abstract)
        )
        if require_quote and not matches:
            audit.rejected_claims.append({
                "claim": item,
                "reason": "missing / short / unmatched verbatim quote in cited source abstract"
            })
            continue
        audit.verified_claims.append(Claim(
            paper_id=pid, stance=stance, claim_key=key,
            statement=statement, limitation=reason or "Not specified; manual review required",
            evidence_quote=quote if matches else "",
            passage_matched=matches
        ))

    grouped = defaultdict(list)
    for claim in audit.verified_claims:
        grouped[claim.claim_key].append(claim)
    for key, group in grouped.items():
        supports = sorted({c.paper_id for c in group if c.stance == "supports"})
        contradicts = sorted({c.paper_id for c in group if c.stance == "contradicts"})
        if supports and contradicts:
            audit.conflicts.append({"claim_key": key, "supports": supports, "contradicts": contradicts})

    if any(p.synthetic for p in papers):
        audit.warnings.append("SYNTHETIC FIXTURE: All example sources are invented for testing and are NOT literature citations.")
    if require_quote:
        audit.warnings.append(
            "Passage grounding checked against cited abstracts; semantic entailment is NOT "
            "verified. Researcher review of methods and full text is required."
        )
    if not audit.verified_claims:
        audit.warnings.append("No verified, machine-readable evidence claims available. Do not infer a conclusion.")
    if audit.rejected_claims:
        audit.warnings.append(f"Rejected {len(audit.rejected_claims)} claims with invalid IDs, formats or missing/unaligned source passages.")
    return audit


def enforce_citations(items: list[dict], papers: list[Paper], key: str = "evidence_ids") -> tuple[list[dict], list[dict]]:
    known = {p.paper_id for p in papers}
    accepted, rejected = [], []
    for item in items:
        ids = item.get(key, [])
        if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or x not in known for x in ids):
            rejected.append({"item": item, "reason": "missing or unrecognized evidence IDs"})
        else:
            accepted.append(item)
    return accepted, rejected


def risk_decision(audit: Audit, claims_needed: int = 2) -> str:
    distinct_sources = {c.paper_id for c in audit.verified_claims}
    if audit.conflicts:
        return "REVIEW_CONFLICT"
    if len(distinct_sources) < claims_needed:
        return "INSUFFICIENT_EVIDENCE"
    return "HUMAN_REVIEW_REQUIRED"

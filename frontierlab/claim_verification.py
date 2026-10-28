"""Auditable claim-to-passage checks; no unsupported 'AI verified the science' claims.

Valid DOI/source ID != anchored evidence passage != semantic entailment.
This module checks IDs and exact passage quotes, and scores model labels only
against independently supplied annotations. It cannot decide scientific truth.
"""
from __future__ import annotations
import re
from collections import defaultdict
from .models import Paper

LABELS = {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT"}

def normalize_excerpt(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip()).casefold()

def quote_anchored(abstract: str, quote: str) -> bool:
    """The anchor check: a nonempty quote occurs in the abstract (whitespace/case-insensitive).

    Shared by audit_predictions and the evidence graph so both apply one rule.
    """
    q = normalize_excerpt(quote)
    return bool(q and q in normalize_excerpt(abstract))

def locate_quote(abstract: str, quote: str) -> tuple[int, int] | None:
    """Character span [start, end) of an anchored quote within the ORIGINAL abstract.

    Returns None unless quote_anchored() passes and the normalized match can be mapped
    back onto the original text exactly (fail closed on any mapping doubt).
    """
    if not isinstance(abstract, str) or not isinstance(quote, str):
        return None
    if not quote_anchored(abstract, quote):
        return None
    lead = len(abstract) - len(abstract.lstrip())
    body = abstract.strip()
    chars: list[str] = []
    origin: list[int] = []
    i = 0
    while i < len(body):
        if re.match(r"\s", body[i]):
            j = i
            while j < len(body) and re.match(r"\s", body[j]):
                j += 1
            chars.append(" ")
            origin.append(lead + i)
            i = j
            continue
        for folded in body[i].casefold():
            chars.append(folded)
            origin.append(lead + i)
        i += 1
    normalized = "".join(chars)
    if normalized != normalize_excerpt(abstract):
        return None
    q = normalize_excerpt(quote)
    at = normalized.find(q)
    if at < 0:
        return None
    start, end = origin[at], origin[at + len(q) - 1] + 1
    if normalize_excerpt(abstract[start:end]) != q:
        return None
    return start, end

def audit_predictions(papers: list[Paper], rows: list[dict]) -> dict:
    """Test predictions against externally authored ground-truth labels.

    Each row: id, paper_id, claim_key, claim, quote, predicted, gold.
    quote must be an exact contiguous span of the abstract (whitespace-insensitive).
    Ground-truth labels MUST come from independent annotators for a real study.
    """
    catalog = {p.paper_id: p for p in papers}
    details, ids = [], set()
    for row in rows:
        case_id = str(row.get("id", ""))
        if not case_id or case_id in ids:
            raise ValueError("Every case needs a distinct nonempty id")
        ids.add(case_id)
        gold = str(row.get("gold", "")).upper()
        if gold not in LABELS:
            raise ValueError("Missing or unrecognized independent gold label")
        predicted = str(row.get("predicted", "")).upper()
        if predicted not in LABELS:
            raise ValueError("Missing or unrecognized model label")
        paper_id = str(row.get("paper_id", ""))
        paper = catalog.get(paper_id)
        anchor = bool(paper and quote_anchored(paper.abstract, row.get("quote", "")))
        # Fail closed: without a quote from the named source, no affirmative
        # 'supports' or 'contradicts' model label is permitted past the gate.
        published = predicted if anchor else "INSUFFICIENT"
        details.append({
            "id":case_id, "paper_id":paper_id, "claim_key":str(row.get("claim_key","")),
            "gold":gold, "model_predicted":predicted,
            "gate_output":published, "id_known":paper is not None,
            "quote_in_abstract":anchor, "gold_agrees_with_gate":published == gold,
            "scientific_entailment_verified":False,
            "reason": ("QUOTE_ANCHORED_LABEL_UNVERIFIED" if anchor else
                       ("UNKNOWN_SOURCE_ID" if paper is None else "NO_MATCHING_SOURCE_PASSAGE"))
        })
    n = len(details)
    def rate(num, den):
        return round(num/den,4) if den else None
    labels = defaultdict(lambda: {"tp":0, "fp":0, "fn":0})
    for row in details:
        for label in LABELS:
            if row["gate_output"] == label and row["gold"] == label:
                labels[label]["tp"] += 1
            elif row["gate_output"] == label and row["gold"] != label:
                labels[label]["fp"] += 1
            elif row["gate_output"] != label and row["gold"] == label:
                labels[label]["fn"] += 1
    by_label = {}
    for label in sorted(LABELS):
        c = labels[label]
        by_label[label] = {
            "precision":rate(c["tp"], c["tp"]+c["fp"]),
            "recall":rate(c["tp"], c["tp"]+c["fn"]),
            **dict(c),
        }
    return {
        "mode":"ANNOTATED_BENCHMARK_ONLY",
        "total":n,
        "source_id_coverage":rate(sum(r["id_known"] for r in details),n),
        "verbatim_passage_coverage":rate(sum(r["quote_in_abstract"] for r in details),n),
        "label_accuracy_vs_independent_gold":rate(
            sum(r["gold_agrees_with_gate"] for r in details),n),
        "by_label":by_label,
        "semantic_entailment_automatically_verified":False,
        "note":"Exact excerpt matching proves a passage occurs, not that the claim follows. "
               "Gold labels are independently authored; synthetic-case scores must not "
               "be reported as real-literature model accuracy.",
        "cases":details,
    }

def conflict_transparency(reported_pairs: list[tuple[str,str]],
                          gold_pairs: list[tuple[str,str]]) -> dict:
    """Pair-level contradiction recall vs independent annotations.

    Empty ground truth => undefined, NEVER 100% by default.
    """
    canon = lambda p: tuple(sorted(map(str,p)))
    gold = {canon(p) for p in gold_pairs}
    detected = {canon(p) for p in reported_pairs}
    tp = len(gold & detected)
    return {"reported":len(detected), "gold":len(gold),
            "true_detected":tp,
            "recall":round(tp/len(gold),4) if gold else None,
            "false_alarm_pairs":len(detected-gold)}

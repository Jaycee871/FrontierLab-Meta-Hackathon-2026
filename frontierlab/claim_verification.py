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
        quote = normalize_excerpt(row.get("quote", ""))
        anchor = bool(paper and quote and quote in normalize_excerpt(paper.abstract))
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

"""Manual scientific evidence review and portable annotation packets.

These are reviewer-supplied labels, NOT objectively validated scientific truth.
Only an exact-ID matched / quote-anchored set of claims is eligible for review.
No API calls or secret access occur in this module.
"""
from __future__ import annotations

import hashlib
import json
from .models import Run

VERDICTS = ("PENDING", "SUPPORTED", "CONTRADICTED", "INSUFFICIENT")
SCHEMA = "frontierlab.human-review.v1"

def review_packet(run: Run) -> dict:
    if run.mode != "live":
        raise ValueError("Researcher review packets require a live evidence run")
    papers = {p.paper_id:p for p in run.papers}
    cases = []
    for i, claim in enumerate(run.audit.verified_claims, 1):
        paper = papers.get(claim.paper_id)
        if paper is None or not claim.passage_matched or not claim.evidence_quote:
            raise ValueError("Review packet requires exact, source-matched abstract quotation")
        body = json.dumps([claim.paper_id, claim.claim_key, claim.statement,
                           claim.evidence_quote], ensure_ascii=False, separators=(",",":"))
        case_id = f"C{i:03d}-" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
        cases.append({
            "case_id":case_id, "paper_id":claim.paper_id, "paper_title":paper.title,
            "source":paper.source, "url":paper.url, "doi":paper.doi,
            "claim_key":claim.claim_key, "claim":claim.statement,
            "model_proposed_stance":claim.stance, "evidence_quote":claim.evidence_quote,
            "abstract_available":bool(paper.abstract.strip()),
            "verbatim_quote_matched":True,
            "review_label":"PENDING", "review_note":"",
        })
    dataset_id = hashlib.sha256(json.dumps(
        [(c["case_id"],c["paper_id"]) for c in cases],
        separators=(",",":")).encode("utf-8")).hexdigest()[:20]
    return {
        "schema":SCHEMA, "dataset_id":dataset_id,
        "research_question":run.question, "model_claims_from":run.model,
        "label_definitions":{
            "SUPPORTED":"The cited excerpt supports this specific claim within its stated scope.",
            "CONTRADICTED":"The cited excerpt directly contradicts the specific claim.",
            "INSUFFICIENT":"The cited excerpt does not decide this claim.",
            "PENDING":"Not yet independently reviewed.",
        },
        "note":"Quoted text existing in an abstract does not establish semantic validity. "
               "Reviewer judgments need transparent rationale; not an independently adjudicated gold dataset.",
        "cases":cases,
    }

def save_review(run: Run, decisions: list[dict]) -> dict:
    packet = review_packet(run)
    known = {c["case_id"]:c for c in packet["cases"]}
    if not isinstance(decisions,list):
        raise ValueError("Review decisions must be a list")
    seen=set()
    for raw in decisions:
        if not isinstance(raw,dict):
            raise ValueError("Invalid decision record")
        cid=raw.get("case_id")
        if not isinstance(cid,str) or cid not in known or cid in seen:
            raise ValueError("Duplicate or unrecognized claim identifier")
        seen.add(cid)
        label=raw.get("review_label")
        note=raw.get("review_note","")
        if label not in VERDICTS or not isinstance(note,str) or len(note)>1500:
            raise ValueError("Unrecognized review label or invalid note")
        if label in ("CONTRADICTED","INSUFFICIENT") and len(note.strip())<8:
            raise ValueError("Rejected or insufficient claims require reviewer rationale (8+ characters)")
        known[cid]["review_label"]=label
        known[cid]["review_note"]=note.strip()
    labels=[c["review_label"] for c in packet["cases"]]
    supported=[c for c in packet["cases"] if c["review_label"]=="SUPPORTED"]
    n=len(labels)
    packet["review_stats"]={
        "total":n, "reviewed":sum(x!="PENDING" for x in labels),
        "pending":labels.count("PENDING"),
        "supported":labels.count("SUPPORTED"),
        "contradicted":labels.count("CONTRADICTED"),
        "insufficient":labels.count("INSUFFICIENT"),
        "supported_distinct_sources":len({c["paper_id"] for c in supported}),
        "human_label_coverage":round(sum(x!="PENDING" for x in labels)/n,4) if n else None,
    }
    packet["status"]="READY_FOR_HUMAN_GATED_SYNTHESIS" if (
        n>0 and packet["review_stats"]["pending"]==0 and
        packet["review_stats"]["supported_distinct_sources"]>=2
    ) else "REVIEW_INCOMPLETE_OR_INSUFFICIENT"
    packet["independent_expert_adjudication_verified"]=False
    run.review=packet
    return packet

def approved_claims(run: Run) -> list:
    packet=run.review
    if not isinstance(packet,dict) or packet.get("schema")!=SCHEMA or (
        packet.get("dataset_id")!=review_packet(run)["dataset_id"]
    ):
        return []
    accepted={c["case_id"] for c in packet["cases"] if c["review_label"]=="SUPPORTED"}
    index={c["case_id"]:i for i,c in enumerate(review_packet(run)["cases"])}
    return [run.audit.verified_claims[index[k]] for k in index if k in accepted]

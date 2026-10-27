"""Published-excerpt pilot; no model calls and no self-certified gold labels."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

from .claim_verification import normalize_excerpt

LABELS = {"SUPPORTED", "CONTRADICTED", "INSUFFICIENT"}
DATA_PATH = Path(__file__).resolve().parents[1] / "datasets" / "real_ph_excerpt_cases_v1.json"


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def load_dataset(path=DATA_PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema") != "frontierlab.real-excerpt-cases.v1":
        raise ValueError("Unexpected literature dataset schema")
    sources = data.get("sources")
    cases = data.get("cases")
    if not isinstance(sources, list) or not isinstance(cases, list) or not sources or not cases:
        raise ValueError("Nonempty source and case lists required")
    by_source = {}
    for source in sources:
        sid = source.get("source_id")
        text = source.get("source_text")
        if not isinstance(sid, str) or not sid or sid in by_source:
            raise ValueError("Unique source IDs required")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Nonempty source text required")
        if hashlib.sha256(text.encode()).hexdigest() != source.get("excerpt_sha256"):
            raise ValueError("Source excerpt hash mismatch")
        by_source[sid] = source
    seen = set()
    for case in cases:
        cid = case.get("case_id")
        if not isinstance(cid, str) or not cid or cid in seen:
            raise ValueError("Unique case IDs required")
        if case.get("source_id") not in by_source or not isinstance(case.get("claim"), str) or not case["claim"].strip():
            raise ValueError("Case requires a known source and claim")
        seen.add(cid)
    return data


def public_cases(data):
    """Explicit whitelist prevents provisional reference labels reaching a model/reviewer."""
    return {
        "sources": deepcopy(data["sources"]),
        "cases": [{key: c[key] for key in ("case_id", "source_id", "claim")}
                  for c in data["cases"]],
        "scope": "Judge only the supplied short excerpt, not the whole paper or clinical truth.",
    }


def dataset_id(data):
    return _hash(public_cases(data))


def reviewer_packet(data):
    packet = public_cases(data)
    packet.update(schema="frontierlab.real-excerpt-review.v1", dataset_id=dataset_id(data),
                  annotation_origin="PENDING_RESEARCHER_ANNOTATION",
                  independence_verified=False)
    for case in packet["cases"]:
        case.update(label="PENDING", rationale="")
    return packet


def predictions_template(data):
    return {
        "schema": "frontierlab.real-excerpt-predictions.v1",
        "dataset_id": dataset_id(data), "model_id": None,
        "execution_origin": "IMPORTED_UNVERIFIED",
        "cases": [{"case_id": c["case_id"], "source_id": c["source_id"],
                   "label": "PENDING", "evidence_quote": ""}
                  for c in data["cases"]],
    }


def _rows(packet, schema, data):
    if not isinstance(packet, dict) or packet.get("schema") != schema or packet.get("dataset_id") != dataset_id(data):
        raise ValueError("Packet schema or source snapshot does not match")
    rows = packet.get("cases")
    expected = {c["case_id"] for c in data["cases"]}
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        raise ValueError("Case records required")
    ids = [r.get("case_id") for r in rows]
    if any(not isinstance(cid, str) for cid in ids) or len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError("Packet must contain each dataset case exactly once")
    return {r["case_id"]: r for r in rows}


def evaluate_imported(data, predictions, review=None):
    predicted = _rows(predictions, "frontierlab.real-excerpt-predictions.v1", data)
    references = {}
    if review is not None:
        references = _rows(review, "frontierlab.real-excerpt-review.v1", data)
        for row in references.values():
            if row.get("label") not in LABELS | {"PENDING"}:
                raise ValueError("Invalid reviewer label")
            if row["label"] != "PENDING" and (
                not isinstance(row.get("rationale"), str) or len(row["rationale"].strip()) < 8
            ):
                raise ValueError("Reviewed cases require a rationale of at least eight characters")
    source_map = {s["source_id"]: s for s in data["sources"]}
    cases = []
    for case in data["cases"]:
        row = predicted[case["case_id"]]
        label = row.get("label")
        if label not in LABELS:
            raise ValueError("Complete model predictions before evaluating")
        quote = row.get("evidence_quote")
        sid = row.get("source_id")
        same_source = sid == case["source_id"]
        anchored = bool(
            same_source and isinstance(quote, str) and 24 <= len(quote) <= 500 and
            normalize_excerpt(quote) in normalize_excerpt(source_map[case["source_id"]]["source_text"])
        )
        cases.append({
            "case_id": case["case_id"], "source_id": sid,
            "raw_label": label, "source_matches_case": same_source,
            "excerpt_matched": anchored,
            "gate_label": label if anchored else "INSUFFICIENT",
            "reference_label": references.get(case["case_id"], {}).get("label", "PENDING"),
            "semantic_support_automatically_verified": False,
        })
    reviewed = sum(c["reference_label"] in LABELS for c in cases)
    ready = (reviewed == len(cases) and review is not None and
             review.get("annotation_origin") == "RESEARCHER_SUPPLIED")
    metrics = None
    if ready:
        n = len(cases)
        metrics = {
            "raw_label_agreement_with_supplied_review": sum(c["raw_label"] == c["reference_label"] for c in cases) / n,
            "gate_label_agreement_with_supplied_review": sum(c["gate_label"] == c["reference_label"] for c in cases) / n,
            "raw_false_supports": sum(c["raw_label"] == "SUPPORTED" and c["reference_label"] != "SUPPORTED" for c in cases),
            "gate_false_supports": sum(c["gate_label"] == "SUPPORTED" and c["reference_label"] != "SUPPORTED" for c in cases),
            "reviewer_corrections_to_gate": sum(c["gate_label"] != c["reference_label"] for c in cases),
        }
    return {
        "schema": "frontierlab.real-excerpt-report.v1", "dataset_id": dataset_id(data),
        "status": "SCORED_AGAINST_SUPPLIED_REVIEW" if ready else "AWAITING_RESEARCHER_ANNOTATION",
        "prediction_origin": "IMPORTED_UNVERIFIED",
        "reported_model_id": predictions.get("model_id"),
        "real_model_execution_verified": False,
        "independent_reference_labels_verified": False,
        "total": len(cases), "reviewed": reviewed,
        "quote_anchor_count": sum(c["excerpt_matched"] for c in cases),
        "gate_abstentions": sum(c["gate_label"] == "INSUFFICIENT" for c in cases),
        "metrics": metrics, "cases": cases,
        "note": "The gate checks source/excerpt integrity, not meaning. Supplied reviewer labels "
                "are not authenticated independent gold. Human corrections are intervention, "
                "not autonomous model accuracy. Draft AI reference labels are never used for scoring.",
    }


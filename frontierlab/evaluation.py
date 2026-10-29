"""Source-bound method comparison; researcher assertions are not execution evidence."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json

from .models import Run
from .interventions import record_human_event
from .review import approved_claims, review_packet, source_fingerprint

CHECKS = ("data", "code", "environment", "parameters", "protocol", "metrics")
CHECK_STATES = ("unknown", "documented", "missing", "not_applicable")
CRITERIA = ("expected_value", "resources", "validation", "limitations", "novelty")
SCHEMA = "frontierlab.method-evaluation.v1"


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def allowed_sources(run: Run) -> list[str]:
    if not run.hypotheses:
        raise ValueError("Generate hypotheses before evaluating methods")
    if run.mode == "demo":
        return sorted(p.paper_id for p in run.papers if p.synthetic)
    if run.mode != "live":
        raise ValueError("Unsupported research mode")
    if not run.review or run.review.get("dataset_id") != review_packet(run)["dataset_id"]:
        raise PermissionError("Current source-bound human review required")
    ids = sorted({c.paper_id for c in approved_claims(run)})
    if run.review.get("status") != "READY_FOR_HUMAN_GATED_SYNTHESIS" or len(ids) < 2:
        raise PermissionError("Two human-supported sources and complete review required")
    if any(p.synthetic for p in run.papers):
        raise PermissionError("Synthetic publications cannot enter a live method evaluation")
    return ids


def context_id(run: Run) -> str:
    allowed_sources(run)
    return _digest({
        "question": run.question, "mode": run.mode, "model": run.model, "backend": run.backend,
        "sources": [source_fingerprint(p) for p in run.papers],
        "claims": [c.__dict__ for c in run.audit.verified_claims],
        "conflicts": run.audit.conflicts, "hypotheses": run.hypotheses,
        "human_review": run.review,
    })


def _text(value, label, minimum=1):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= 3000:
        raise ValueError(f"{label} requires {minimum}..3000 characters")
    return value.strip()


def blank_candidate(candidate_id: str, name: str = "") -> dict:
    return {
        "candidate_id": candidate_id, "name": name, "evidence_ids": [],
        "scope": "",
        "checks": {key: {"status": "unknown", "detail": "", "reference": ""}
                   for key in CHECKS},
        "comparison": {key: "" for key in CRITERIA},
    }


def _candidate(raw, known):
    if not isinstance(raw, dict):
        raise ValueError("Candidate must be an object")
    cid = _text(raw.get("candidate_id"), "Candidate ID")
    name = _text(raw.get("name"), "Method name")
    ids = raw.get("evidence_ids")
    if (not isinstance(ids, list) or not ids or
            any(not isinstance(x, str) or x not in known for x in ids)):
        raise ValueError("Method references must use reviewed source IDs")
    scope = _text(raw.get("scope"), "Applicability and scope")
    checks, gaps = {}, []
    supplied = raw.get("checks", {})
    if not isinstance(supplied, dict):
        raise ValueError("Reproducibility checks must be an object")
    for key in CHECKS:
        item = supplied.get(key, {})
        if not isinstance(item, dict) or item.get("status", "unknown") not in CHECK_STATES:
            raise ValueError("Invalid reproducibility check status")
        status = item.get("status", "unknown")
        detail = item.get("detail", "")
        reference = item.get("reference", "")
        if not isinstance(detail, str) or not isinstance(reference, str):
            raise ValueError("Check details and references must be text")
        if status != "unknown":
            detail = _text(detail, key + " explanation")
        if status == "documented":
            reference = _text(reference, key + " location/reference")
        checks[key] = {"status": status, "detail": detail.strip(), "reference": reference.strip()}
        if status in ("unknown", "missing"):
            gaps.append({"item": key, "status": status,
                         "reason": detail.strip() or "Not assessed; inspect original methods."})
    comparison = raw.get("comparison", {})
    if not isinstance(comparison, dict):
        raise ValueError("Comparison criteria must be an object")
    comparison = {key: _text(comparison.get(key), key) for key in CRITERIA}
    return {
        "candidate_id": cid, "name": name, "evidence_ids": sorted(set(ids)),
        "scope": scope, "checks": checks, "comparison": comparison,
        "reproducibility_status": "INCOMPLETE_DOCUMENTATION" if gaps else "DOCUMENTED_NOT_EXECUTED",
        "open_checks": gaps,
    }


def build_evaluation(run: Run, candidates: list[dict], *, selected_id: str | None,
                     rationale: str) -> dict:
    known = allowed_sources(run)
    if not isinstance(candidates, list) or not 0 <= len(candidates) <= 4:
        raise ValueError("Provide zero to four candidate methods")
    normalized = [_candidate(c, known) for c in candidates]
    ids = [c["candidate_id"] for c in normalized]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate candidate IDs")
    rationale = _text(rationale, "Selection or deferral rationale", minimum=8)
    if selected_id is not None and (not isinstance(selected_id, str) or selected_id not in ids):
        raise ValueError("Select a known method or defer")
    if selected_id is not None and len(normalized) < 2:
        raise ValueError("At least two candidates required for a comparative selection; otherwise defer")
    status = "READY_FOR_DRAFT_PLANNING" if selected_id is not None else "DEFERRED_INSUFFICIENT_COMPARISON"
    result = {
        "schema": SCHEMA, "context_id": context_id(run), "status": status,
        "origin": "SYNTHETIC_FIXTURE" if run.mode == "demo" else "RESEARCHER_ASSESSED",
        "candidates": normalized, "selected_candidate_id": selected_id, "rationale": rationale,
        "uncertainty": {
            "source_count": len(known),
            "machine_flagged_tensions": deepcopy(run.audit.conflicts),
            "source_scope": "Abstract-level claim review; method records are researcher assertions.",
            "method_references_independently_checked": False,
            "confidence_calibrated": False,
            "scientific_execution_verified": False,
            "note": "Selection is a reasoned draft decision, not a probability of success or proven superiority.",
        },
    }
    result["evaluation_id"] = _digest(result)
    return result


def save_evaluation(run: Run, candidates: list[dict], *, selected_id: str | None,
                    rationale: str) -> dict:
    result = build_evaluation(run, candidates, selected_id=selected_id, rationale=rationale)
    run.evaluation = result
    run.plan = None
    run.log.append({"time_utc": datetime.now(timezone.utc).isoformat(),
                    "role": "Method Evaluation", "status": result["status"],
                    "note": "Researcher-saved method comparison; evaluation_id=" + result["evaluation_id"]})
    return result


def require_evaluation(run: Run) -> dict:
    saved = run.evaluation
    if not isinstance(saved, dict) or saved.get("schema") != SCHEMA:
        raise PermissionError("Complete method evaluation before planning")
    rebuilt = build_evaluation(run, saved.get("candidates"),
                               selected_id=saved.get("selected_candidate_id"),
                               rationale=saved.get("rationale"))
    if rebuilt != saved:
        raise PermissionError("Method evaluation is stale or changed; review it again")
    if saved["status"] != "READY_FOR_DRAFT_PLANNING":
        raise PermissionError("Method comparison was deferred; planning remains blocked")
    return saved


def selected_method(evaluation: dict) -> dict:
    return next(c for c in evaluation["candidates"]
                if c["candidate_id"] == evaluation["selected_candidate_id"])


def suggest_methods(run: Run, *, model_client) -> list[dict]:
    """One optional model call; output remains an editable, unreviewed proposal."""
    known = allowed_sources(run)
    if run.mode != "live" or model_client is None:
        raise PermissionError("Method suggestions require a live, connected model")
    if run.backend not in ("none", "unspecified") and getattr(model_client, "backend", "unspecified") != run.backend:
        raise PermissionError("Use this run's original model backend for method suggestions")
    response = model_client.json("Method Evaluation Agent", (
        'Propose up to two alternative research methods relevant to the hypotheses. '
        'Return {"candidates":[{"name":string,"evidence_ids":[provided IDs],"scope":string,'
        '"comparison":{"expected_value":string,"resources":string,"validation":string,'
        '"limitations":string,"novelty":string}}]}. '
        'Use only provided abstracts and reviewed claims. Say UNKNOWN when details, '
        'novelty or resources cannot be inferred. Do not claim code was executed or '
        'that structure confidence establishes binding, pH selectivity or agonism. '
        'Do not treat complementary pipeline tools as competing methods. '
        'Return an empty candidates list if no meaningful alternatives are supported.'
    ), {"question": run.question, "hypotheses": run.hypotheses,
        "papers": [p.__dict__ for p in run.papers if p.paper_id in known],
        "reviewed_claims": [c.__dict__ for c in approved_claims(run)]})
    raw = response.get("candidates")
    if not isinstance(raw, list) or len(raw) > 2:
        raise ValueError("Expected zero to two method proposals")
    out = []
    for i, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            raise ValueError("Invalid method proposal")
        candidate = blank_candidate(f"M{i}", item.get("name", ""))
        candidate.update({key: item.get(key) for key in ("evidence_ids", "scope", "comparison")})
        checked = _candidate(candidate, known)
        out.append({key: checked[key] for key in candidate})
    return out


def demo_candidates() -> list[dict]:
    """Invented strategies; no real experiment or method comparison was run."""
    out = []
    for cid, name, scope, benefit in [
        ("M1", "[FICTIONAL] Matched-condition replication",
         "Compare the same invented binder under matched buffer and assay conditions.",
         "Could separate a buffer confound from an apparent pH effect."),
        ("M2", "[FICTIONAL] Cross-assay confirmation",
         "Compare the invented observation across independent assay formats.",
         "Could expose assay-format dependence before interpreting the pH response."),
    ]:
        c = blank_candidate(cid, name)
        c.update(evidence_ids=["SYNTHETIC:A", "SYNTHETIC:B", "SYNTHETIC:C"], scope=scope)
        c["comparison"] = {
            "expected_value": benefit,
            "resources": "Unknown; obtain protocol, materials and access estimates.",
            "validation": "Require independent controls and repeats; no experiment has run.",
            "limitations": "Entirely fictional abstracts; actual methods and effect sizes unavailable.",
            "novelty": "Not assessed; these are illustrative validation strategies.",
        }
        out.append(c)
    return out


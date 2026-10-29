"""Audit-only trajectory graph for FrontierLab runs.

This graph complements, but never replaces, the evidence graph.

- evidence_graph.py answers: "does this plan step trace back to checked evidence?"
- trajectory_graph.py answers: "what process events occurred during this run?"

Trajectory nodes never participate in the EXTRACTED-only plan-step approval gate.
No prompts, model outputs, secrets or authorization headers are stored here.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json

from .error_taxonomy import classify_run
from .models import Run
from .process_metrics import stage_completion

SCHEMA = "frontierlab.trajectory-graph.v1"

STAGES = ("research", "evidence", "hypothesis", "evaluation", "planning")

ROLE_STAGE = {
    "Evidence Extraction Agent": "evidence",
    "Adversarial Skeptic Agent": "hypothesis",
    "Hypothesis Agent": "hypothesis",
    "Method Evaluation Agent": "evaluation",
    "Scientific Planning Agent": "planning",
    "Retriever": "evidence",
    "Extraction Agent": "evidence",
    "Evidence Auditor": "evidence",
    "Audit Gate": "evidence",
    "Human Claim Review": "evidence",
    "Skeptic Agent": "hypothesis",
    "Method Evaluation": "evaluation",
    "Planning Agent": "planning",
    "Citation Gate": "planning",
}

HUMAN_STAGE = {
    "CLAIM_REVIEW_SAVED": "evidence",
    "METHOD_EVALUATION_SAVED": "evaluation",
    "PLANNING_APPROVED": "planning",
    "PLAN_STEP_APPROVED": "planning",
}


def _digest(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(raw.encode("utf-8")).hexdigest()[:16]


def _safe_usage(receipt: dict) -> dict:
    usage = receipt.get("usage", {})
    if not isinstance(usage, dict):
        return {}
    return {
        key: value
        for key in ("prompt_tokens", "completion_tokens", "total_tokens")
        if isinstance((value := usage.get(key)), int) and value >= 0
    }


def _stage_for_signal(event: dict) -> str | None:
    role = event.get("role")
    if isinstance(role, str) and role in ROLE_STAGE:
        return ROLE_STAGE[role]
    source = event.get("source")
    if source == "audit.rejected_claims":
        return "evidence"
    if source == "audit.conflicts":
        return "evidence"
    if source == "inference.receipts":
        return "hypothesis"
    return None


def build_trajectory_graph(run: Run) -> dict:
    completion = stage_completion(run)
    nodes: list[dict] = []
    edges: list[dict] = []

    def add_node(node: dict) -> str:
        nodes.append(node)
        return node["id"]

    def add_edge(source: str, target: str, relation: str, *, basis: str) -> None:
        edges.append({
            "source": source,
            "target": target,
            "relation": relation,
            "basis": basis,
        })

    # Stable workflow spine.
    for index, stage in enumerate(STAGES, 1):
        add_node({
            "id": f"stage:{stage}",
            "type": "stage",
            "stage": stage,
            "index": index,
            "completed": completion["stages"][stage],
        })
    for left, right in zip(STAGES, STAGES[1:]):
        add_edge(f"stage:{left}", f"stage:{right}", "NEXT_STAGE", basis="fixed_frontierlab_workflow")

    # Recorded model-call receipts. Hashes and usage only; never prompt/output content.
    receipts = []
    if isinstance(run.inference, dict) and isinstance(run.inference.get("receipts"), list):
        receipts = run.inference["receipts"]
    for index, receipt in enumerate(receipts, 1):
        if not isinstance(receipt, dict):
            continue
        role = receipt.get("role")
        stage = ROLE_STAGE.get(role, "research") if isinstance(role, str) else "research"
        call_id = f"model_call:{index}:{_digest([receipt.get('input_sha256'), role, receipt.get('started_at_utc')])}"
        node = {
            "id": call_id,
            "type": "model_call",
            "index": index,
            "role": role,
            "status": receipt.get("status"),
            "requested_model": receipt.get("requested_model"),
            "reported_model": receipt.get("reported_model"),
            "started_at_utc": receipt.get("started_at_utc"),
            "input_sha256": receipt.get("input_sha256"),
            "output_sha256": receipt.get("output_sha256"),
            "finish_reason": receipt.get("finish_reason"),
            "usage": _safe_usage(receipt),
            "elapsed_seconds": receipt.get("elapsed_seconds"),
        }
        add_node(node)
        add_edge(call_id, f"stage:{stage}", "EXECUTED_IN", basis="receipt_role_mapping")

    # Consequential human actions recorded by interventions.py.
    for index, event in enumerate(getattr(run, "human_events", []) or [], 1):
        if not isinstance(event, dict) or event.get("schema") != "frontierlab.human-intervention.v1":
            continue
        kind = event.get("kind")
        stage = HUMAN_STAGE.get(kind)
        event_id = f"human_event:{event.get('event_id') or _digest([index, kind, event.get('artifact_id')])}"
        add_node({
            "id": event_id,
            "type": "human_event",
            "index": index,
            "kind": kind,
            "time_utc": event.get("time_utc"),
            "artifact_id": event.get("artifact_id"),
            "actor_label": event.get("actor_label"),
            "identity_verified": bool(event.get("identity_verified", False)),
            "severity": event.get("severity"),
        })
        if stage:
            add_edge(event_id, f"stage:{stage}", "INTERVENED_IN", basis="human_event_kind_mapping")

    # Researcher method evaluation as a first-class process artifact.
    if isinstance(run.evaluation, dict):
        evaluation_id = str(run.evaluation.get("evaluation_id") or _digest(run.evaluation))
        eid = f"method_evaluation:{evaluation_id}"
        add_node({
            "id": eid,
            "type": "method_evaluation",
            "evaluation_id": evaluation_id,
            "status": run.evaluation.get("status"),
            "selected_candidate_id": run.evaluation.get("selected_candidate_id"),
            "origin": run.evaluation.get("origin"),
        })
        add_edge(eid, "stage:evaluation", "RECORDED_IN", basis="run.evaluation")

    # Rejected claims become visible trajectory artifacts even when they cannot attach
    # to the evidence graph because they lack a valid source.
    for index, rejected in enumerate(run.audit.rejected_claims, 1):
        if not isinstance(rejected, dict):
            continue
        claim = rejected.get("claim") if isinstance(rejected.get("claim"), dict) else {}
        rid = f"rejected_claim:{index}:{_digest([rejected.get('reason'), claim])}"
        add_node({
            "id": rid,
            "type": "rejected_claim",
            "index": index,
            "reason": rejected.get("reason"),
            "paper_id": claim.get("paper_id"),
            "claim_key": claim.get("claim_key"),
        })
        add_edge(rid, "stage:evidence", "REJECTED_IN", basis="audit.rejected_claims")

    # Deterministically classified blocking/failure/tension signals.
    taxonomy = classify_run(run)
    for index, event in enumerate(taxonomy.get("events", []), 1):
        if not isinstance(event, dict):
            continue
        sid = f"process_signal:{index}:{_digest(event)}"
        add_node({
            "id": sid,
            "type": "process_signal",
            "index": index,
            "category": event.get("category"),
            "source": event.get("source"),
            "role": event.get("role"),
            "status": event.get("status"),
        })
        stage = _stage_for_signal(event)
        if stage:
            add_edge(sid, f"stage:{stage}", "SIGNALED_IN", basis="error_taxonomy_mapping")

    return {
        "schema": SCHEMA,
        "question_sha256": sha256(run.question.encode("utf-8")).hexdigest(),
        "mode": run.mode,
        "backend": run.backend,
        "model": run.model,
        "nodes": sorted(nodes, key=lambda node: node["id"]),
        "edges": sorted(edges, key=lambda edge: (edge["source"], edge["target"], edge["relation"])),
        "note": (
            "Audit-only process graph. It does not participate in scientific evidence "
            "gating and does not prove that a model output is scientifically correct."
        ),
    }


def summarize(graph: dict) -> dict:
    types = Counter(
        node.get("type")
        for node in graph.get("nodes", [])
        if isinstance(node, dict) and isinstance(node.get("type"), str)
    )
    relations = Counter(
        edge.get("relation")
        for edge in graph.get("edges", [])
        if isinstance(edge, dict) and isinstance(edge.get("relation"), str)
    )
    return {
        "nodes_by_type": dict(sorted(types.items())),
        "edges_by_relation": dict(sorted(relations.items())),
        "model_calls": types.get("model_call", 0),
        "human_events": types.get("human_event", 0),
        "rejected_claims": types.get("rejected_claim", 0),
        "process_signals": types.get("process_signal", 0),
    }


def to_json(graph: dict) -> str:
    return json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True)

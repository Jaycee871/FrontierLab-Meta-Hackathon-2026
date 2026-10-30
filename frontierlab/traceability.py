"""Measured provenance coverage for FrontierLab evidence graphs.

Trace coverage is about whether research artifacts can be followed back to known
sources. It is not an accuracy, entailment, or scientific-validity metric.
"""
from __future__ import annotations

from collections import defaultdict

from .evidence_graph import SCHEMA as EVIDENCE_GRAPH_SCHEMA

IN_SCOPE_TYPES = ("claim", "hypothesis", "plan_step")


def _index(graph: dict):
    nodes = {node["id"]: node for node in graph.get("nodes", []) if isinstance(node, dict)}
    outgoing = defaultdict(list)
    for edge in graph.get("edges", []):
        if isinstance(edge, dict):
            outgoing[edge.get("source")].append(edge)
    return nodes, outgoing


def _headline_scope(node: dict) -> bool:
    ntype = node.get("type")
    if ntype == "claim":
        return node.get("gate_status") == "PASSED_EVIDENCE_GATE"
    return ntype in {"hypothesis", "plan_step"}


def trace_one(graph: dict, artifact_id: str) -> dict:
    """Trace one artifact to papers and evaluate strict EXTRACTED completeness."""
    if not isinstance(graph, dict) or graph.get("schema") != EVIDENCE_GRAPH_SCHEMA:
        raise ValueError("Expected a FrontierLab evidence graph v2")

    nodes, outgoing = _index(graph)
    artifact = nodes.get(artifact_id)
    if artifact is None:
        raise ValueError("Unknown artifact")
    if artifact.get("type") not in IN_SCOPE_TYPES:
        raise ValueError("Trace coverage applies to claim/hypothesis/plan_step artifacts")

    papers = set()
    blocking_edges = []
    unresolved = []
    dead_ends = []
    seen = set()
    stack = [artifact_id]

    while stack:
        node_id = stack.pop()
        if node_id in seen:
            continue
        seen.add(node_id)

        node = nodes.get(node_id)
        if node is None:
            dead_ends.append(node_id)
            continue
        if node.get("type") == "paper":
            papers.add(node_id.split(":", 1)[1])
            continue

        unknown = node.get("unresolved_evidence_ids")
        if isinstance(unknown, list) and unknown:
            unresolved.extend(str(value) for value in unknown)

        edges = outgoing.get(node_id, [])
        if not edges:
            dead_ends.append(node_id)
            continue

        for edge in edges:
            if edge.get("provenance") != "EXTRACTED":
                blocking_edges.append({
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "relation": edge.get("relation"),
                    "provenance": edge.get("provenance"),
                    "reason": edge.get("reason"),
                })
            target = edge.get("target")
            if isinstance(target, str):
                stack.append(target)
            else:
                dead_ends.append(str(target))

    source_traceable = bool(papers)
    strict_extracted = bool(
        papers and not blocking_edges and not unresolved and not dead_ends
    )
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact.get("type"),
        "source_traceable": source_traceable,
        "strict_extracted": strict_extracted,
        "papers": sorted(papers),
        "blocking_edges": blocking_edges,
        "unresolved_evidence_ids": sorted(set(unresolved)),
        "dead_ends": sorted(set(dead_ends)),
    }


def trace_coverage(graph: dict) -> dict:
    """Calculate measured trace coverage over downstream-eligible artifacts.

    Headline denominator:
      * claims that passed the evidence gate;
      * all hypotheses;
      * all plan steps.

    Rejected claim nodes remain visible as exclusions rather than silently
    lowering or inflating the headline denominator.
    """
    if not isinstance(graph, dict) or graph.get("schema") != EVIDENCE_GRAPH_SCHEMA:
        raise ValueError("Expected a FrontierLab evidence graph v2")

    nodes = [node for node in graph.get("nodes", []) if isinstance(node, dict)]
    scoped = [node for node in nodes if _headline_scope(node)]
    records = [trace_one(graph, node["id"]) for node in scoped]

    total = len(records)
    source_traced = sum(record["source_traceable"] for record in records)
    strict = sum(record["strict_extracted"] for record in records)

    by_type = {}
    for ntype in IN_SCOPE_TYPES:
        subset = [record for record in records if record["artifact_type"] == ntype]
        denom = len(subset)
        by_type[ntype] = {
            "artifacts": denom,
            "source_traceable": sum(record["source_traceable"] for record in subset),
            "strict_extracted": sum(record["strict_extracted"] for record in subset),
            "source_trace_coverage": round(
                sum(record["source_traceable"] for record in subset) / denom, 4
            ) if denom else None,
            "strict_extracted_coverage": round(
                sum(record["strict_extracted"] for record in subset) / denom, 4
            ) if denom else None,
        }

    rejected_claims = sum(
        node.get("type") == "claim"
        and node.get("gate_status") == "REJECTED_BY_EVIDENCE_GATE"
        for node in nodes
    )

    return {
        "schema": "frontierlab.trace-coverage.v1",
        "scope_definition": (
            "Claims that passed the evidence gate plus all hypotheses and plan steps."
        ),
        "material_artifacts": total,
        "source_traceable_artifacts": source_traced,
        "strict_extracted_artifacts": strict,
        "source_trace_coverage": round(source_traced / total, 4) if total else None,
        "strict_extracted_coverage": round(strict / total, 4) if total else None,
        "excluded_rejected_claims": rejected_claims,
        "unattached_rejected_claims": int(graph.get("unattached_rejected_claims", 0) or 0),
        "by_type": by_type,
        "artifacts": records,
        "scientific_accuracy_measured": False,
        "semantic_entailment_verified": False,
        "note": (
            "Source Trace Coverage measures whether an in-scope artifact reaches at least "
            "one known Paper. Strict Extracted Coverage additionally requires every reachable "
            "provenance edge to be EXTRACTED, no unresolved source IDs, and no dead ends. "
            "Neither metric proves that a scientific claim is true."
        ),
    }


def source_audit_summary(graph: dict) -> dict:
    if not isinstance(graph, dict) or graph.get("schema") != EVIDENCE_GRAPH_SCHEMA:
        raise ValueError("Expected a FrontierLab evidence graph v2")

    nodes = [node for node in graph.get("nodes", []) if isinstance(node, dict)]
    edges = [edge for edge in graph.get("edges", []) if isinstance(edge, dict)]

    passed_claims = [
        node for node in nodes
        if node.get("type") == "claim"
        and node.get("gate_status") == "PASSED_EVIDENCE_GATE"
    ]
    anchored_claim_ids = {
        edge.get("source")
        for edge in edges
        if edge.get("source", "").startswith("claim:")
        and edge.get("provenance") == "EXTRACTED"
        and edge.get("relation") in {"SUPPORTS", "CONTRADICTS"}
    }

    return {
        "papers": sum(node.get("type") == "paper" for node in nodes),
        "passages": sum(node.get("type") == "passage" for node in nodes),
        "passed_claims": len(passed_claims),
        "anchored_passed_claims": sum(
            node.get("id") in anchored_claim_ids for node in passed_claims
        ),
        "rejected_claims_attached": sum(
            node.get("type") == "claim"
            and node.get("gate_status") == "REJECTED_BY_EVIDENCE_GATE"
            for node in nodes
        ),
        "rejected_claims_unattached": int(graph.get("unattached_rejected_claims", 0) or 0),
        "source_audit_is_semantic_entailment": False,
    }

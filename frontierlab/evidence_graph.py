"""Provenance-tagged evidence graph: Paper <- Passage <- Claim <- Hypothesis <- PlanStep.

Plain dicts only (no graph library, no services). Every edge carries a provenance tag:

* EXTRACTED - read directly from the record and deterministically checked. For a claim
  edge this means the claim passed the existing verbatim evidence gate AND its quote is
  located in the cited abstract (``claim_verification.quote_anchored`` /
  ``locate_quote``). For CITES / DERIVED_FROM edges it means an explicit,
  validated source-ID reference.
* INFERRED - asserted by the model (e.g. a Muse Glimmer stance) without an anchored
  quote. Shown to the researcher; never counted as evidence.
* AMBIGUOUS - labels conflict (mixed / inconclusive stance, opposite stances from the
  same paper on the same claim key, or a reviewer verdict of CONTRADICTED /
  INSUFFICIENT). Shown to the researcher; never counted as evidence.

Gate rule: a PlanStep may be approved only if every edge reachable from it is
EXTRACTED and every path ends at a Paper. This is ADDITIONAL to the existing gates in
``audit``, ``review`` and ``pipeline``; it relaxes none of them. Like those gates it
proves that a passage exists, not that the claim follows from it.

The EXTRACTED / INFERRED / AMBIGUOUS vocabulary is borrowed, as an idea only, from the
open-source Graphify project (Graphify Labs, Apache-2.0); no Graphify code is used.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import asdict
from html import escape

from .claim_verification import locate_quote, normalize_excerpt, quote_anchored
from .models import Paper, Run

SCHEMA = "frontierlab.evidence-graph.v1"
NODE_TYPES = ("paper", "passage", "claim", "hypothesis", "plan_step")
RELATIONS = ("SUPPORTS", "CONTRADICTS", "CITES", "DERIVED_FROM")
PROVENANCE = ("EXTRACTED", "INFERRED", "AMBIGUOUS")
_STANCE_RELATION = {"supports": "SUPPORTS", "contradicts": "CONTRADICTS"}
_CONFLICTING_REVIEW = {"CONTRADICTED", "INSUFFICIENT"}


def _h(*parts) -> str:
    raw = json.dumps(parts, ensure_ascii=False, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def classify_claim_edge(paper: Paper, stance: str, quote: str, *, gate_passed: bool,
                        conflicting_stance: bool = False, review_label: str | None = None) -> dict:
    """Relation, provenance and passage span for one claim -> source edge.

    EXTRACTED requires gate_passed (the claim survived ``audit.validate_claims``) and a
    quote located verbatim in ``paper.abstract``. Conflicting labels give AMBIGUOUS,
    which overrides EXTRACTED. Anything else is INFERRED.
    """
    stance = str(stance or "").lower()
    relation = _STANCE_RELATION.get(stance, "CITES")
    quote = quote if isinstance(quote, str) else ""
    span = locate_quote(paper.abstract, quote) if gate_passed and quote.strip() else None
    if stance not in _STANCE_RELATION:
        return {"relation": relation, "provenance": "AMBIGUOUS", "span": span,
                "reason": f"Stance '{stance or 'missing'}' does not decide the claim"}
    if conflicting_stance:
        return {"relation": relation, "provenance": "AMBIGUOUS", "span": span,
                "reason": "Opposite stances from the same source on the same claim key"}
    if review_label in _CONFLICTING_REVIEW:
        return {"relation": relation, "provenance": "AMBIGUOUS", "span": span,
                "reason": f"Researcher verdict {review_label} conflicts with the model stance"}
    if span is not None:
        return {"relation": relation, "provenance": "EXTRACTED", "span": span,
                "reason": "Quote located verbatim in the cited abstract (not semantic entailment)"}
    why = ("Claim failed the verbatim evidence gate" if not gate_passed
           else "No quote located in the cited abstract")
    return {"relation": relation, "provenance": "INFERRED", "span": None,
            "reason": why + "; model stance only"}


class _G:
    def __init__(self):
        self.nodes: dict[str, dict] = {}
        self.edges: dict[tuple, dict] = {}

    def node(self, nid: str, ntype: str, **attrs) -> str:
        self.nodes.setdefault(nid, {"id": nid, "type": ntype, **attrs})
        return nid

    def edge(self, source, target, relation, provenance, reason, **attrs):
        key = (source, target, relation)
        self.edges.setdefault(key, {"source": source, "target": target, "relation": relation,
                                    "provenance": provenance, "reason": reason, **attrs})


def _review_labels(run: Run) -> dict[tuple, str]:
    labels = {}
    for case in (run.review or {}).get("cases", []) if isinstance(run.review, dict) else []:
        key = (case.get("paper_id"), case.get("claim_key"), case.get("claim"), case.get("evidence_quote"))
        labels[key] = case.get("review_label")
    return labels


def _eligible_claims(run: Run) -> list:
    """Claims a hypothesis may be derived from: human-approved ones once a review exists."""
    if run.mode == "live" and run.review:
        from .review import approved_claims
        try:
            return approved_claims(run)
        except ValueError:
            return []
    return list(run.audit.verified_claims)


def build_evidence_graph(run: Run, *, previous: dict | None = None) -> dict:
    """Build the provenance graph from a run's papers, audited claims, hypotheses and plan.

    ``previous`` carries researcher step approvals forward only for steps that still
    exist (same content-derived id) and still satisfy the EXTRACTED-only path rule.
    """
    g = _G()
    papers = {p.paper_id: p for p in run.papers}
    for p in run.papers:
        g.node(f"paper:{p.paper_id}", "paper", label=p.title, paper=asdict(p))

    verified = list(run.audit.verified_claims)
    stances = defaultdict(set)
    for c in verified:
        stances[(c.paper_id, c.claim_key)].add(c.stance)
    reviews = _review_labels(run)
    claim_ids: dict[int, str] = {}

    def add_claim(paper_id, claim_key, stance, statement, quote, *, gate_passed, status):
        paper = papers[paper_id]
        cid = f"claim:{_h(paper_id, claim_key, stance, statement, quote, gate_passed)}"
        review = reviews.get((paper_id, claim_key, statement, quote)) if gate_passed else None
        both = {"supports", "contradicts"} <= stances.get((paper_id, claim_key), set())
        verdict = classify_claim_edge(paper, stance, quote, gate_passed=gate_passed,
                                      conflicting_stance=gate_passed and both, review_label=review)
        g.node(cid, "claim", label=statement[:160], paper_id=paper_id, claim_key=claim_key,
               stance=stance, statement=statement, evidence_quote=quote, gate_status=status,
               review_label=review)
        target = f"paper:{paper_id}"
        if verdict["span"] is not None:
            start, end = verdict["span"]
            target = g.node(f"passage:{paper_id}:{start}-{end}", "passage",
                            label=paper.abstract[start:end][:160], paper_id=paper_id,
                            start=start, end=end, text=paper.abstract[start:end])
            g.edge(target, f"paper:{paper_id}", "CITES", "EXTRACTED",
                   "Passage located at these character offsets of the abstract")
        g.edge(cid, target, verdict["relation"], verdict["provenance"], verdict["reason"])
        return cid

    for i, c in enumerate(verified):
        if c.paper_id in papers:
            claim_ids[i] = add_claim(c.paper_id, c.claim_key, c.stance, c.statement,
                                     c.evidence_quote if c.passage_matched else "",
                                     gate_passed=True, status="PASSED_EVIDENCE_GATE")
    skipped = 0
    for rejected in run.audit.rejected_claims:
        item = rejected.get("claim", {}) if isinstance(rejected, dict) else {}
        pid = str(item.get("paper_id", "")) if isinstance(item, dict) else ""
        if pid not in papers:
            skipped += 1  # no known source to attach to; already listed in the audit
            continue
        raw_quote = item.get("evidence_quote", item.get("quote", ""))
        add_claim(pid, str(item.get("claim_key", "")).strip().lower(),
                  str(item.get("stance", "")).lower(), str(item.get("statement", "")).strip(),
                  raw_quote if isinstance(raw_quote, str) else "", gate_passed=False,
                  status="REJECTED_BY_EVIDENCE_GATE")

    eligible = {id(c) for c in _eligible_claims(run)}
    eligible_ids = [claim_ids[i] for i, c in enumerate(verified) if i in claim_ids and id(c) in eligible]
    eligible_by_paper = defaultdict(list)
    for cid in eligible_ids:
        eligible_by_paper[g.nodes[cid]["paper_id"]].append(cid)

    hyp_nodes = []
    for i, hyp in enumerate(run.hypotheses or []):
        if not isinstance(hyp, dict):
            continue
        ids = [x for x in hyp.get("evidence_ids", []) if isinstance(x, str)] if isinstance(
            hyp.get("evidence_ids"), list) else []
        hid = g.node(f"hypothesis:{i + 1}-{_h(hyp.get('text'), ids)}", "hypothesis",
                     label=str(hyp.get("text", ""))[:160], text=str(hyp.get("text", "")),
                     evidence_ids=ids)
        hyp_nodes.append((hid, set(ids)))
        for pid in ids:
            if pid not in papers:
                g.nodes[hid].setdefault("unresolved_evidence_ids", []).append(pid)
                continue
            if eligible_by_paper[pid]:
                for cid in eligible_by_paper[pid]:
                    g.edge(hid, cid, "DERIVED_FROM", "EXTRACTED",
                           "Hypothesis explicitly cites this claim's source ID")
            else:
                g.edge(hid, f"paper:{pid}", "CITES", "INFERRED",
                       "Cited source has no eligible (gate-passed / reviewer-approved) claim")

    plan = run.plan if isinstance(run.plan, dict) else None
    if plan:
        plan_ids = [x for x in plan.get("evidence_ids", []) if isinstance(x, str)]
        for i, step in enumerate(plan.get("steps", []) or []):
            sid = g.node(f"step:{i + 1}-{_h(step, plan_ids, plan.get('evaluation_id'))}", "plan_step",
                         label=str(step)[:160], text=str(step), index=i + 1,
                         plan_evidence_ids=plan_ids, plan_status=plan.get("status"))
            for hid, ids in hyp_nodes:
                if ids & set(plan_ids):
                    g.edge(sid, hid, "DERIVED_FROM", "EXTRACTED",
                           "Plan cites a source this hypothesis cites")

    graph = {
        "schema": SCHEMA, "question": run.question, "mode": run.mode,
        "nodes": sorted(g.nodes.values(), key=lambda n: n["id"]),
        "edges": sorted(g.edges.values(), key=lambda e: (e["source"], e["target"], e["relation"])),
        "unattached_rejected_claims": skipped,
        "approvals": {},
        "note": ("EXTRACTED means a passage was located and ID references were checked; it is "
                 "NOT semantic entailment. INFERRED and AMBIGUOUS edges never count as evidence."),
    }
    for sid, record in ((previous or {}).get("approvals") or {}).items():
        if any(n["id"] == sid for n in graph["nodes"]) and step_gate(graph, sid)["approvable"]:
            graph["approvals"][sid] = record
    return graph


def _index(graph: dict):
    nodes = {n["id"]: n for n in graph.get("nodes", [])}
    out = defaultdict(list)
    for e in graph.get("edges", []):
        out[e["source"]].append(e)
    return nodes, out


def step_gate(graph: dict, step_id: str) -> dict:
    """Apply the EXTRACTED-only path rule to one plan step.

    Approvable only if: the step reaches at least one Paper, every reachable edge is
    EXTRACTED, every path terminates at a Paper, no hypothesis on the way has unresolved
    source IDs, and every source the plan cites is reached.
    """
    nodes, out = _index(graph)
    step = nodes.get(step_id)
    if not step or step.get("type") != "plan_step":
        return {"step_id": step_id, "approvable": False, "reasons": ["Unknown plan step"],
                "papers": [], "blocking_edges": []}
    reasons, blocking, papers, seen = [], [], set(), set()
    stack = [step_id]
    while stack:
        nid = stack.pop()
        if nid in seen:
            continue
        seen.add(nid)
        node = nodes.get(nid)
        if node is None:
            reasons.append(f"Dangling reference {nid}")
            continue
        if node["type"] == "paper":
            papers.add(nid.split(":", 1)[1])
            continue
        if node.get("unresolved_evidence_ids"):
            reasons.append(f"{nid} cites unknown source IDs {node['unresolved_evidence_ids']}")
        edges = out.get(nid, [])
        if not edges:
            reasons.append(f"{nid} has no path to a Paper")
        for e in edges:
            if e["provenance"] != "EXTRACTED":
                blocking.append(e)
                reasons.append(f"{e['provenance']} edge {e['source']} -{e['relation']}-> {e['target']}: {e['reason']}")
            stack.append(e["target"])
    missing = sorted(set(step.get("plan_evidence_ids", [])) - papers)
    if missing:
        reasons.append(f"Plan cites sources with no evidence path from this step: {missing}")
    if not papers:
        reasons.append("No Paper reached")
    return {"step_id": step_id, "approvable": not reasons, "reasons": reasons,
            "papers": sorted(papers), "blocking_edges": blocking}


def approve_plan_step(graph: dict, step_id: str, *, reviewer: str, note: str) -> dict:
    """Record a researcher's approval of one plan step; refuses unless step_gate passes."""
    gate = step_gate(graph, step_id)
    if not gate["approvable"]:
        raise PermissionError("Plan step not approvable: " + "; ".join(gate["reasons"]))
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("Reviewer name required")
    if not isinstance(note, str) or len(note.strip()) < 8:
        raise ValueError("Approval requires a rationale (8+ characters)")
    graph["approvals"][step_id] = {"reviewer": reviewer.strip(), "note": note.strip()[:1500],
                                   "papers": gate["papers"]}
    return graph


def refresh_evidence_graph(run: Run) -> dict:
    """Rebuild ``run.evidence_graph`` from the current run, keeping still-valid approvals."""
    run.evidence_graph = build_evidence_graph(run, previous=run.evidence_graph)
    return run.evidence_graph


def summarize(graph: dict) -> dict:
    counts = {p: 0 for p in PROVENANCE}
    for e in graph.get("edges", []):
        counts[e["provenance"]] += 1
    types = defaultdict(int)
    for n in graph.get("nodes", []):
        types[n["type"]] += 1
    steps = [step_gate(graph, n["id"]) for n in graph.get("nodes", []) if n["type"] == "plan_step"]
    return {
        "nodes": dict(types), "edges_by_provenance": counts,
        "plan_steps": len(steps), "plan_steps_approvable": sum(s["approvable"] for s in steps),
        "plan_steps_approved": len(graph.get("approvals", {})),
        "surfaced_for_review": [e for e in graph.get("edges", []) if e["provenance"] != "EXTRACTED"],
    }


def to_json(graph: dict) -> str:
    return json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True)


def load_graph(data: str | dict) -> dict:
    """Parse and re-verify a graph.json. Fails closed if any EXTRACTED claim edge or
    passage cannot be re-anchored against the abstract stored in the graph."""
    graph = json.loads(data) if isinstance(data, str) else json.loads(json.dumps(data))
    if not isinstance(graph, dict) or graph.get("schema") != SCHEMA:
        raise ValueError("Not a FrontierLab evidence graph")
    nodes = {}
    for n in graph.get("nodes", []):
        if not isinstance(n, dict) or n.get("type") not in NODE_TYPES or not isinstance(n.get("id"), str):
            raise ValueError("Invalid node")
        nodes[n["id"]] = n
    for e in graph.get("edges", []):
        if (not isinstance(e, dict) or e.get("relation") not in RELATIONS
                or e.get("provenance") not in PROVENANCE
                or e.get("source") not in nodes or e.get("target") not in nodes):
            raise ValueError("Invalid edge")
    for n in nodes.values():
        if n["type"] == "passage":
            paper = nodes.get(f"paper:{n.get('paper_id')}")
            if paper is None:
                raise ValueError("Passage without paper")
            abstract = paper["paper"]["abstract"]
            start, end = n.get("start"), n.get("end")
            if (not isinstance(start, int) or not isinstance(end, int)
                    or abstract[start:end] != n.get("text")
                    or locate_quote(abstract, n.get("text", "")) is None):
                raise ValueError(f"Passage {n['id']} does not anchor in its abstract")
    for e in graph.get("edges", []):
        src, tgt = nodes[e["source"]], nodes[e["target"]]
        if e["provenance"] == "EXTRACTED" and src["type"] == "claim":
            if tgt["type"] != "passage" or src.get("gate_status") != "PASSED_EVIDENCE_GATE":
                raise ValueError(f"EXTRACTED claim edge {src['id']} lacks a gate-passed passage")
            if not quote_anchored(tgt["text"], src.get("evidence_quote", "")) or (
                normalize_excerpt(tgt["text"]) != normalize_excerpt(src.get("evidence_quote", ""))
            ):
                raise ValueError(f"EXTRACTED claim edge {src['id']} quote does not match its passage")
    if not isinstance(graph.get("approvals", {}), dict):
        raise ValueError("Invalid approvals")
    for sid in graph.get("approvals", {}):
        if not step_gate(graph, sid)["approvable"]:
            raise ValueError(f"Recorded approval for {sid} violates the EXTRACTED-only path rule")
    return graph


# -- compact monochrome view (Flatland plate style: line art, rule style not colour) --
_COLUMNS = ("paper", "passage", "claim", "hypothesis", "plan_step")
_TITLES = {"paper": "PAPERS", "passage": "PASSAGES", "claim": "CLAIMS",
           "hypothesis": "HYPOTHESES", "plan_step": "PLAN STEPS"}
_DASH = {"EXTRACTED": "", "INFERRED": ' stroke-dasharray="5 4"', "AMBIGUOUS": ' stroke-dasharray="1 3"'}


def to_svg(graph: dict, *, max_nodes: int = 60) -> str | None:
    """Layered line-art drawing. Returns None when the graph is too large to read."""
    nodes = graph.get("nodes", [])
    if not nodes or len(nodes) > max_nodes:
        return None
    col_w, row_h, top, left = 190, 46, 64, 24
    rows = {t: [n for n in nodes if n["type"] == t] for t in _COLUMNS}
    pos = {}
    for c, t in enumerate(_COLUMNS):
        for r, n in enumerate(rows[t]):
            pos[n["id"]] = (left + c * col_w + 8, top + r * row_h + 14)
    height = top + max(1, max(len(v) for v in rows.values())) * row_h + 56
    width = left * 2 + col_w * len(_COLUMNS)
    font = "font-family=\"Georgia, 'Times New Roman', serif\""
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-label="Evidence provenance graph">',
           f'<rect width="{width}" height="{height}" fill="#1E1E1E" stroke="#F2F2F2" stroke-width="1"/>']
    for c, t in enumerate(_COLUMNS):
        x = left + c * col_w + 8
        out.append(f'<text x="{x}" y="34" fill="#F2F2F2" font-size="11" letter-spacing="2.5" {font}>{_TITLES[t]}</text>')
        out.append(f'<line x1="{x}" y1="42" x2="{x + col_w - 30}" y2="42" stroke="#F2F2F2" stroke-width="1" opacity="0.55"/>')
    for e in graph.get("edges", []):
        if e["source"] in pos and e["target"] in pos:
            (x1, y1), (x2, y2) = pos[e["source"]], pos[e["target"]]
            out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2 + 150}" y2="{y2}" stroke="#F2F2F2" '
                       f'stroke-width="1"{_DASH[e["provenance"]]}><title>{escape(e["provenance"] + " " + e["relation"])}</title></line>')
    for n in nodes:
        x, y = pos[n["id"]]
        shape = {"paper": f'<rect x="{x - 5}" y="{y - 5}" width="10" height="10"',
                 "passage": f'<line x1="{x - 6}" y1="{y}" x2="{x + 6}" y2="{y}"',
                 "claim": f'<polygon points="{x},{y - 6} {x + 6},{y + 5} {x - 6},{y + 5}"',
                 "hypothesis": f'<polygon points="{x - 6},{y} {x - 3},{y - 5} {x + 3},{y - 5} {x + 6},{y} {x + 3},{y + 5} {x - 3},{y + 5}"',
                 "plan_step": f'<rect x="{x - 6}" y="{y - 6}" width="12" height="12"'}[n["type"]]
        out.append(f'{shape} fill="#1E1E1E" stroke="#F2F2F2" stroke-width="1"/>')
        label = n.get("label", "") or n["id"]
        label = label if len(label) <= 24 else label[:23] + "…"
        out.append(f'<text x="{x + 12}" y="{y + 4}" fill="#CFCFCF" font-size="10" {font}>'
                   f'<title>{escape(n["id"])}</title>{escape(label)}</text>')
    ly = height - 22
    for i, (name, dash) in enumerate(_DASH.items()):
        lx = left + 8 + i * 190
        out.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 36}" y2="{ly}" stroke="#F2F2F2" stroke-width="1"{dash}/>')
        out.append(f'<text x="{lx + 44}" y="{ly + 4}" fill="#CFCFCF" font-size="10" {font}>{name}</text>')
    out.append("</svg>")
    return "".join(out)

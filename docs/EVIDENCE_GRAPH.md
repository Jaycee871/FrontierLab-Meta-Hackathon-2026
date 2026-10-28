# Evidence graph: provenance for every plan step

Module: [`frontierlab/evidence_graph.py`](../frontierlab/evidence_graph.py) · Tests: [`tests/test_evidence_graph.py`](../tests/test_evidence_graph.py)

FrontierLab builds a small, typed graph from each run, linking the plan back to the literature:

```
Paper <-CITES- Passage <-SUPPORTS|CONTRADICTS- Claim <-DERIVED_FROM- Hypothesis <-DERIVED_FROM- PlanStep
```

The graph is made of plain Python dicts. It uses no graph library, no database and no service, and nothing was added to `requirements.txt`. It is stored in `Run.evidence_graph`, so it is part of `Run.as_dict()` and the "complete provenance JSON" export. The Streamlit app also offers it as a separate `graph.json` download.

## Nodes

| Type | Built from | Key fields |
| --- | --- | --- |
| `paper` | `Run.papers` (the existing `Paper` dataclass, stored in full) | `paper` (all fields, including the abstract) |
| `passage` | A claim's quote, located in the abstract | `paper_id`, `start`, `end` (character offsets into the original abstract), `text` |
| `claim` | `Run.audit.verified_claims`, plus rejected claims whose source ID is known | `stance`, `statement`, `evidence_quote`, `gate_status`, `review_label` |
| `hypothesis` | `Run.hypotheses` | `text`, `evidence_ids` |
| `plan_step` | `Run.plan["steps"]` | `text`, `index`, `plan_evidence_ids` |

## Provenance tags

Every edge carries exactly one tag:

- **EXTRACTED.** For a claim edge, this means the claim passed the existing verbatim evidence gate (`audit.validate_claims`) **and** its quote is located in the cited abstract. The location check is the same anchor rule that `claim_verification.audit_predictions` uses (`quote_anchored` / `locate_quote`, both built on `normalize_excerpt`). For `CITES` and `DERIVED_FROM` edges, it means an explicit, checked source-ID reference.
- **INFERRED.** The model (for example Muse Glimmer) asserted a stance, but no anchored quote exists. Either the claim was rejected by the evidence gate, or it is an unquoted synthetic fixture. INFERRED edges are also used when a hypothesis cites a source that has no eligible claim.
- **AMBIGUOUS.** The labels conflict: the stance is `mixed` or `inconclusive`, the same source gives opposite stances on the same claim key, or a researcher verdict of CONTRADICTED or INSUFFICIENT contradicts the model's stance. AMBIGUOUS overrides EXTRACTED.

INFERRED and AMBIGUOUS edges are listed for the researcher in the UI ("Surfaced for researcher review"). **They never count as evidence.**

## Gate rule for plan steps

`step_gate(graph, step_id)` makes a step approvable only if all of these hold:

- every edge reachable from the step is EXTRACTED;
- every path ends at a Paper;
- no hypothesis on the way cites an unknown source ID;
- every source the plan cites is reached.

`approve_plan_step()` refuses with `PermissionError` otherwise. It also requires a reviewer name and a rationale of 8 or more characters.

This gate is **additional**. It relaxes none of the existing gates. The verbatim evidence gate, human claim review, two-source rule, method evaluation and planning approval all still apply. Once a review exists, hypotheses link only to claims the researcher marked SUPPORTED.

A recorded approval is kept when the graph is rebuilt only if the step still exists unchanged (step IDs are content hashes) and still passes the rule. `load_graph()` re-checks every passage and every EXTRACTED claim edge against the abstract stored in the graph, as well as every recorded approval. A tampered or stale `graph.json` therefore fails closed.

As with the verbatim gate, EXTRACTED proves that a passage exists. **It does not prove that the claim follows from that passage.**

## In the app

Section "6 · Evidence graph" contains:

- counts by provenance;
- a monochrome line-art drawing (solid = EXTRACTED, dashed = INFERRED, dotted = AMBIGUOUS). The drawing is omitted when the graph has more than 60 nodes;
- the surfaced non-evidence links;
- a per-step gate table, and an approval form that lists only eligible steps;
- the `graph.json` download.

## Public API

`build_evidence_graph(run, previous=None)`, `refresh_evidence_graph(run)`, `classify_claim_edge(...)`, `step_gate(graph, step_id)`, `approve_plan_step(graph, step_id, reviewer=, note=)`, `summarize(graph)`, `to_json(graph)`, `load_graph(text_or_dict)`, `to_svg(graph, max_nodes=60)`.

## Prior art and credit

The EXTRACTED / INFERRED / AMBIGUOUS edge vocabulary is borrowed, as an idea, from [Graphify](https://github.com/Graphify-Labs/graphify) by Graphify Labs (Apache-2.0), which tags knowledge-graph edges this way for code and documents. FrontierLab does **not** depend on, bundle or copy Graphify. This module is an independent implementation, so no NOTICE entry is required.

There is one deliberate difference. For non-code documents, Graphify's tag is reported by the extracting model itself. Here, EXTRACTED is assigned only by FrontierLab's deterministic quote-location check. The model's own label can never produce it.

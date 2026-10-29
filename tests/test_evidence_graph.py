"""Provenance-tagged evidence graph: classification, path gate and graph.json round trip."""
import json
from copy import deepcopy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from frontierlab.audit import validate_claims
from frontierlab.claim_verification import audit_predictions, locate_quote, quote_anchored
from frontierlab.claim_benchmark import benchmark
from frontierlab.evidence_graph import (
    approval_digest, approve_plan_step, build_evidence_graph, classify_claim_edge, load_graph,
    run_fingerprints, step_gate, summarize, to_json, to_svg,
)
from frontierlab.review import source_fingerprint
from frontierlab.models import Paper, Run
from frontierlab.pipeline import run_research
from tests.test_recorded_method_selection import load_selected_run

APP = Path(__file__).resolve().parents[1] / "app.py"
ABS_A = ("Histidine scanning of the  CDR loops produced variants whose HER2 binding "
         "was strongly reduced at pH 6.0 relative to pH 7.4 in surface plasmon resonance.")
ABS_B = "A second library confirmed pH-dependent release of the target in endosomal conditions."
QUOTE_A = "HER2 binding was strongly REDUCED at pH 6.0"   # case / whitespace differ
QUOTE_B = "confirmed pH-dependent release of the target"


def paper(pid, abstract):
    return Paper(paper_id=pid, title=f"Paper {pid}", year="2024", authors="A. Author",
                 abstract=abstract, url=f"https://europepmc.org/{pid}")


PAPERS = [paper("PMC1", ABS_A), paper("PMC2", ABS_B)]


def live_run(claims, *, hypotheses=None, plan=None):
    audit = validate_claims(PAPERS, claims, require_quote=True)
    return Run(question="q", mode="live", model="meta/muse-glimmer-30b", papers=PAPERS,
               audit=audit, hypotheses=hypotheses or [], skeptic={}, log=[], plan=plan)


def claim(pid, quote, stance="supports", key="ph-release", statement=None):
    return {"paper_id": pid, "claim_key": key, "stance": stance, "limitation": "abstract only",
            "statement": statement or f"{pid} reports pH-dependent behaviour.", "evidence_quote": quote}


def edges_from(graph, prefix):
    return [e for e in graph["edges"] if e["source"].startswith(prefix)]


# -- provenance classification ------------------------------------------------------

def test_extracted_requires_gate_and_located_quote_with_exact_offsets():
    v = classify_claim_edge(PAPERS[0], "supports", QUOTE_A, gate_passed=True)
    assert (v["relation"], v["provenance"]) == ("SUPPORTS", "EXTRACTED")
    start, end = v["span"]
    assert ABS_A[start:end] == "HER2 binding was strongly reduced at pH 6.0"


def test_inferred_when_glimmer_stance_has_no_anchored_quote():
    v = classify_claim_edge(PAPERS[0], "contradicts", "binding increased at acidic pH", gate_passed=True)
    assert (v["relation"], v["provenance"], v["span"]) == ("CONTRADICTS", "INFERRED", None)
    # Even a real substring is INFERRED if the claim never passed the evidence gate.
    v = classify_claim_edge(PAPERS[0], "supports", QUOTE_A, gate_passed=False)
    assert v["provenance"] == "INFERRED" and v["span"] is None


@pytest.mark.parametrize("kwargs", [
    {"stance": "mixed"}, {"stance": "inconclusive"},
    {"stance": "supports", "conflicting_stance": True},
    {"stance": "supports", "review_label": "CONTRADICTED"},
    {"stance": "supports", "review_label": "INSUFFICIENT"},
])
def test_ambiguous_when_labels_conflict_even_if_quote_is_anchored(kwargs):
    stance = kwargs.pop("stance")
    v = classify_claim_edge(PAPERS[0], stance, QUOTE_A, gate_passed=True, **kwargs)
    assert v["provenance"] == "AMBIGUOUS"


def test_same_source_opposite_stances_become_ambiguous_in_built_graph():
    run = live_run([claim("PMC1", QUOTE_A, "supports"),
                    claim("PMC1", QUOTE_A, "contradicts", statement="PMC1 reports the opposite.")])
    graph = build_evidence_graph(run)
    assert {e["provenance"] for e in edges_from(graph, "claim:")} == {"AMBIGUOUS"}


# -- unanchored quotes never yield EXTRACTED ---------------------------------------

@pytest.mark.parametrize("quote", [
    "", "   ", "HER2 binding was strongly increased at pH 6.0", "pH 6.0",  # too short for the gate
    ABS_B[:40],  # anchored in a DIFFERENT paper's abstract
])
def test_unanchored_or_gate_rejected_quote_never_extracted(quote):
    run = live_run([claim("PMC1", quote)])
    graph = build_evidence_graph(run)
    claim_edges = edges_from(graph, "claim:")
    assert claim_edges and all(e["provenance"] != "EXTRACTED" for e in claim_edges)
    assert not any(n["type"] == "passage" for n in graph["nodes"])


def test_tampered_graph_claiming_extracted_for_unanchored_quote_fails_closed():
    graph = build_evidence_graph(live_run([claim("PMC1", QUOTE_A)]))
    forged = deepcopy(graph)
    node = next(n for n in forged["nodes"] if n["type"] == "claim")
    node["evidence_quote"] = "HER2 binding was strongly increased at pH 6.0"
    with pytest.raises(ValueError):
        load_graph(to_json(forged))
    forged = deepcopy(graph)
    passage = next(n for n in forged["nodes"] if n["type"] == "passage")
    passage["text"] = "binding was abolished entirely"
    with pytest.raises(ValueError):
        load_graph(to_json(forged))
    forged = deepcopy(build_evidence_graph(live_run([claim("PMC1", "not in the abstract at all, invented")])))
    edge = next(e for e in forged["edges"] if e["source"].startswith("claim:"))
    edge["provenance"] = "EXTRACTED"
    with pytest.raises(ValueError):
        load_graph(forged)


def test_shared_anchor_helpers_agree_with_audit_predictions():
    papers, rows = benchmark()
    catalog = {p.paper_id: p for p in papers}
    result = {c["id"]: c for c in audit_predictions(papers, rows)["cases"]}
    for row in rows:
        p = catalog.get(row["paper_id"])
        anchored = bool(p and quote_anchored(p.abstract, row["quote"]))
        assert anchored == result[row["id"]]["quote_in_abstract"]
        assert (p is not None and locate_quote(p.abstract, row["quote"]) is not None) == anchored


# -- EXTRACTED-only path rule ---------------------------------------------------------

def planned_run(claims, hyp_ids, plan_ids):
    return live_run(claims,
                    hypotheses=[{"text": "pH-dependent release is reproducible.", "evidence_ids": hyp_ids}],
                    plan={"steps": ["Preregister matched-pH assays.", "Replicate independently."],
                          "evidence_ids": plan_ids, "status": "DRAFT_FOR_RESEARCHER_REVIEW"})


def step_ids(graph):
    return [n["id"] for n in graph["nodes"] if n["type"] == "plan_step"]


def test_step_approvable_only_through_all_extracted_path():
    run = planned_run([claim("PMC1", QUOTE_A), claim("PMC2", QUOTE_B)], ["PMC1", "PMC2"], ["PMC1", "PMC2"])
    graph = build_evidence_graph(run)
    for sid in step_ids(graph):
        gate = step_gate(graph, sid)
        assert gate["approvable"], gate["reasons"]
        assert gate["papers"] == ["PMC1", "PMC2"]
    approve_plan_step(graph, step_ids(graph)[0], reviewer="Jaycee", note="Both passages checked in full text.")
    assert summarize(graph)["plan_steps_approved"] == 1


def test_one_inferred_link_blocks_the_whole_step():
    run = planned_run([claim("PMC1", QUOTE_A), claim("PMC2", "an invented sentence that is not in the abstract")],
                      ["PMC1", "PMC2"], ["PMC1", "PMC2"])
    graph = build_evidence_graph(run)
    for sid in step_ids(graph):
        gate = step_gate(graph, sid)
        assert not gate["approvable"]
        assert any(e["provenance"] == "INFERRED" for e in gate["blocking_edges"])
        with pytest.raises(PermissionError):
            approve_plan_step(graph, sid, reviewer="Jaycee", note="Trying to approve anyway.")
    surfaced = summarize(graph)["surfaced_for_review"]
    assert any(e["provenance"] == "INFERRED" and e["target"] == "paper:PMC2" for e in surfaced)


def test_ambiguous_link_and_missing_paths_block_steps():
    run = planned_run([claim("PMC1", QUOTE_A, "mixed"), claim("PMC2", QUOTE_B)], ["PMC1", "PMC2"], ["PMC1", "PMC2"])
    graph = build_evidence_graph(run)
    assert not any(step_gate(graph, s)["approvable"] for s in step_ids(graph))
    # Plan cites a source the hypothesis never reaches; unknown hypothesis IDs block too.
    graph = build_evidence_graph(planned_run([claim("PMC1", QUOTE_A), claim("PMC2", QUOTE_B)], ["PMC1"], ["PMC1", "PMC2"]))
    assert not any(step_gate(graph, s)["approvable"] for s in step_ids(graph))
    graph = build_evidence_graph(planned_run([claim("PMC1", QUOTE_A)], ["PMC1", "PMC404"], ["PMC1"]))
    assert not any(step_gate(graph, s)["approvable"] for s in step_ids(graph))
    assert not step_gate(graph, "step:unknown")["approvable"]


def test_demo_fixture_has_no_extracted_claims_and_plan_steps_stay_blocked():
    run = run_research("q", "q", mode="demo")
    graph = run.evidence_graph
    assert graph and all(e["provenance"] != "EXTRACTED" for e in edges_from(graph, "claim:"))
    run.plan = {"steps": ["Mock step"], "evidence_ids": ["SYNTHETIC:A"], "status": "SYNTHETIC_TEST_ONLY"}
    graph = build_evidence_graph(run)
    assert not step_gate(graph, step_ids(graph)[0])["approvable"]


def test_recorded_reviewed_nim_run_builds_extracted_paths_to_real_abstracts():
    run = load_selected_run()
    run.plan = {"steps": ["Compare M2 against matched-pH controls."], "evidence_ids": ["PMC6927761"],
                "status": "DRAFT_FOR_RESEARCHER_REVIEW", "evaluation_id": run.evaluation["evaluation_id"]}
    graph = build_evidence_graph(run)
    passages = [n for n in graph["nodes"] if n["type"] == "passage"]
    assert len(passages) == len(run.audit.verified_claims) == 2
    papers = {p.paper_id: p for p in run.papers}
    for n in passages:
        assert papers[n["paper_id"]].abstract[n["start"]:n["end"]] == n["text"]
    assert step_gate(graph, step_ids(graph)[0])["approvable"]


def test_approvals_survive_rebuild_only_while_path_stays_extracted():
    run = planned_run([claim("PMC1", QUOTE_A), claim("PMC2", QUOTE_B)], ["PMC1", "PMC2"], ["PMC1", "PMC2"])
    graph = build_evidence_graph(run)
    sid = step_ids(graph)[0]
    approve_plan_step(graph, sid, reviewer="Jaycee", note="Checked against full text.")
    assert sid in build_evidence_graph(run, previous=graph)["approvals"]
    weaker = planned_run([claim("PMC1", QUOTE_A), claim("PMC2", "not anchored in the abstract, invented")],
                         ["PMC1", "PMC2"], ["PMC1", "PMC2"])
    assert build_evidence_graph(weaker, previous=graph)["approvals"] == {}
    forged = deepcopy(build_evidence_graph(weaker))
    forged["approvals"] = {step_ids(forged)[0]: {"reviewer": "x", "note": "forged approval"}}
    with pytest.raises(ValueError):
        load_graph(forged)


# -- approval integrity on load ------------------------------------------------------

def approved_graph():
    run = planned_run([claim("PMC1", QUOTE_A), claim("PMC2", QUOTE_B)], ["PMC1", "PMC2"], ["PMC1", "PMC2"])
    graph = build_evidence_graph(run)
    sid = step_ids(graph)[0]
    approve_plan_step(graph, sid, reviewer="Jaycee", note="Checked against full text.")
    return run, graph, sid


def test_approval_record_has_utc_timestamp_and_step_binding_and_loads():
    run, graph, sid = approved_graph()
    record = graph["approvals"][sid]
    assert record["approved_at_utc"].endswith("+00:00")
    assert record["approval_digest"] == approval_digest(graph, sid, record["papers"])
    assert load_graph(to_json(graph)) == graph
    assert load_graph(graph, expected_fingerprints=run_fingerprints(run)) == graph


@pytest.mark.parametrize("reviewer", ["", "   ", None])
def test_load_rejects_injected_approval_without_reviewer(reviewer):
    _, graph, sid = approved_graph()
    forged = deepcopy(graph)
    forged["approvals"][sid]["reviewer"] = reviewer
    with pytest.raises(ValueError, match="Reviewer name required"):
        load_graph(forged)
    with pytest.raises(ValueError):
        approve_plan_step(deepcopy(graph), sid, reviewer=reviewer, note="Checked against full text.")


@pytest.mark.parametrize("note", ["", "       ", "short", None])
def test_load_rejects_injected_approval_with_empty_or_short_note(note):
    _, graph, sid = approved_graph()
    forged = deepcopy(graph)
    forged["approvals"][sid]["note"] = note
    with pytest.raises(ValueError, match="rationale"):
        load_graph(forged)
    with pytest.raises(ValueError):
        approve_plan_step(deepcopy(graph), sid, reviewer="Jaycee", note=note)


def test_load_rejects_pre_fix_approval_shape_and_bad_timestamps():
    _, graph, sid = approved_graph()
    old_shape = deepcopy(graph)
    old_shape["approvals"][sid] = {"reviewer": "Jaycee", "note": "Checked against full text.",
                                   "papers": ["PMC1", "PMC2"]}
    with pytest.raises(ValueError, match="missing or unexpected fields"):
        load_graph(old_shape)
    for stamp in ["", "yesterday", "2026-10-29T12:00:00", "2026-10-29T20:00:00+08:00", 0]:
        forged = deepcopy(graph)
        forged["approvals"][sid]["approved_at_utc"] = stamp
        with pytest.raises(ValueError, match="timestamp"):
            load_graph(forged)


def test_load_rejects_approval_transplanted_to_another_step():
    _, graph, sid = approved_graph()
    other = [s for s in step_ids(graph) if s != sid][0]
    assert step_gate(graph, other)["approvable"]  # the target step is itself approvable
    forged = deepcopy(graph)
    forged["approvals"] = {other: deepcopy(graph["approvals"][sid])}
    with pytest.raises(ValueError, match="not bound to this step"):
        load_graph(forged)


def test_load_rejects_approval_after_step_text_rewritten_in_place():
    _, graph, sid = approved_graph()
    forged = deepcopy(graph)
    step = next(n for n in forged["nodes"] if n["id"] == sid)
    step["text"] = "Skip the matched-pH controls."
    with pytest.raises(ValueError, match="not bound to this step"):
        load_graph(forged)


def rewrite_paper_consistently(graph, *, refresh_fingerprint):
    """Self-consistent forgery: abstract, passage and claim quote all say 'raised'."""
    forged = deepcopy(graph)
    nodes = {n["id"]: n for n in forged["nodes"]}
    paper = nodes["paper:PMC1"]
    paper["paper"]["abstract"] = paper["paper"]["abstract"].replace("strongly reduced", "strongly raised!")
    fake = "HER2 binding was strongly raised! at pH 6.0"
    start = paper["paper"]["abstract"].index(fake)
    for n in forged["nodes"]:
        if n["type"] == "passage" and n["paper_id"] == "PMC1":
            n["start"], n["end"], n["text"] = start, start + len(fake), fake
        if n["type"] == "claim" and n["paper_id"] == "PMC1":
            n["evidence_quote"] = fake
    if refresh_fingerprint:
        paper["source_fingerprint"] = source_fingerprint(Paper(**paper["paper"]))
        for sid, record in forged["approvals"].items():
            record["approval_digest"] = approval_digest(forged, sid, record["papers"])
    return forged


def test_load_rejects_self_consistent_abstract_passage_quote_rewrite():
    _, graph, _ = approved_graph()
    with pytest.raises(ValueError, match="source fingerprint"):
        load_graph(rewrite_paper_consistently(graph, refresh_fingerprint=False))


def test_fully_rehashed_rewrite_is_caught_against_the_trusted_run():
    # graph.json is unsigned: a forger who recomputes every hash passes the standalone
    # check; binding to the trusted run's source fingerprints still rejects it.
    run, graph, _ = approved_graph()
    forged = rewrite_paper_consistently(graph, refresh_fingerprint=True)
    load_graph(forged)  # documented limit of an unsigned file
    with pytest.raises(ValueError, match="differs from the trusted source record"):
        load_graph(forged, expected_fingerprints=run_fingerprints(run))
    with pytest.raises(ValueError, match="differ from the trusted run"):
        load_graph(graph, expected_fingerprints={"PMC1": run_fingerprints(run)["PMC1"]})


def test_legacy_v1_graph_is_rejected_not_migrated():
    _, graph, _ = approved_graph()
    legacy = deepcopy(graph)
    legacy["schema"] = "frontierlab.evidence-graph.v1"
    with pytest.raises(ValueError, match="Legacy evidence graph"):
        load_graph(legacy)


def test_rebuild_drops_approval_once_source_record_changes():
    run, graph, sid = approved_graph()
    assert sid in build_evidence_graph(run, previous=graph)["approvals"]
    run.papers = [paper("PMC1", ABS_A + " Revised."), PAPERS[1]]
    assert build_evidence_graph(run, previous=graph)["approvals"] == {}


# -- serialisation round trip -----------------------------------------------------------

def test_graph_json_round_trip_and_run_as_dict():
    run = planned_run([claim("PMC1", QUOTE_A), claim("PMC2", QUOTE_B), claim("PMC2", "made-up, unanchored claim quote")],
                      ["PMC1", "PMC2"], ["PMC1", "PMC2"])
    graph = build_evidence_graph(run)
    approve_plan_step(graph, step_ids(graph)[1], reviewer="Jaycee", note="Reviewed with full methods.")
    text = to_json(graph)
    assert load_graph(text) == graph
    assert to_json(load_graph(text)) == text
    assert build_evidence_graph(run) == build_evidence_graph(run)  # deterministic
    run.evidence_graph = graph
    exported = json.loads(json.dumps(run.as_dict()))
    assert load_graph(exported["evidence_graph"]) == graph
    with pytest.raises(ValueError):
        load_graph({**graph, "schema": "other"})


def test_svg_is_monochrome_line_art_and_bounded():
    graph = build_evidence_graph(planned_run([claim("PMC1", QUOTE_A)], ["PMC1"], ["PMC1"]))
    svg = to_svg(graph)
    assert svg.startswith("<svg") and 'stroke-dasharray="5 4"' in svg  # INFERRED legend is dashed
    colours = {c for c in ("#1E1E1E", "#F2F2F2", "#CFCFCF") if c in svg}
    assert colours == {"#1E1E1E", "#F2F2F2", "#CFCFCF"}
    assert "gradient" not in svg.lower() and "filter" not in svg.lower()
    assert to_svg(graph, max_nodes=2) is None


def test_app_shows_graph_panel_and_download_in_demo():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    app.button[0].click().run()
    assert not app.exception
    assert any(e.label.startswith("6 · Evidence graph") for e in app.expander)
    run = app.session_state["frontier_result"]
    assert run.evidence_graph["schema"] == "frontierlab.evidence-graph.v2"
    assert any("NOT counted as evidence" in w.value for w in app.warning)

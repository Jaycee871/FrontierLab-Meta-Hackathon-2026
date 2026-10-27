from copy import deepcopy
from dataclasses import replace
import json
import pytest

from frontierlab.evaluation import (
    CHECKS, blank_candidate, build_evaluation, demo_candidates,
    require_evaluation, save_evaluation, suggest_methods,
)
from frontierlab.models import Paper
from frontierlab.pipeline import run_research, continue_after_review, make_plan
from frontierlab.review import review_packet, save_review
from frontierlab.reporting import export_json


class Model:
    model = "MOCK-muse-glimmer-NOT-LIVE"
    def __init__(self):
        self.calls = []
        self.plan_changes = {}
        self.proposals = None

    def json(self, role, task, payload):
        self.calls.append((role, payload))
        if role == "Evidence Extraction Agent":
            return {"claims": [{
                "paper_id": payload["paper"]["paper_id"], "claim_key": "condition",
                "stance": "supports", "statement": "The response varies by conditions.",
                "limitation": "Abstract only", "evidence_quote": payload["paper"]["abstract"],
            }]}
        if role == "Adversarial Skeptic Agent":
            return {"explanation": "Mock review", "uncertainties": ["No actual experiment."]}
        if role == "Hypothesis Agent":
            return {"hypotheses": [{"text": "Test condition dependence.",
                    "evidence_ids": ["PMID:1", "PMID:2"], "rationale": "Mock evidence."}]}
        if role == "Method Evaluation Agent":
            return {"candidates": self.proposals}
        if role == "Scientific Planning Agent":
            return {"objective": "Mock objective", "steps": ["Review unresolved checks."],
                    "controls": ["Matched conditions"], "metrics": ["Mock response"],
                    "replication": ["Independent repeats"], "falsification": ["Effect disappears"],
                    "evidence_ids": ["PMID:1"], "limitations": "Not executed.",
                    **self.plan_changes}
        raise AssertionError(role)


def live(*, synthesize=True):
    model = Model()
    papers = [Paper(f"PMID:{i}", f"Article {i}", "2026", "Author",
              "The response depended on experimental conditions in this fictional test.",
              f"https://example.org/{i}") for i in (1, 2)]
    run = run_research("A mock method comparison", "x", mode="live", model_client=model,
                       retrieve=lambda q,n: papers)
    packet = review_packet(run)
    save_review(run, [{"case_id": c["case_id"], "review_label": "SUPPORTED"}
                      for c in packet["cases"]])
    if synthesize:
        continue_after_review(run, model_client=model)
    return run, model


def candidates():
    out = []
    for i in (1, 2):
        c = blank_candidate(f"M{i}", f"Mock strategy {i}")
        c.update(evidence_ids=[f"PMID:{i}"], scope="Only the mock assay conditions.")
        c["comparison"] = {key: "Unknown; inspect full methods before use."
                           for key in c["comparison"]}
        out.append(c)
    return out


def save(run):
    return save_evaluation(run, candidates(), selected_id="M1",
                           rationale="Mock preference; no real efficacy claim.")


def test_planning_cannot_skip_method_evaluation_or_call_model():
    run, model = live()
    before = len(model.calls)
    with pytest.raises(PermissionError, match="evaluation"):
        make_plan(run, model_client=model, approved=True)
    assert len(model.calls) == before and run.plan is None


def test_unknown_reproducibility_is_exported_without_confidence_or_execution_claims():
    run, _ = live()
    result = save(run)
    method = result["candidates"][0]
    assert len(method["open_checks"]) == len(CHECKS)
    assert method["reproducibility_status"] == "INCOMPLETE_DOCUMENTATION"
    assert result["uncertainty"]["confidence_calibrated"] is False
    assert result["uncertainty"]["scientific_execution_verified"] is False
    assert result["origin"] == "RESEARCHER_ASSESSED"
    assert json.loads(export_json(run))["evaluation"] == result


@pytest.mark.parametrize("count", [0, 1])
def test_insufficient_comparison_can_be_saved_as_deferral_but_never_plans(count):
    run, model = live()
    result = save_evaluation(run, candidates()[:count], selected_id=None,
                             rationale="Insufficient basis to compare alternative methods.")
    assert result["status"] == "DEFERRED_INSUFFICIENT_COMPARISON"
    before = len(model.calls)
    with pytest.raises(PermissionError, match="deferred"):
        make_plan(run, model_client=model, approved=True)
    assert len(model.calls) == before


def test_single_method_cannot_be_selected_as_comparative_winner():
    run, _ = live()
    with pytest.raises(ValueError, match="two candidates"):
        save_evaluation(run, candidates()[:1], selected_id="M1", rationale="Mock rationale")


@pytest.mark.parametrize("mutation", ["unknown_source", "duplicate", "no_scope", "no_reason", "bad_state"])
def test_invalid_method_dossiers_do_not_commit_a_selection(mutation):
    run, _ = live()
    cs = candidates()
    if mutation == "unknown_source":
        cs[0]["evidence_ids"] = ["FABRICATED"]
    elif mutation == "duplicate":
        cs[1]["candidate_id"] = "M1"
    elif mutation == "no_scope":
        cs[0]["scope"] = ""
    elif mutation == "no_reason":
        cs[0]["comparison"]["limitations"] = ""
    else:
        cs[0]["checks"]["code"]["status"] = "REPRODUCTION_PASSED"
    with pytest.raises(ValueError):
        save_evaluation(run, cs, selected_id="M1", rationale="Mock comparison rationale")
    assert run.evaluation is None


def test_documented_material_requires_location_but_does_not_claim_execution():
    run, _ = live()
    cs = candidates()
    for c in cs:
        for check in c["checks"].values():
            check.update(status="documented", detail="Researcher reports the item is described.")
    with pytest.raises(ValueError, match="location"):
        save_evaluation(run, cs, selected_id="M1", rationale="Mock comparison rationale")
    for c in cs:
        for check in c["checks"].values():
            check["reference"] = "Researcher-supplied methods location; not fetched."
    result = save_evaluation(run, cs, selected_id="M1", rationale="Mock comparison rationale")
    assert result["candidates"][0]["reproducibility_status"] == "DOCUMENTED_NOT_EXECUTED"
    assert result["uncertainty"]["method_references_independently_checked"] is False


@pytest.mark.parametrize("change", ["question", "abstract", "hypothesis", "review", "candidate", "selection"])
def test_stale_or_mutated_evaluation_blocks_plan_before_model_call(change):
    run, model = live()
    save(run)
    if change == "question":
        run.question += " New scope."
    elif change == "abstract":
        run.papers[0] = replace(run.papers[0], abstract=run.papers[0].abstract + " Revision.")
    elif change == "hypothesis":
        run.hypotheses[0]["text"] += " Changed."
    elif change == "review":
        run.review["cases"][0]["review_note"] = "Changed assessment."
    elif change == "candidate":
        run.evaluation["candidates"][0]["scope"] = "Changed target."
    else:
        run.evaluation["selected_candidate_id"] = "M2"
    before = len(model.calls)
    with pytest.raises((PermissionError, ValueError)):
        make_plan(run, model_client=model, approved=True)
    assert len(model.calls) == before and run.plan is None


def test_plan_is_bound_to_researcher_selected_method_and_open_checks():
    run, model = live()
    saved = save(run)
    model.plan_changes = {"selected_candidate_id": "M2", "status": "SCIENTIFICALLY_VALIDATED"}
    make_plan(run, model_client=model, approved=True)
    assert run.plan["selected_candidate_id"] == "M1"
    assert run.plan["evaluation_id"] == saved["evaluation_id"]
    assert run.plan["status"] == "DRAFT_FOR_RESEARCHER_REVIEW"
    assert run.plan["selected_method"]["open_checks"]
    assert model.calls[-1][1]["method_evaluation"]["selected_candidate_id"] == "M1"


@pytest.mark.parametrize("bad_field", ["controls", "metrics", "replication", "falsification"])
def test_missing_plan_design_elements_are_rejected(bad_field):
    run, model = live()
    save(run)
    model.plan_changes[bad_field] = []
    with pytest.raises(ValueError, match=bad_field):
        make_plan(run, model_client=model, approved=True)
    assert run.plan is None


def test_plan_must_cite_selected_methods_sources():
    run, model = live()
    cs = candidates()
    cs[0]["evidence_ids"] = ["PMID:1", "PMID:2"]
    save_evaluation(run, cs, selected_id="M1", rationale="Mock comparison rationale")
    with pytest.raises(ValueError, match="selected method"):
        make_plan(run, model_client=model, approved=True)


def test_rereview_invalidates_hypotheses_evaluation_and_plan():
    run, model = live()
    save(run)
    make_plan(run, model_client=model, approved=True)
    cs = review_packet(run)["cases"]
    save_review(run, [{"case_id": c["case_id"], "review_label": "SUPPORTED"} for c in cs])
    assert run.hypotheses == [] and run.evaluation is None and run.plan is None


def test_regenerated_hypotheses_invalidate_old_evaluation():
    run, model = live()
    save(run)
    make_plan(run, model_client=model, approved=True)
    continue_after_review(run, model_client=model)
    assert run.evaluation is None and run.plan is None


def test_model_proposals_are_unreviewed_and_do_not_self_certify_reproduction():
    run, model = live()
    model.proposals = deepcopy(candidates())
    model.proposals[0]["checks"]["code"]["status"] = "documented"
    proposed = suggest_methods(run, model_client=model)
    assert proposed[0]["checks"]["code"]["status"] == "unknown"
    assert run.evaluation is None
    assert model.calls[-1][0] == "Method Evaluation Agent"
    assert {p["paper_id"] for p in model.calls[-1][1]["papers"]} == {"PMID:1", "PMID:2"}


def test_fabricated_model_proposal_source_is_rejected():
    run, model = live()
    model.proposals = candidates()
    model.proposals[0]["evidence_ids"] = ["FAKE"]
    with pytest.raises(ValueError, match="reviewed source"):
        suggest_methods(run, model_client=model)


def test_no_method_inference_before_hypothesis_and_review():
    run, model = live(synthesize=False)
    before = len(model.calls)
    with pytest.raises(ValueError, match="hypotheses"):
        suggest_methods(run, model_client=model)
    assert len(model.calls) == before


def test_fictional_five_stage_flow_remains_explicitly_fictional():
    run = run_research("Mock binder question", "unused", mode="demo")
    save_evaluation(run, demo_candidates(), selected_id="M1",
                    rationale="Illustrate a matched-condition plan with fictional data.")
    make_plan(run, approved=True)
    assert run.evaluation["origin"] == "SYNTHETIC_FIXTURE"
    assert run.plan["status"] == "SYNTHETIC_TEST_ONLY"
    assert run.plan["selected_candidate_id"] == "M1"
    assert not run.evaluation["uncertainty"]["scientific_execution_verified"]


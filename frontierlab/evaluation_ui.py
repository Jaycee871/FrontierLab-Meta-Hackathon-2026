"""Streamlit method review form; does not run scientific tools or remote inference."""
from __future__ import annotations
import json

from .evaluation import (CHECKS, CHECK_STATES, CRITERIA, allowed_sources,
                         blank_candidate, context_id, demo_candidates,
                         save_evaluation, suggest_methods, require_evaluation)
from .openweight import OpenWeightClient

CHECK_LABELS = {
    "data": "Data / inputs", "code": "Code / model version",
    "environment": "Environment / dependencies", "parameters": "Parameters / seeds",
    "protocol": "Protocol / controls", "metrics": "Evaluation metrics",
}
CRITERION_LABELS = {
    "expected_value": "Expected research value and rationale",
    "resources": "Required resources / feasibility",
    "validation": "Validation needed before interpreting results",
    "limitations": "Limitations and uncertainty",
    "novelty": "Novelty / diversity evidence (UNKNOWN if unassessed)",
}


def render_evaluation(run):
    import streamlit as st
    st.subheader("4 · Method evaluation")
    if not run.hypotheses:
        st.info("Generate hypotheses after evidence review before comparing methods.")
        return
    try:
        sources = allowed_sources(run)
        ctx = context_id(run)
    except (ValueError, PermissionError) as exc:
        st.warning(str(exc))
        return
    state_key = "method_drafts_" + ctx
    if state_key not in st.session_state:
        st.session_state[state_key] = (
            run.evaluation["candidates"] if run.evaluation and run.evaluation.get("context_id") == ctx
            else demo_candidates() if run.mode == "demo"
            else [blank_candidate("M1"), blank_candidate("M2")]
        )
    revision_key = "method_revision_" + ctx
    st.session_state.setdefault(revision_key, 0)
    st.caption(
        "Record where each method detail was found. Documented means researcher-reported "
        "documentation, not a verified download, executed reproduction or proven scientific result. "
        "Only the saved evaluation is used for planning; save any edits before continuing."
    )
    if run.mode == "demo":
        st.warning("FICTIONAL strategies and evidence. No model or laboratory experiment has run.")
    elif st.button("Suggest methods with the local Meta model", key="suggest_" + ctx):
        try:
            proposals = suggest_methods(run, model_client=OpenWeightClient())
            st.session_state[state_key] = proposals
            st.session_state[revision_key] += 1
            st.success("Editable model proposals loaded. Inspect sources and review every field.")
        except (ValueError, PermissionError, RuntimeError, OSError) as exc:
            st.error("Method suggestions unavailable: " + str(exc))
    if any(term in run.question.lower() for term in ("protein", "binder", "egfr", "glp1r")):
        with st.expander("Protein-design evaluation context"):
            st.write(
                "Separate structure confidence, functional evidence, novelty and design diversity. "
                "For a conditional binder, record relevant pH conditions and species; for an agonist, "
                "record activation evidence separately from binding. Mark unavailable results UNKNOWN. "
                "Complementary tools such as backbone generation and sequence design are not automatically "
                "alternative methods."
            )
            st.markdown("[Proteinbase selection context](https://proteinbase.com/competitions/anthropic-adaptyv-2026/selection)")
    drafts = st.session_state[state_key]
    prefix = ctx + "_" + str(st.session_state[revision_key])
    count = st.number_input(
        "Number of candidate methods (0–1 allows deferral only)", min_value=0, max_value=4,
        value=len(drafts), step=1, key="method_count_" + prefix)
    records = []
    with st.form("method_evaluation_form_" + prefix):
        for i in range(int(count)):
            base = drafts[i] if i < len(drafts) else blank_candidate(f"M{i+1}")
            cid = f"M{i+1}"
            with st.expander("Candidate " + cid, expanded=True):
                name = st.text_input("Method name", value=base.get("name", ""), key=prefix + cid + "name")
                evidence_ids = st.multiselect(
                    "Reviewed source IDs", sources,
                    default=[p for p in base.get("evidence_ids", []) if p in sources],
                    key=prefix + cid + "sources")
                scope = st.text_area(
                    "Applicability: target, conditions and comparison scope",
                    value=base.get("scope", ""), key=prefix + cid + "scope")
                checks = {}
                for check in CHECKS:
                    prior = base.get("checks", {}).get(check, {})
                    st.markdown("**" + CHECK_LABELS[check] + "**")
                    state = st.selectbox(
                        "Documentation status", CHECK_STATES,
                        index=CHECK_STATES.index(prior.get("status", "unknown")),
                        key=prefix + cid + check + "state")
                    detail = st.text_input(
                        "Finding or reason (required unless unknown)",
                        value=prior.get("detail", ""), key=prefix + cid + check + "detail")
                    reference = st.text_input(
                        "Location / reference (required if documented)",
                        value=prior.get("reference", ""), key=prefix + cid + check + "reference")
                    checks[check] = {"status": state, "detail": detail, "reference": reference}
                comparison = {}
                for criterion in CRITERIA:
                    comparison[criterion] = st.text_area(
                        CRITERION_LABELS[criterion], value=base.get("comparison", {}).get(criterion, ""),
                        key=prefix + cid + criterion)
                records.append({"candidate_id": cid, "name": name, "evidence_ids": evidence_ids,
                                "scope": scope, "checks": checks, "comparison": comparison})
        options = ["DEFER"] + [c["candidate_id"] for c in records]
        previous = (run.evaluation or {}).get("selected_candidate_id") or "DEFER"
        selected = st.selectbox(
            "Researcher decision", options,
            index=options.index(previous) if previous in options else 0,
            format_func=lambda x: "Defer: insufficient basis for comparison" if x == "DEFER" else x,
            key="decision_" + prefix)
        rationale = st.text_area(
            "Why select this method or defer? (at least 8 characters)",
            value=(run.evaluation or {}).get("rationale", ""), key="rationale_" + prefix)
        submitted = st.form_submit_button("Save method evaluation", type="primary")
    if submitted:
        try:
            saved = save_evaluation(
                run, records, selected_id=None if selected == "DEFER" else selected,
                rationale=rationale)
            st.session_state[state_key] = records
            st.success("Evaluation saved. Status: " + saved["status"])
        except (ValueError, PermissionError) as exc:
            st.error("Evaluation not saved: " + str(exc))
    if run.evaluation:
        try:
            require_evaluation(run)
            st.success("Saved comparison is current; a draft plan can be approved below.")
        except (ValueError, PermissionError) as exc:
            st.warning(str(exc))
        st.dataframe([
            {"Method": c["candidate_id"] + " · " + c["name"],
             "Reproducibility": c["reproducibility_status"],
             "Open checks": len(c["open_checks"]),
             "Scope": c["scope"],
             **{CRITERION_LABELS[k]: c["comparison"][k] for k in CRITERIA}}
            for c in run.evaluation["candidates"]
        ], hide_index=True, use_container_width=True)
        st.caption("No calibrated confidence percentage or scientifically proven winner is computed.")
        st.json(run.evaluation)
        st.download_button(
            "Download method evaluation JSON",
            data=json.dumps(run.evaluation, ensure_ascii=False, indent=2),
            file_name="frontierlab_method_evaluation.json", mime="application/json",
            key="export_eval_" + ctx)


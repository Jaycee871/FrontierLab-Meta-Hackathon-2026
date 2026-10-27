"""Run with 'streamlit run app.py'."""
from __future__ import annotations
import streamlit as st
from frontierlab.demo_data import QUESTION, QUERY
from frontierlab.quantitative import inverse_variance_heterogeneity
from frontierlab.openweight import OpenWeightClient
from frontierlab.pipeline import make_plan, run_research
from frontierlab.reporting import export_json, summary
from frontierlab.claim_benchmark import benchmark
from frontierlab.claim_verification import audit_predictions, conflict_transparency

st.set_page_config(page_title="FrontierLab | Research Intelligence", page_icon="🔬", layout="wide")
st.markdown("""
<style>
.stApp {background: #090e18; color: #e8edf8;}
.block-container {padding-top: 2rem; max-width: 1320px;}
h1,h2,h3 {letter-spacing:-0.025em;}
[data-testid="stMetric"] {background:#131e2d;padding:16px;border:1px solid #273449;border-radius:14px;}
[data-testid="stSidebar"] {background:#111b2a;}
.stAlert {border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.caption("META GLOBAL AI DEVELOPER HACKATHON 2026  /  INDIE DEVELOPER  /  PUSH THE FRONTIER")
st.title("FrontierLab  /  Research Intelligence")
st.write("An evidence-grounded scientific research workflow that **records disagreement instead of hiding it**.")

with st.sidebar:
    st.header("Engine")
    mode_label = st.radio("Evidence mode", ["Synthetic audit demonstration", "Live Europe PMC metadata (no model calls)", "Live Europe PMC + local Meta model"], index=0)
    mode = "demo" if mode_label.startswith("Synthetic") else "live"
    use_local_meta = mode_label == "Live Europe PMC + local Meta model"
    st.info("PAID META API DISABLED. Optional Meta Muse Glimmer inference is restricted to a same-host, local llama.cpp server at 127.0.0.1:8080.")
    if mode == "demo":
        st.warning("SYNTHETIC DATA. Invented publications demonstrate auditing; none are real scientific evidence.")
    elif use_local_meta:
        st.warning("Experimental real open-weight model mode. Requires an actual Muse Glimmer checkpoint served on THIS machine; charges no Meta API credits. Never expose the local server publicly.")
    else:
        st.info("Europe PMC metadata only. No model inference, no paid API requests.")
    st.caption("No autonomous wet-lab execution, clinical advice or unverified study claims.")

with st.form("research_form"):
    question = st.text_area("Scientific research question", value=QUESTION, height=85)
    query = st.text_input("Europe PMC search query", value=QUERY, disabled=(mode == "demo"))
    n = st.slider("Maximum live abstracts", 1, 10, 4, disabled=(mode == "demo"))
    run_clicked = st.form_submit_button("Run research audit", use_container_width=True, type="primary")

if run_clicked:
    with st.spinner("Retrieving evidence and applying verification gates..."):
        try:
            local_client = OpenWeightClient() if use_local_meta else None
            result = run_research(question, query, mode=mode, model_client=local_client, max_papers=n)
            st.session_state["frontier_result"] = result
        except Exception as exc:
            st.error(f"Research run failed: {type(exc).__name__}: {exc}")

result = st.session_state.get("frontier_result")
if result:
    stats = summary(result)
    a, b, c, d = st.columns(4)
    a.metric("Sources", stats["sources"])
    b.metric("Claims: passage checks / synthetic", stats["claims"])
    c.metric("Conflicts", stats["conflicts"])
    d.metric("Rejected claims", stats["rejected"])
    st.caption(f"Decision gate: **{stats['decision']}** · Model: {result.model} · Data source: {result.mode}")
    for warning in result.audit.warnings:
        st.warning(warning)
    if result.mode == "demo":
        with st.expander("Wolfram-validated heterogeneity example (FICTIONAL numbers)", expanded=False):
            stats_q = inverse_variance_heterogeneity([0.4, -0.3], [0.15, 0.1])
            st.error("SYNTHETIC: These invented effect sizes do NOT represent observed studies.")
            x, y, z = st.columns(3)
            x.metric("Pooled effect (not a conclusion)", f"{stats_q['pooled_effect']:.4f}")
            y.metric("Cochran Q", f"{stats_q['Q']:.4f}")
            z.metric("I²", f"{stats_q['I2'] * 100:.1f}%")
            st.caption("High inconsistency: do NOT force consensus. Independently checked with Wolfram Language; no online Wolfram call is made by this app.")
    if result.mode == "demo":
        with st.expander("Claim-to-passage audit benchmark (FICTIONAL · hand-labeled)", expanded=False):
            fixture_papers, fixture_cases = benchmark()
            verified = audit_predictions(fixture_papers, fixture_cases)
            st.warning("All ten examples and predictions are HAND-AUTHORED FICTION. Scores do not represent Meta/NVIDIA model accuracy, nor prove scientific validity.")
            x, y, z = st.columns(3)
            x.metric("Known source IDs", f"{verified['source_id_coverage']:.0%}")
            y.metric("Verbatim excerpt matches", f"{verified['verbatim_passage_coverage']:.0%}")
            z.metric("Synthetic gold-label agreement", f"{verified['label_accuracy_vs_independent_gold']:.0%}")
            st.caption("A quotation can exist yet be used to support a FALSE statement; genuine semantic verification needs independently annotated evidence.")
            st.json({"cases": verified["cases"], "missing_conflict_detection_example":
                     conflict_transparency([], [("SYNTHETIC:A","SYNTHETIC:B")])})
    with st.expander("1 · Evidence catalogue", expanded=True):
        for p in result.papers:
            st.markdown(f"**{p.title}**  ·  {p.paper_id}  ·  {p.year}")
            st.caption(f"{p.authors} · {p.source} · {'SYNTHETIC / NO LINK' if p.synthetic else p.url}")
            st.write(p.abstract)
            st.divider()
    with st.expander("2 · Extracted claims and citation checks", expanded=True):
        if not result.audit.verified_claims:
            st.info("No claims have passed the source-ID gate. This is not evidence that a scientific claim is false.")
        for claim in result.audit.verified_claims:
            st.markdown(f"**{claim.stance.upper()}** · {claim.paper_id} · {claim.claim_key}")
            st.write(claim.statement)
            if claim.passage_matched:
                st.caption(f"Verbatim abstract excerpt (NOT semantic verification): {claim.evidence_quote}")
            else:
                st.caption("No passage match recorded (synthetic fixture only).")
            st.caption(f"Limitations: {claim.limitation}")
        st.caption("Valid source IDs and verbatim excerpts are NOT independent scientific fact-checking or semantic entailment. Compare claims against the original article and methods.")
        if result.audit.rejected_claims:
            st.json(result.audit.rejected_claims)
    with st.expander("3 · Conflict review & skeptic", expanded=True):
        if result.audit.conflicts:
            st.error("Incompatible directions detected. Do not report consensus.")
            st.json(result.audit.conflicts)
        else:
            st.info("No machine-detected contradictions; this is not proof of agreement.")
        st.json(result.skeptic)
    with st.expander("4 · Falsifiable hypotheses", expanded=True):
        st.json(result.hypotheses)
    st.subheader("5 · Human review gate")
    approved = st.checkbox("I have reviewed the evidence, conflicts and limitations. Allow a DRAFT research plan.")
    if st.button("Generate cited plan", disabled=not approved or not result.hypotheses, type="primary"):
        try:
            planner = OpenWeightClient() if result.mode == "live" and "muse-glimmer" in result.model.lower() else None
            make_plan(result, model_client=planner, approved=approved)
            st.success("Draft created. Human scientific review is still required.")
        except Exception as exc:
            st.error(f"Planning blocked: {exc}")
    if result.plan:
        st.json(result.plan)
    with st.expander("Audit trail", expanded=False):
        st.json(result.log)
    st.download_button("Download complete provenance JSON", data=export_json(result),
                       file_name="frontierlab_audit.json", mime="application/json")
else:
    st.info("Begin with synthetic conflict fixtures or Europe PMC. Local Muse Glimmer inference is optional, requires a separately launched checkpoint, and NEVER contacts the paid Meta API.")

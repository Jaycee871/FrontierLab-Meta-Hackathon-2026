"""Run with 'streamlit run app.py'."""
from __future__ import annotations
import streamlit as st
from frontierlab.demo_data import QUESTION, QUERY
from frontierlab.quantitative import inverse_variance_heterogeneity
from frontierlab.pipeline import make_plan, run_research
from frontierlab.reporting import export_json, summary

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
    mode_label = st.radio("Evidence mode", ["Synthetic audit demonstration", "Live Europe PMC metadata (no model calls)"], index=0)
    mode = "demo" if mode_label.startswith("Synthetic") else "live"
    st.info("PAID META API DISABLED. This build makes no Meta Model API calls, even if a key exists in the environment.")
    if mode == "demo":
        st.warning("SYNTHETIC DATA. Invented publications demonstrate auditing; none are real scientific evidence.")
    else:
        st.info("Only Europe PMC metadata is fetched. Model-based claims and hypotheses remain disabled until a safe open-weight backend is tested.")
    st.caption("No autonomous wet-lab execution, clinical advice or unverified study claims.")

with st.form("research_form"):
    question = st.text_area("Scientific research question", value=QUESTION, height=85)
    query = st.text_input("Europe PMC search query", value=QUERY, disabled=(mode == "demo"))
    n = st.slider("Maximum live abstracts", 1, 10, 4, disabled=(mode == "demo"))
    run_clicked = st.form_submit_button("Run research audit", use_container_width=True, type="primary")

if run_clicked:
    with st.spinner("Retrieving evidence and applying verification gates..."):
        try:
            result = run_research(question, query, mode=mode, model_client=None, max_papers=n)
            st.session_state["frontier_result"] = result
        except Exception as exc:
            st.error(f"Research run failed: {type(exc).__name__}: {exc}")

result = st.session_state.get("frontier_result")
if result:
    stats = summary(result)
    a, b, c, d = st.columns(4)
    a.metric("Sources", stats["sources"])
    b.metric("Source-ID-checked claims", stats["claims"])
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
            st.caption(f"Limitations: {claim.limitation}")
        st.caption("Source-ID verification is NOT independent fact checking. Confirm each statement in the original paper.")
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
            make_plan(result, model_client=None, approved=approved)
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
    st.info("Begin with the labeled fictional conflict fixture, or retrieve Europe PMC metadata. A Meta open-weight inference backend is being evaluated; this build makes NO paid Meta API calls.")

"""Run with 'streamlit run app.py'."""
from __future__ import annotations
import base64
import json
from pathlib import Path
import streamlit as st
from frontierlab.demo_data import QUESTION, QUERY
from frontierlab.quantitative import inverse_variance_heterogeneity
from frontierlab.openweight import OpenWeightClient
from frontierlab.pipeline import make_plan, run_research, continue_after_review
from frontierlab.review import review_packet, save_review
from frontierlab.reporting import export_json, summary
from frontierlab.process_metrics import process_metrics
from frontierlab.trajectory_graph import build_trajectory_graph, summarize as trajectory_summary, to_json as trajectory_json
from frontierlab.interventions import record_human_event
from frontierlab.claim_benchmark import benchmark
from frontierlab.claim_verification import audit_predictions, conflict_transparency
from frontierlab.integrity_trials import suite_report
from frontierlab.evaluation_ui import render_evaluation
from frontierlab.evaluation import require_evaluation
from frontierlab.evidence_graph import (approve_plan_step, refresh_evidence_graph, step_gate,
                                        summarize as graph_summary, to_json as graph_json, to_svg as graph_svg)
from frontierlab.literature_pilot import load_dataset, reviewer_packet
from frontierlab.recorded_gate_ablation import run_recorded_pilot
from frontierlab.research_backend import NvidiaResearchClient, research_enabled, remaining_calls
from frontierlab.version import __version__



ASSETS = Path(__file__).resolve().parent / "docs" / "assets"
_icon_path = ASSETS / "flatland-sphere-icon.png"
st.set_page_config(page_title="FrontierLab | Research Intelligence",
                   page_icon=str(_icon_path) if _icon_path.exists() else "◯", layout="wide")

# Presentation only: black-and-white "Flatland book plate" styling (see docs/assets/).
SERIF = "Georgia, 'Times New Roman', Times, serif"
st.markdown(f"""
<style>
:root {{ --fl-ink: #F2F2F2; --fl-soft: #CFCFCF; --fl-bg: #1E1E1E; --fl-bg2: #262626; --fl-line: rgba(242,242,242,0.55); }}
.stApp {{ background: var(--fl-bg); color: var(--fl-ink); }}
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp summary p, [data-testid="stMetricValue"],
[data-testid="stMetricLabel"], [data-testid="stCaptionContainer"] {{ font-family: {SERIF}; }}
[data-testid="stDecoration"] {{ display: none; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2rem; max-width: 1320px; }}
h1 {{ font-weight: 400; font-style: italic; letter-spacing: 0.02em; }}
h2, h3 {{ font-weight: 400; letter-spacing: 0.04em; }}
[data-testid="stCaptionContainer"], .stCaption {{ color: var(--fl-soft); }}
hr {{ border-color: var(--fl-line) !important; }}
a {{ color: var(--fl-ink) !important; text-decoration: underline; text-underline-offset: 3px; }}
/* hero banner and section bands */
.fl-hero {{ display: block; width: 100%; height: auto; border: 1px solid var(--fl-line); margin: 0 0 1.2rem 0; }}
.fl-band {{ display: flex; align-items: center; gap: 0.6rem; margin: 1.6rem 0 0.4rem 0;
           padding-bottom: 0.35rem; border-bottom: 1px solid var(--fl-line);
           font-variant: small-caps; letter-spacing: 0.22em; font-size: 0.85rem; color: var(--fl-ink); }}
.fl-band svg {{ flex: none; }}
/* outlined white boxes instead of filled cards */
[data-testid="stMetric"] {{ background: transparent; padding: 14px 16px; border: 1px solid var(--fl-ink); border-radius: 0; }}
[data-testid="stSidebar"] {{ background: #1A1A1A; border-right: 1px solid var(--fl-line); }}
[data-testid="stExpander"] details {{ border: 1px solid var(--fl-line); border-radius: 0; background: transparent; }}
[data-testid="stForm"] {{ border: 1px solid var(--fl-line); border-radius: 0; }}
[data-testid="stAlert"] > div, [data-testid="stAlertContainer"] {{ background: transparent !important;
           border: 1px solid var(--fl-line); border-radius: 0; color: var(--fl-ink); }}
[data-testid="stAlertContentWarning"], [data-testid="stAlertContentError"],
[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentInfo"] {{ color: var(--fl-ink); }}
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) > div {{ border-style: dashed; border-color: var(--fl-ink); }}
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) > div {{ border: 2px solid var(--fl-ink); }}
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) > div {{ border-left: 4px double var(--fl-ink); }}
[data-testid="stTextAreaRootElement"], [data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"],
[data-testid="stSelectbox"] .react-aria-ComboBox > [role="group"], [data-testid="stMultiSelect"] .react-aria-ComboBox > [role="group"] {{
           background: transparent !important; border: 1px solid var(--fl-line) !important; border-radius: 0 !important; }}
[data-testid="stTextAreaRootElement"]:focus-within, [data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stNumberInputContainer"]:focus-within {{ border-color: var(--fl-ink) !important; }}
[data-testid="stMultiSelectTagsContainer"] span[data-tag] {{
           background: transparent !important; color: var(--fl-ink) !important; border: 1px solid var(--fl-ink); border-radius: 0; }}
[data-testid="stMultiSelectTagsContainer"] span[data-tag] * {{ color: var(--fl-ink) !important; fill: var(--fl-ink); }}
/* checkboxes: outlined square, white tick on charcoal (never white-on-white) */
[data-testid="stCheckbox"] label > div:first-of-type {{ background: transparent !important; border: 1px solid var(--fl-ink) !important; border-radius: 0 !important; }}
[data-testid="stCheckbox"] label > div:first-of-type svg polyline {{ stroke: var(--fl-ink) !important; }}
[data-testid="stCode"] pre, [data-testid="stJson"] {{ border: 1px solid var(--fl-line); border-radius: 0; }}
/* JSON viewer: monochrome (keys soft, values ink) */
[data-testid="stJson"] span {{ color: var(--fl-ink) !important; }}
[data-testid="stJson"] .object-key, [data-testid="stJson"] .object-key span {{ color: var(--fl-soft) !important; }}
[data-testid="stJson"] .object-key-val {{ border-left-color: rgba(242,242,242,0.25) !important; }}
[data-testid="stJson"] svg {{ color: var(--fl-ink) !important; fill: var(--fl-ink) !important; }}
/* buttons: outlined white boxes that invert on hover */
.stApp :is([data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primaryFormSubmit"], [data-testid="stBaseButton-secondaryFormSubmit"]) {{ background: transparent; color: var(--fl-ink); border: 1px solid var(--fl-ink);
           border-radius: 0; box-shadow: none; letter-spacing: 0.06em; }}
.stApp :is([data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primaryFormSubmit"], [data-testid="stBaseButton-secondaryFormSubmit"]) p {{ color: inherit; }}
.stApp :is([data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primaryFormSubmit"], [data-testid="stBaseButton-secondaryFormSubmit"]):hover:not(:disabled), .stApp :is([data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primaryFormSubmit"], [data-testid="stBaseButton-secondaryFormSubmit"]):focus-visible {{
           background: var(--fl-ink); color: var(--fl-bg); border-color: var(--fl-ink); }}
.stApp :is([data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primaryFormSubmit"], [data-testid="stBaseButton-secondaryFormSubmit"]):disabled {{ background: transparent; color: var(--fl-soft); border: 1px dashed var(--fl-line); opacity: 0.7; }}
</style>
""", unsafe_allow_html=True)

_ICON = 'width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F2F2F2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
BAND_ICONS = {
    "point": f'<svg {_ICON}><line x1="2" y1="18" x2="22" y2="18" stroke-width="1"/><circle cx="12" cy="11" r="3" fill="#F2F2F2" stroke="none"/></svg>',
    "sphere": f'<svg {_ICON}><circle cx="12" cy="12" r="10" stroke-width="1.5"/><ellipse cx="12" cy="12" rx="10" ry="3" stroke-width="0.8" stroke-dasharray="2 2"/><ellipse cx="12" cy="12" rx="3.6" ry="10" stroke-width="0.8"/></svg>',
    "cube": f'<svg {_ICON}><rect x="3" y="8" width="13" height="13" stroke-width="1.4"/><polyline points="3,8 8,3 21,3 16,8" stroke-width="1.4"/><polyline points="21,3 21,16 16,21" stroke-width="1.4"/></svg>',
}


def band(label: str, icon: str) -> None:
    """Small-caps section band, as on the README architecture plate."""
    st.markdown(f'<div class="fl-band">{BAND_ICONS[icon]}<span>{label}</span></div>', unsafe_allow_html=True)


_hero_path = ASSETS / "flatland-hero.svg"
if _hero_path.exists():
    _hero = base64.b64encode(_hero_path.read_bytes()).decode("ascii")
    st.markdown(f'<img class="fl-hero" src="data:image/svg+xml;base64,{_hero}" '
                'alt="FrontierLab: From Flatland to Spaceland. Role shapes rise from a flat plane toward a sphere.">',
                unsafe_allow_html=True)

st.caption("META GLOBAL AI DEVELOPER HACKATHON 2026  /  INDIE DEVELOPER  /  PUSH THE FRONTIER")
st.title("FrontierLab  /  Research Intelligence")
st.caption(f"Research → Evidence → Hypothesis → Evaluation → Planning · v{__version__}")
deployment_path = Path(__file__).resolve().parent / "deployment.json"
if deployment_path.exists():
    deployment = json.loads(deployment_path.read_text(encoding="utf-8"))
    st.caption(f"Deployed source: {deployment['source_sha'][:12]} · {deployment['version']} · {deployment['space_id']}")
st.write("An evidence-grounded scientific research workflow that **records disagreement instead of hiding it**.")

nim_authorized = False
with st.sidebar:
    st.header("Engine")
    mode_label = st.radio("Evidence mode", ["Synthetic audit demonstration", "Live Europe PMC metadata (no model calls)", "Live Europe PMC + local Meta model", "Live Europe PMC + Meta via NVIDIA"], index=0)
    mode = "demo" if mode_label.startswith("Synthetic") else "live"
    use_local_meta = mode_label == "Live Europe PMC + local Meta model"
    use_nim = mode_label == "Live Europe PMC + Meta via NVIDIA"
    st.info("Paid Meta Platforms API is disabled. Choose a local model or the optional NVIDIA-hosted Meta backend.")
    if mode == "demo":
        st.warning("SYNTHETIC DATA. Invented publications demonstrate auditing; none are real scientific evidence.")
    elif use_nim:
        if not research_enabled():
            st.warning("NVIDIA research inference has not been enabled by the app owner.")
        nim_authorized = st.checkbox(
            "Allow this research question and retrieved abstracts to be sent to NVIDIA for Meta inference",
            value=False, disabled=not research_enabled(), key="nim_research_consent")
        st.caption(f"Remaining shared model calls in this server process: {remaining_calls()} / 8. Failed requests consume the allowance; no automatic retries.")
    elif use_local_meta:
        st.warning("Experimental real open-weight model mode. Requires an actual Muse Glimmer checkpoint served on THIS machine; charges no Meta API credits. Never expose the local server publicly.")
    else:
        st.info("Europe PMC metadata only. No model inference, no paid API requests.")
    st.caption("No autonomous wet-lab execution, clinical advice or unverified study claims.")

band("I · Flatland — question and evidence", "point")
st.subheader("1 · Research question")
with st.form("research_form"):
    question = st.text_area("Scientific research question", value=QUESTION, height=85)
    query = st.text_input("Europe PMC search query", value=QUERY, disabled=(mode == "demo"))
    n = st.slider("Maximum live abstracts", 1, 2 if use_nim else 10,
                  2 if use_nim else 4, disabled=(mode == "demo"))
    run_clicked = st.form_submit_button("Run research audit", use_container_width=True,
                                       type="primary", disabled=use_nim and not nim_authorized)

if run_clicked:
    with st.spinner("Retrieving evidence and applying verification gates..."):
        try:
            st.session_state.pop("frontier_result", None)
            st.session_state.pop("frontier_model_client", None)
            client = (NvidiaResearchClient(authorized=nim_authorized) if use_nim else
                      OpenWeightClient() if use_local_meta else None)
            st.session_state["frontier_model_client"] = client
            result = run_research(question, query, mode=mode, model_client=client, max_papers=n)
            st.session_state["frontier_result"] = result
        except Exception as exc:
            st.error(f"Research run failed: {type(exc).__name__}: {exc}")

with st.expander("Published-literature pilot · 12 cases awaiting researcher annotation"):
    pilot = load_dataset()
    st.caption("Four published antibody-engineering papers; short abstract excerpts only. Draft reference labels are excluded from the review download. Researcher annotations remain pending.")
    recorded_path = Path(__file__).resolve().parent / "docs/runs/meta_nim_pilot_20261028.json"
    if recorded_path.exists():
        recorded = json.loads(recorded_path.read_text(encoding="utf-8"))["receipt"]
        st.info("RECORDED REAL META RUN · 12 structured predictions, 8 matched quotations and 4 insufficient-evidence responses. This panel makes no live model call; accuracy awaits researcher review.")
        st.download_button("Download recorded Meta predictions", data=json.dumps(recorded["predictions"], ensure_ascii=False, indent=2), file_name="meta_pilot_predictions_20261028.json", mime="application/json")
        ablation = run_recorded_pilot()
        with st.expander("Gate ablation · recorded 12-case Glimmer batch", expanded=False):
            st.warning(
                "POST-GENERATION REPLAY ONLY. The recorded model prompt already requested evidence quotes, "
                "so this does not isolate the causal effect of quote-grounded prompting. "
                "The 12-case human review is still pending; no accuracy is reported."
            )
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Raw decisive", ablation["arm_a_fixed_model_outputs"]["decisive"])
            g2.metric("Quote-gated decisive", ablation["arm_b_source_quote_post_gate"]["decisive"])
            g3.metric("New abstentions from gate", ablation["effects"]["quote_gate_new_abstentions"])
            g4.metric("Human reviews pending", ablation["arm_c_source_quote_plus_human_review"]["pending_review"])
            st.caption(
                f"Recorded Meta call: {ablation['recorded_model_call']['usage']['total_tokens']} tokens · "
                f"{ablation['recorded_model_call']['elapsed_seconds']:.3f}s · "
                f"new model calls for this replay: {ablation['new_model_calls']}."
            )
            st.caption(
                "In this clean recorded batch, all eight decisive outputs already had valid anchored quotes, "
                "so the post-processing source/quote gate introduced zero additional abstentions. "
                "That is a result, not evidence that the gate is unnecessary."
            )
            st.download_button(
                "Download recorded gate-ablation JSON",
                data=json.dumps(ablation, ensure_ascii=False, indent=2, sort_keys=True),
                file_name="gate_ablation_recorded_20261028.json",
                mime="application/json",
            )
    st.download_button(
        "Download literature reviewer packet", data=json.dumps(reviewer_packet(pilot), ensure_ascii=False, indent=2),
        file_name="frontierlab_real_excerpt_review.json", mime="application/json")
    st.markdown("[Pilot protocol and source attribution](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/blob/main/docs/REAL_LITERATURE_PILOT.md)")
    review_path = Path(__file__).resolve().parent / "docs/runs/nim_claim_review_completed_20261028.json"
    if review_path.exists():
        reviewed = json.loads(review_path.read_text(encoding="utf-8"))
        st.success("RECORDED CORE RUN · Jaycee871 reviewed both claims as SUPPORTED on October 28, 2026. These judgments cover two claims, separate from the 12-case pilot.")
        st.caption("The original extraction receipt is preserved. No hypothesis, method selection or plan was generated by recording this review; this panel makes no model call.")
        st.dataframe([{"Case": c["case_id"], "Claim": c["claim"], "Human judgment": c["review_label"], "Reason": c["review_note"]} for c in reviewed["cases"]], hide_index=True, use_container_width=True)
        st.download_button("Download completed core-workflow human review", data=review_path.read_text(encoding="utf-8"), file_name=review_path.name, mime="application/json")

result = st.session_state.get("frontier_result")
if result:
    active_client = st.session_state.get("frontier_model_client")
    if result.backend == "nvidia-nim" and (not use_nim or not nim_authorized):
        active_client = None
    stats = summary(result)
    a, b, c, d = st.columns(4)
    a.metric("Sources", stats["sources"])
    b.metric("Claims: passage checks / synthetic", stats["claims"])
    c.metric("Conflicts", stats["conflicts"])
    d.metric("Rejected claims", stats["rejected"])
    st.caption(f"Decision gate: **{stats['decision']}** · Backend: {result.backend} · Model: {result.model} · Data source: {result.mode}")
    if result.inference:
        with st.expander("Model request receipts"):
            st.json(result.inference)
    with st.expander("Process metrics · audit only", expanded=False):
        pm = process_metrics(result)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Completed stages", f"{pm['stage_completion']['completed']} / 5")
        m2.metric("SCR", f"{pm['scr'] * 100:.0f}%")
        m3.metric("Observed human actions", pm["human_interventions"]["observed_total"])
        aerr = pm["nim"]["aerr"]
        m4.metric("AERR", "N/A" if aerr is None else f"{aerr * 100:.0f}%")
        st.caption(
            "Process metrics describe workflow activity, not model accuracy. "
            "Observed human actions use recorded intervention events when available; legacy runs use a conservative fallback. Identity is not verified."
        )
        taxonomy = pm["error_taxonomy"]
        e1, e2, e3 = st.columns(3)
        e1.metric("Governance / evidence blocks", taxonomy["governance_or_evidence_blocks"])
        e2.metric("Runtime failures", taxonomy["runtime_failures"])
        e3.metric("Scientific tensions", taxonomy["scientific_tensions"])
        if pm["nim"]["applicable"]:
            st.caption(
                f"NIM calls: {pm['nim']['attempted_calls']} · "
                f"tokens: {pm['nim']['total_tokens']} · "
                f"recorded model time: {pm['nim']['elapsed_seconds']:.3f}s"
            )
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
    if result.mode == "demo":
        with st.expander("Research Failure Lab · 12 fictional failure injections", expanded=False):
            lab = suite_report()
            st.warning(
                "OFFLINE HAND-AUTHORED POLICY TESTS ONLY: no actual Meta inference, "
                "real biomedical model call, independent scientific assessment or "
                "human learning experiment has occurred."
            )
            u, v, w = st.columns(3)
            u.metric("Policy test cases", lab["total"])
            v.metric("Expected guard decisions matched", lab["matched_expectations"])
            w.metric("Real model calls", lab["model_calls"])
            st.caption(
                "Cross-stage scenarios: stale source snapshots, unsupported excerpts, "
                "unverified BioNeMo origin, train/test peptide leakage, and human teachability evidence. "
                "A quote that exists can still be semantically wrong."
            )
            st.json(lab["cases"])
            st.download_button(
                "Download fictional failure-injection results",
                data=json.dumps(lab, indent=2, ensure_ascii=False),
                file_name="frontierlab_v011_failure_lab_fictional.json",
                mime="application/json",
            )
    with st.expander("2 · Evidence catalogue", expanded=True):
        for p in result.papers:
            st.markdown(f"**{p.title}**  ·  {p.paper_id}  ·  {p.year}")
            st.caption(f"{p.authors} · {p.source} · {'SYNTHETIC / NO LINK' if p.synthetic else p.url}")
            st.write(p.abstract)
            st.divider()
    with st.expander("Evidence claims and citation checks", expanded=True):
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
    with st.expander("Evidence conflicts and skeptical review", expanded=True):
        if result.audit.conflicts:
            st.error("Incompatible directions detected. Do not report consensus.")
            st.json(result.audit.conflicts)
        else:
            st.info("No machine-detected contradictions; this is not proof of agreement.")
        st.json(result.skeptic)
    if result.mode == "live" and result.audit.verified_claims:
        band("II · The Sphere — human claim review", "sphere")
        with st.expander("Researcher claim review · required before synthesis", expanded=True):
            st.warning(
                "Verbatim excerpt matching does NOT establish entailment. "
                "Choose a human judgment for each claim. PENDING items and fewer than two "
                "supported distinct sources block research hypothesis generation."
            )
            packet=review_packet(result)
            previous={c["case_id"]:c for c in (result.review or {}).get("cases", [])}
            st.download_button(
                "Download source-bound blank reviewer packet",
                data=json.dumps(packet, ensure_ascii=False, indent=2),
                file_name="frontierlab_human_review_blank.json", mime="application/json"
            )
            decisions=[]
            with st.form("claim_reviewer_form"):
                for case in packet["cases"]:
                    cid=case["case_id"]
                    earlier=previous.get(cid, {})
                    st.markdown(f"**{cid} · {case['paper_title']}**")
                    st.caption(f"Source ID: {case['paper_id']} · {case['source']}")
                    st.write("**Model claim:** " + case["claim"])
                    st.code(case["evidence_quote"], language="text")
                    st.caption("The quotation exists in the source abstract. Its meaning has NOT been verified.")
                    opts=["PENDING","SUPPORTED","CONTRADICTED","INSUFFICIENT"]
                    default=earlier.get("review_label","PENDING")
                    verdict=st.selectbox(
                        "Reviewer judgment", opts,
                        index=opts.index(default) if default in opts else 0,
                        key=f"claim_review_{cid}"
                    )
                    note=st.text_input(
                        "Reason for verdict (required if contradicted or insufficient)",
                        value=earlier.get("review_note",""), key=f"claim_reason_{cid}"
                    )
                    decisions.append({"case_id":cid,"review_label":verdict,"review_note":note})
                    st.divider()
                submitted=st.form_submit_button("Save human review judgments", type="primary")
            if submitted:
                try:
                    save_review(result, decisions)
                    st.session_state["frontier_result"]=result
                    st.success("Human review saved in this session; download JSON to preserve it.")
                except ValueError as exc:
                    st.error(f"Review validation failed: {exc}")
            if result.review:
                st.json({"review_status":result.review.get("status"),
                         "review_statistics":result.review.get("review_stats"),
                         "independent_expert_adjudication_verified":False})
                st.download_button(
                    "Download human-annotated review JSON",
                    data=json.dumps(result.review,ensure_ascii=False,indent=2),
                    file_name="frontierlab_human_review_annotated.json",
                    mime="application/json"
                )
                if result.review.get("status")=="READY_FOR_HUMAN_GATED_SYNTHESIS":
                    st.info("Review complete. Hypothesis synthesis requires an actually connected, available model and further human scrutiny.")
                    if st.button("Resume model synthesis after human review", type="secondary",
                                 disabled=active_client is None):
                        try:
                            continue_after_review(result, model_client=active_client)
                            st.session_state["frontier_result"]=result
                            st.success("Provisional human-gated draft created; scientific validation is still needed.")
                        except (ValueError, PermissionError, RuntimeError) as exc:
                            st.error(f"Synthesis remains blocked: {type(exc).__name__}: {exc}")
    band("III · Spaceland — hypothesis, evaluation and plan", "cube")
    with st.expander("3 · Falsifiable hypotheses", expanded=True):
        st.json(result.hypotheses)
    render_evaluation(result, model_client=active_client)
    st.subheader("5 · Research plan approval gate")
    try:
        require_evaluation(result)
        evaluation_ready = True
    except (ValueError, PermissionError):
        evaluation_ready = False
    approved = st.checkbox("I have reviewed the evidence, conflicts and limitations. Allow a DRAFT research plan.")
    if st.button("Generate cited plan", disabled=not approved or not result.hypotheses or not evaluation_ready or (result.mode == "live" and active_client is None), type="primary"):
        try:
            planner = active_client if result.mode == "live" else None
            make_plan(result, model_client=planner, approved=approved)
            st.success("Draft created. Human scientific review is still required.")
        except Exception as exc:
            st.error(f"Planning blocked: {exc}")
    if result.plan:
        st.json(result.plan)
    # Rebuilt from the current run on every render, so reviews, hypotheses and plans stay in sync.
    graph = refresh_evidence_graph(result)
    g_stats = graph_summary(graph)
    with st.expander("6 · Evidence graph · provenance of every plan step", expanded=False):
        st.caption("EXTRACTED: passage located in the cited abstract and source IDs checked (not semantic entailment). "
                   "INFERRED: model stance without an anchored quote. AMBIGUOUS: conflicting labels. "
                   "Only all-EXTRACTED paths to a paper count as evidence.")
        e_count = g_stats["edges_by_provenance"]
        x, y, z = st.columns(3)
        x.metric("EXTRACTED edges", e_count["EXTRACTED"])
        y.metric("INFERRED edges (not evidence)", e_count["INFERRED"])
        z.metric("AMBIGUOUS edges (not evidence)", e_count["AMBIGUOUS"])
        drawing = graph_svg(graph)
        if drawing:
            st.markdown('<img class="fl-hero" alt="Evidence provenance graph: solid lines EXTRACTED, dashed INFERRED, dotted AMBIGUOUS" '
                        f'src="data:image/svg+xml;base64,{base64.b64encode(drawing.encode("utf-8")).decode("ascii")}">',
                        unsafe_allow_html=True)
        else:
            st.caption("Graph too large to draw legibly; use the tables and graph.json below.")
        if g_stats["surfaced_for_review"]:
            st.warning("Surfaced for researcher review. These links are NOT counted as evidence.")
            st.dataframe([{"Provenance": e["provenance"], "From": e["source"], "Relation": e["relation"],
                           "To": e["target"], "Why": e["reason"]} for e in g_stats["surfaced_for_review"]],
                         hide_index=True, use_container_width=True)
        steps = [n for n in graph["nodes"] if n["type"] == "plan_step"]
        if steps:
            gates = {n["id"]: step_gate(graph, n["id"]) for n in steps}
            st.dataframe([{"Step": n["index"], "Text": n["text"],
                           "Path gate": "ALL EXTRACTED" if gates[n["id"]]["approvable"] else "BLOCKED",
                           "Researcher approval": "RECORDED" if n["id"] in graph["approvals"] else "—",
                           "Reasons": "; ".join(gates[n["id"]]["reasons"])} for n in steps],
                         hide_index=True, use_container_width=True)
            eligible = [n["id"] for n in steps if gates[n["id"]]["approvable"] and n["id"] not in graph["approvals"]]
            if eligible:
                with st.form("plan_step_approval_form"):
                    chosen = st.selectbox("Plan step with an all-EXTRACTED evidence path", eligible,
                                          format_func=lambda sid: next(f"Step {n['index']}" for n in steps if n["id"] == sid))
                    reviewer = st.text_input("Reviewer")
                    rationale = st.text_input("Approval rationale (8+ characters)")
                    if st.form_submit_button("Record researcher approval of this step", type="secondary"):
                        try:
                            approve_plan_step(graph, chosen, reviewer=reviewer, note=rationale)
                            record_human_event(result, "PLAN_STEP_APPROVED", chosen, actor_label=reviewer, note=rationale)
                            st.session_state["frontier_result"] = result
                            st.success("Step approval recorded in this session; it remains a draft, not a validated protocol.")
                        except (ValueError, PermissionError) as exc:
                            st.error(f"Step approval blocked: {exc}")
            else:
                st.info("No plan step is currently eligible for approval under the EXTRACTED-only path rule.")
        else:
            st.caption("No plan steps yet. Steps appear here once a draft plan exists.")
        st.download_button("Download graph.json", data=graph_json(graph),
                           file_name="graph.json", mime="application/json")
    trajectory = build_trajectory_graph(result)
    t_stats = trajectory_summary(trajectory)
    with st.expander("7 · Trajectory audit graph · process trace", expanded=False):
        st.caption(
            "Audit-only process graph. It records model calls, human interventions, "
            "method evaluation, rejected claims and process signals. It never participates "
            "in the scientific evidence gate."
        )
        t1, t2, t3, t4 = st.columns(4)
        t1.metric("Model calls", t_stats["model_calls"])
        t2.metric("Human events", t_stats["human_events"])
        t3.metric("Rejected claims", t_stats["rejected_claims"])
        t4.metric("Process signals", t_stats["process_signals"])
        st.dataframe(
            [{"Node type": key, "Count": value} for key, value in t_stats["nodes_by_type"].items()],
            hide_index=True, use_container_width=True
        )
        st.download_button(
            "Download trajectory.json",
            data=trajectory_json(trajectory),
            file_name="trajectory.json",
            mime="application/json",
        )
    with st.expander("Audit trail", expanded=False):
        st.json(result.log)
    st.download_button("Download complete provenance JSON", data=export_json(result),
                       file_name="frontierlab_audit.json", mime="application/json")
else:
    st.info("Begin with the synthetic audit or Europe PMC. Model-backed research requires a configured local server or an explicitly enabled NVIDIA backend.")


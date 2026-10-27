"""FrontierLab's explicit, traceable role-by-role scientific workflow."""
from __future__ import annotations
from datetime import datetime, timezone
from .audit import enforce_citations, risk_decision, validate_claims
from .demo_data import DEMO_CLAIMS, DEMO_PAPERS, QUESTION
from .evidence import retrieve_papers
from .models import Run


def log_step(log: list[dict], role: str, state: str, note: str):
    log.append({"time_utc": datetime.now(timezone.utc).isoformat(), "role": role, "status": state, "note": note})


def run_research(question: str, query: str, *, mode: str, model_client=None, max_papers: int = 5,
                 retrieve=retrieve_papers) -> Run:
    if not question.strip():
        raise ValueError("Please enter a research question")
    if mode not in {"demo", "live"}:
        raise ValueError("Unsupported run mode")
    log: list[dict] = []
    if mode == "demo":
        papers = DEMO_PAPERS[:]
        candidate_claims = DEMO_CLAIMS[:]
        log_step(log, "Retriever", "SIMULATED", "Loaded invented, clearly labeled fixture; not retrieved literature")
        log_step(log, "Extraction Agent", "SIMULATED", "Loaded hand-authored fictional claims")
        audit = validate_claims(papers, candidate_claims)
        hypothesis = [{"text": "Assay conditions may alter observed acidic-pH binding differences.",
                       "evidence_ids": ["SYNTHETIC:A", "SYNTHETIC:B", "SYNTHETIC:C"],
                       "rationale": "Invented disagreement illustrates a falsifiable test design."}]
        skeptic = {"decision": "REVIEW_CONFLICT", "explanation": "Invented examples disagree and cannot be treated as evidence.",
                   "uncertainties": ["Assay-condition confounding", "No external validation"]}
        log_step(log, "Evidence Auditor", "PASS_WITH_WARNING", "Three synthetic IDs validated; one conflict flagged")
        log_step(log, "Skeptic / Hypothesis", "SIMULATED", "Deterministic demonstration, no AI inference")
        return Run(question=question, mode=mode, model="None (fixture)", papers=papers,
                   audit=audit, hypotheses=hypothesis, skeptic=skeptic, log=log)

    papers = retrieve(query, max_papers)
    log_step(log, "Retriever", "COMPLETE", f"Retrieved {len(papers)} indexed publications with abstracts")
    if not papers:
        audit = validate_claims([], [])
        audit.warnings.append("No matching abstracts. Refine your search before making research claims.")
        return Run(question, mode, "None", papers, audit, [], {"decision": "NO_EVIDENCE"}, log)
    if model_client is None:
        audit = validate_claims(papers, [])
        audit.warnings.append("No local model attached: sources retrieved, AI extraction and synthesis have NOT run.")
        log_step(log, "Meta AI", "BLOCKED", "No explicit local model was selected")
        return Run(question, mode, "None (not connected)", papers, audit, [],
                   {"decision": "MODEL_NOT_CONNECTED"}, log)

    extracted = []
    for paper in papers:
        packet = {"question": question, "paper": {"paper_id": paper.paper_id,
                  "title": paper.title, "year": paper.year, "abstract": paper.abstract}}
        res = model_client.json("Evidence Extraction Agent", (
            "Extract up to 2 scientific claims about the research question from this abstract. "
            "Output JSON: {\"claims\": [{\"paper_id\": exact source paper ID, "
            "\"claim_key\": concise normalized comparison target, "
            "\"stance\": one of supports|contradicts|mixed|inconclusive, "
            "\"statement\": carefully scoped interpretation, \"limitation\": caveat}]}. "
            "Use only abstract-level evidence; don't infer results not given. "
            "If this abstract is irrelevant or uninformative, use an empty claims array."
        ), packet)
        for c in res.get("claims", []):
            if isinstance(c, dict):
                if c.get("paper_id") != paper.paper_id:
                    c["paper_id"] = "REJECTED_UNKNOWN_ID"
                extracted.append(c)
    audit = validate_claims(papers, extracted)
    log_step(log, "Extraction Agent", "COMPLETE", f"{len(extracted)} proposed claims; {len(audit.rejected_claims)} rejected for invalid metadata")
    if risk_decision(audit) == "INSUFFICIENT_EVIDENCE":
        audit.warnings.append("Fewer than two distinct sources with validated source IDs; hypothesis generation stopped.")
        log_step(log, "Audit Gate", "BLOCKED", "Insufficient distinct sourced claims for synthesis")
        return Run(question, mode, model_client.model, papers, audit, [],
                   {"decision": "INSUFFICIENT_EVIDENCE"}, log)

    claims = [c.__dict__ for c in audit.verified_claims]
    evidence_ids = [p.paper_id for p in papers]
    skeptic = model_client.json("Adversarial Skeptic Agent", (
        "Analyze sources ONLY. Output JSON: {\"explanation\": string, "
        "\"uncertainties\": [strings], \"recommended_checks\": [strings]}. "
        "Seek rival explanations, confounding, and methodological differences. "
        "Do not force consensus."
    ), {"question": question, "claims": claims, "deterministic_conflicts": audit.conflicts})
    skeptic["decision"] = risk_decision(audit)
    log_step(log, "Skeptic Agent", "COMPLETE", f"Rule-based disposition: {skeptic['decision']}")

    proposed = model_client.json("Hypothesis Agent", (
        "Output JSON: {\"hypotheses\": [{\"text\": falsifiable hypothesis, "
        "\"evidence_ids\": [only provided source IDs], \"rationale\": brief limitations-aware rationale}]}. "
        "Maximum 2; no medical advice or unwarranted claims."
    ), {"question": question, "claims": claims, "valid_evidence_ids": evidence_ids,
        "conflicts": audit.conflicts, "skeptic": skeptic})
    hypotheses, rejected = enforce_citations(proposed.get("hypotheses", []), papers)
    if rejected:
        audit.warnings.append(f"Rejected {len(rejected)} hypotheses with unsupported source IDs.")
    log_step(log, "Hypothesis Agent", "COMPLETE", f"{len(hypotheses)} citation-linked hypotheses survived audit")
    return Run(question, mode, model_client.model, papers, audit, hypotheses, skeptic, log)


def make_plan(run: Run, *, model_client=None, approved: bool = False) -> Run:
    if not approved:
        raise PermissionError("Human approval required before planning")
    if not run.hypotheses:
        raise ValueError("Cannot plan without a supported hypothesis")
    if risk_decision(run.audit) == "INSUFFICIENT_EVIDENCE":
        raise ValueError("Cannot plan from fewer than two sources with valid evidence claims")
    if run.mode == "demo":
        run.plan = {
            "status": "SYNTHETIC_TEST_ONLY",
            "objective": "Determine whether buffer/assay variation explains fictional apparent pH effects.",
            "steps": [
                "Preregister a factorial design across pH, ionic strength and assay conditions.",
                "Use independent replicates and negative controls.",
                "Quantify uncertainty and stop if controls fail."
            ],
            "evidence_ids": ["SYNTHETIC:A", "SYNTHETIC:B", "SYNTHETIC:C"],
            "limitations": "Entire scenario is fictional and not a validated scientific protocol.",
        }
        log_step(run.log, "Planning Agent", "SIMULATED", "Human-approved mock plan; no AI / laboratory execution")
        return run
    if model_client is None:
        raise ValueError("A valid local model is required to generate a live plan")
    proposed = model_client.json("Scientific Planning Agent", (
        "Write ONE cautious, research-review plan. Return JSON: "
        "{\"objective\": string, \"steps\": [strings], "
        "\"evidence_ids\": [existing source IDs], \"limitations\": string}. "
        "Focus on controls, replication, measurement, falsification and human oversight. "
        "This is a conceptual research proposal, not medical advice or automated laboratory instructions."
    ), {"question": run.question, "hypotheses": run.hypotheses,
        "claims": [c.__dict__ for c in run.audit.verified_claims],
        "conflicts": run.audit.conflicts, "skeptic": run.skeptic,
        "allowed_evidence_ids": [p.paper_id for p in run.papers]})
    accepted, rejected = enforce_citations([proposed], run.papers)
    if rejected or not accepted:
        log_step(run.log, "Citation Gate", "BLOCKED", "Planning Agent used missing/invalid source IDs")
        raise ValueError("Plan references invalid citations; generation stopped")
    run.plan = {"status": "DRAFT_FOR_RESEARCHER_REVIEW", **proposed}
    log_step(run.log, "Planning Agent", "COMPLETE", "Cited plan drafted following human approval")
    return run

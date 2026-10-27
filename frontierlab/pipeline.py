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
            "\"statement\": carefully scoped interpretation, \"limitation\": caveat, " 
            "\"evidence_quote\": exact 24-to-500-character contiguous excerpt from THIS abstract}]}. "
            "The evidence_quote MUST appear verbatim within the given abstract. "
            "If no supporting or contradicting passage can be quoted, output no claim. "
            "Quote presence does NOT establish logical support; researcher review is mandatory. "
            "Use only abstract-level evidence; don't infer results not given. "
            "If this abstract is irrelevant or uninformative, use an empty claims array."
        ), packet)
        for c in res.get("claims", []):
            if isinstance(c, dict):
                if c.get("paper_id") != paper.paper_id:
                    c["paper_id"] = "REJECTED_UNKNOWN_ID"
                extracted.append(c)
    audit = validate_claims(papers, extracted, require_quote=True)
    log_step(log, "Extraction Agent", "COMPLETE", f"{len(extracted)} proposed; {len(audit.verified_claims)} abstract-quoted; {len(audit.rejected_claims)} rejected")
    if risk_decision(audit) == "INSUFFICIENT_EVIDENCE":
        audit.warnings.append("Fewer than two distinct sources with validated source IDs; hypothesis generation stopped.")
        log_step(log, "Audit Gate", "BLOCKED", "Insufficient distinct sourced claims for synthesis")
        return Run(question, mode, model_client.model, papers, audit, [],
                   {"decision": "INSUFFICIENT_EVIDENCE"}, log)

    audit.warnings.append(
        "Live quoted claims are PROVISIONAL until reviewed individually by a researcher. "
        "No skeptical synthesis or hypotheses have been generated."
    )
    log_step(log, "Human Claim Review", "BLOCKED", "Claim-level semantic judgments pending researcher annotations")
    return Run(question, mode, model_client.model, papers, audit, [],
               {"decision":"HUMAN_CLAIM_REVIEW_REQUIRED",
                "explanation":"Quote presence has been checked; entailment has not."}, log)


def continue_after_review(run: Run, *, model_client=None) -> Run:
    """Resume skeptical synthesis only after explicit human claim-level review."""
    from .review import approved_claims, review_packet
    if run.mode != "live" or model_client is None:
        raise PermissionError("Live human-gated synthesis requires a connected model")
    if not run.review or run.review.get("dataset_id") != review_packet(run)["dataset_id"]:
        raise PermissionError("No valid source-bound human review packet")
    if run.review.get("status") != "READY_FOR_HUMAN_GATED_SYNTHESIS":
        raise PermissionError("Complete all claim reviews and support at least two distinct sources")
    approved = approved_claims(run)
    evidence_ids = sorted({c.paper_id for c in approved})
    if len(evidence_ids) < 2:
        raise PermissionError("Two independently reviewed supporting sources required")
    papers = [p for p in run.papers if p.paper_id in evidence_ids]
    claims = [c.__dict__ for c in approved]
    audit = run.audit
    question = run.question
    log = run.log
    # The raw model's detected tensions remain in run.audit.conflicts.
    # A separate reviewed-only contrast cannot be inferred when assay conditions vary.
    reviewer_conflicts = [
        record for record in audit.conflicts
        if any(pid in evidence_ids for pid in record.get("supports", []))
        and any(pid in evidence_ids for pid in record.get("contradicts", []))
    ]
    skeptic = model_client.json("Adversarial Skeptic Agent", (
        "Analyze sources ONLY. Output JSON: {\"explanation\": string, "
        "\"uncertainties\": [strings], \"recommended_checks\": [strings]}. "
        "Seek rival explanations, confounding, and methodological differences. "
        "Do not force consensus."
    ), {"question": question, "claims": claims, "deterministic_conflicts": reviewer_conflicts})
    skeptic["decision"] = "REVIEW_CONFLICT" if reviewer_conflicts else "HUMAN_REVIEWED_DRAFT"
    skeptic["human_review_summary"] = run.review["review_stats"]
    log_step(log, "Skeptic Agent", "COMPLETE", f"Rule-based disposition: {skeptic['decision']}")

    proposed = model_client.json("Hypothesis Agent", (
        "Output JSON: {\"hypotheses\": [{\"text\": falsifiable hypothesis, "
        "\"evidence_ids\": [only provided source IDs], \"rationale\": brief limitations-aware rationale}]}. "
        "Maximum 2; no medical advice or unwarranted claims."
    ), {"question": question, "claims": claims, "valid_evidence_ids": evidence_ids,
        "conflicts": reviewer_conflicts, "skeptic": skeptic})
    hypotheses, rejected = enforce_citations(proposed.get("hypotheses", []), papers)
    if rejected:
        audit.warnings.append(f"Rejected {len(rejected)} hypotheses with unsupported source IDs.")
    log_step(log, "Hypothesis Agent", "COMPLETE", f"{len(hypotheses)} citation-linked hypotheses survived audit")
    run.hypotheses = hypotheses
    run.evaluation = None
    run.plan = None
    run.skeptic = skeptic
    run.model = model_client.model
    return run


def make_plan(run: Run, *, model_client=None, approved: bool = False) -> Run:
    if not approved:
        raise PermissionError("Human approval required before planning")
    if not run.hypotheses:
        raise ValueError("Cannot plan without a supported hypothesis")
    if run.mode == "live":
        from .review import approved_claims, review_packet
        if not run.review or run.review.get("dataset_id") != review_packet(run)["dataset_id"]:
            raise PermissionError("Live planning requires a valid human-reviewed evidence packet")
        if run.review.get("status") != "READY_FOR_HUMAN_GATED_SYNTHESIS" or (
            len({c.paper_id for c in approved_claims(run)}) < 2
        ):
            raise PermissionError("Live planning requires two human-reviewed supporting sources")
    if risk_decision(run.audit) == "INSUFFICIENT_EVIDENCE":
        raise ValueError("Cannot plan from fewer than two sources with valid evidence claims")
    from copy import deepcopy
    from .evaluation import require_evaluation, selected_method
    evaluation = require_evaluation(run)
    method = selected_method(evaluation)
    evaluation_context = {
        "evaluation_id": evaluation["evaluation_id"],
        "selected_candidate_id": method["candidate_id"],
        "selected_method": deepcopy(method),
        "selection_rationale": evaluation["rationale"],
        "uncertainty": deepcopy(evaluation["uncertainty"]),
    }
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
            "controls": ["Fictional negative and matched-condition controls."],
            "metrics": ["Prespecified condition-dependent response and its uncertainty."],
            "replication": ["Propose independent repeats before interpreting effects."],
            "falsification": ["Defer if matched conditions remove the apparent pH effect."],
            **evaluation_context,
        }
        log_step(run.log, "Planning Agent", "SIMULATED", "Human-approved mock plan; no AI / laboratory execution")
        return run
    if model_client is None:
        raise ValueError("A valid local model is required to generate a live plan")
    permitted_claims = approved_claims(run)
    permitted_ids = {c.paper_id for c in permitted_claims}
    permitted_papers = [p for p in run.papers if p.paper_id in permitted_ids]
    proposed = model_client.json("Scientific Planning Agent", (
        "Write ONE cautious, research-review plan. Return JSON: "
        "{\"objective\": string, \"steps\": [strings], "
        "\"controls\": [strings], \"metrics\": [strings], "
        "\"replication\": [strings], \"falsification\": [strings], "
        "\"evidence_ids\": [existing source IDs], \"limitations\": string}. "
        "Focus on controls, replication, measurement, falsification and human oversight. "
        "Use the researcher-selected method and explicitly address its unresolved checks. "
        "Cite every source attached to that method. Do not report proposed tests as executed. "
        "This is a conceptual research proposal, not medical advice or automated laboratory instructions."
    ), {"question": run.question, "hypotheses": run.hypotheses,
        "claims": [c.__dict__ for c in permitted_claims],
        "conflicts": run.audit.conflicts, "skeptic": run.skeptic,
        "allowed_evidence_ids": sorted(permitted_ids),
        "method_evaluation": evaluation_context})
    accepted, rejected = enforce_citations([proposed], permitted_papers)
    if rejected or not accepted:
        log_step(run.log, "Citation Gate", "BLOCKED", "Planning Agent used missing/invalid source IDs")
        raise ValueError("Plan references invalid citations; generation stopped")
    for key in ("objective", "limitations"):
        if not isinstance(proposed.get(key), str) or not proposed[key].strip():
            raise ValueError("Plan requires nonempty " + key)
    for key in ("steps", "controls", "metrics", "replication", "falsification"):
        values = proposed.get(key)
        if not isinstance(values, list) or not values or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError("Plan requires nonempty " + key)
    if not set(method["evidence_ids"]).issubset(proposed["evidence_ids"]):
        raise ValueError("Plan must cite the selected method's sources")
    # The model cannot overwrite the reviewed decision, constraints or draft status.
    run.plan = {key: proposed[key] for key in (
        "objective", "steps", "controls", "metrics", "replication",
        "falsification", "evidence_ids", "limitations")}
    run.plan.update(evaluation_context)
    run.plan["status"] = "DRAFT_FOR_RESEARCHER_REVIEW"
    log_step(run.log, "Planning Agent", "COMPLETE", "Cited plan drafted following human approval")
    return run


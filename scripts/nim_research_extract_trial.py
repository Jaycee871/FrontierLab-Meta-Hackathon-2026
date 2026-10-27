"""Bounded real NIM extraction through FrontierLab; always stops before human review."""
from datetime import datetime, timezone
import json
import os
from frontierlab.literature_pilot import load_dataset
from frontierlab.models import Paper
from frontierlab.pipeline import run_research
from frontierlab.research_backend import CallBudget, NvidiaResearchClient
from frontierlab.review import review_packet
from scripts.smoke_nvidia_muse import _run_context

QUESTION = (
    "What do these two published excerpts establish about pH-dependent antibody "
    "engineering, and what remains unknown about generalization?"
)
SOURCE_IDS = ("PMC4314675", "PMC6927761")


def source_papers():
    data = load_dataset()
    sources = {s["source_id"]: s for s in data["sources"]}
    return [Paper(
        paper_id=sid, title=sources[sid]["title"],
        year=str(sources[sid]["publication_year_records"][0]["year"]),
        authors=", ".join(sources[sid]["authors"]), abstract=sources[sid]["source_text"],
        url=sources[sid]["url"], doi=sources[sid]["doi"],
        source="Europe PMC published abstract excerpt (frozen snapshot)", synthetic=False,
    ) for sid in SOURCE_IDS]


def main():
    if (os.getenv("FRONTIERLAB_EXTRACTION_TRIAL") != "YES" or
            os.getenv("FRONTIERLAB_NIM_RESEARCH") != "YES"):
        print("EXTRACTION_TRIAL_NOT_AUTHORIZED: no call made")
        return 2
    started = datetime.now(timezone.utc).isoformat()
    client = NvidiaResearchClient(authorized=True, budget=CallBudget(2))
    base = {"schema_version": 1, "started_at_utc": started, **_run_context(),
            "scope": "Two frozen published abstract excerpts; not a new live literature search.",
            "maximum_model_calls": 2, "human_review_automated": False,
            "hypothesis_or_plan_generation_authorized": False,
            "scientific_accuracy": None, "paid_meta_platforms_api_used": False}
    try:
        run = run_research(QUESTION, "frozen excerpts", mode="live",
                          model_client=client, max_papers=2,
                          retrieve=lambda q,n: source_papers()[:n])
    except (RuntimeError, ValueError, PermissionError) as exc:
        base.update(status="REAL_RESEARCH_STEP_FAILED", error_type=type(exc).__name__,
                    inference=client.provenance)
        print(json.dumps(base, ensure_ascii=False, indent=2))
        return 1
    packet = review_packet(run) if run.audit.verified_claims else None
    assert not run.hypotheses and run.evaluation is None and run.plan is None
    base.update(
        status="REAL_RESEARCH_PAUSED_FOR_HUMAN_REVIEW" if (
            run.skeptic.get("decision") == "HUMAN_CLAIM_REVIEW_REQUIRED"
        ) else "REAL_RESEARCH_STOPPED_WITH_INSUFFICIENT_EVIDENCE",
        run=run.as_dict(), reviewer_packet=packet,
    )
    print(json.dumps(base, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


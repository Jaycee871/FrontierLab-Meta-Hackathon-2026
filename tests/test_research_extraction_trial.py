"""Offline verification of the bounded real-excerpt extraction runner."""
import json
from scripts import nim_research_extract_trial as trial
from frontierlab.research_backend import NvidiaResearchClient


def test_extraction_sources_are_frozen_published_excerpts():
    papers = trial.source_papers()
    assert len(papers) == 2 and all(not p.synthetic for p in papers)
    assert all(p.doi and len(p.abstract) >= 24 for p in papers)
    assert all("frozen snapshot" in p.source for p in papers)


def test_extraction_runner_needs_its_own_opt_in(monkeypatch, capsys):
    monkeypatch.delenv("FRONTIERLAB_EXTRACTION_TRIAL", raising=False)
    assert trial.main() == 2
    assert "NOT_AUTHORIZED" in capsys.readouterr().out


def test_mock_runner_stops_before_human_review_and_never_calls_synthesis(monkeypatch, capsys):
    calls = []
    class Response:
        status_code = 200
        def __init__(self, body): self.body = body
        def json(self): return self.body
    class Session:
        def post(self, url, **kwargs):
            prompt = kwargs["json"]["messages"][-1]["content"]
            role = prompt.split("\nROLE: ",1)[1].split("\nTASK:",1)[0]
            calls.append(role)
            assert role == "Evidence Extraction Agent"
            data = json.loads(prompt.split("\nSOURCE DATA:\n",1)[1])
            answer = {"claims": [{"paper_id": data["paper"]["paper_id"],
                "claim_key": "test-only", "stance": "supports",
                "statement": "Artificial claim, awaiting review.",
                "limitation": "Mock model output only.",
                "evidence_quote": data["paper"]["abstract"]}]}
            return Response({"model":"meta/muse-glimmer-30b",
                "choices":[{"message":{"content":json.dumps(answer)},"finish_reason":"stop"}]})
    monkeypatch.setenv("FRONTIERLAB_EXTRACTION_TRIAL", "YES")
    monkeypatch.setenv("FRONTIERLAB_NIM_RESEARCH", "YES")
    monkeypatch.setattr(trial, "NvidiaResearchClient",
        lambda **kwargs: NvidiaResearchClient(**kwargs, key="DUMMY", session=Session()))
    assert trial.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert calls == ["Evidence Extraction Agent"] * 2
    assert result["status"] == "REAL_RESEARCH_PAUSED_FOR_HUMAN_REVIEW"
    assert result["run"]["backend"] == "nvidia-nim"
    assert not result["run"]["hypotheses"] and result["run"]["plan"] is None
    assert all(c["review_label"] == "PENDING" for c in result["reviewer_packet"]["cases"])


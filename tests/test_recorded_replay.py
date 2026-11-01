"""Recorded real M2 replay: numbers are recomputed from docs/runs, with zero model calls."""
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests
from streamlit.testing.v1 import AppTest

import frontierlab
from frontierlab import openweight, pipeline, research_backend
from frontierlab.evidence import EPMC_ENDPOINT, europepmc_error_message
from frontierlab.evidence_graph import build_evidence_graph
from frontierlab.planning_readiness import build_planning_readiness
from frontierlab.recorded_replay import RUNS, build_recorded_replay, load_recorded_m2_run
from frontierlab.traceability import trace_coverage
from frontierlab.version import __version__
from scripts.planning_readiness_recorded import run as recorded_packet
from scripts.trace_coverage_recorded import run as recorded_trace

APP = Path(__file__).resolve().parents[1] / "app.py"
REPLAY_EXPANDER = "Start here · Replay recorded real M2 case (no model call)"


@pytest.fixture
def no_model_or_network(monkeypatch):
    """Any model client construction or HTTP request fails the test."""
    def forbidden(*args, **kwargs):
        raise AssertionError("replay must not create a model client or make a network request")
    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    monkeypatch.setattr(research_backend, "NvidiaResearchClient", forbidden)
    monkeypatch.setattr(openweight, "OpenWeightClient", forbidden)
    monkeypatch.delenv("FRONTIERLAB_NIM_RESEARCH", raising=False)


def test_replay_numbers_are_computed_from_recorded_files(no_model_or_network):
    replay = build_recorded_replay()
    trace = replay["trace_coverage"]
    assert trace["source_trace_coverage"] == 1.0
    assert trace["strict_extracted_coverage"] == 0.5
    assert trace["material_artifacts"] == 4
    assert trace["source_traceable_artifacts"] == 4 and trace["strict_extracted_artifacts"] == 2
    assert replay["readiness_summary"]["required_obligations"] == 9
    assert replay["readiness_summary"]["planning_approved"] is False
    assert replay["new_model_calls"] == 0
    assert replay["recorded_date_taipei"] == "2026-10-28"
    assert replay["operating_status"]["traceability"]["strict_extracted_coverage"] == 0.5
    blocked = [a for a in trace["artifacts"] if not a["strict_extracted"]]
    assert {p for a in blocked for p in a["papers"]} == {"PMC4314675"}
    assert all(e["provenance"] == "AMBIGUOUS" and "inconclusive" in e["reason"]
               for a in blocked for e in a["blocking_edges"])


def test_replay_matches_recorded_scripts_and_independent_recomputation():
    replay = build_recorded_replay()
    script_trace = recorded_trace()["trace_coverage"]
    assert replay["trace_coverage"]["source_trace_coverage"] == script_trace["source_trace_coverage"]
    assert replay["trace_coverage"]["strict_extracted_coverage"] == script_trace["strict_extracted_coverage"]
    packet = recorded_packet()
    assert len(packet["planning_obligations"]) == replay["readiness_summary"]["required_obligations"]
    run, _ = load_recorded_m2_run()
    assert trace_coverage(build_evidence_graph(run))["strict_extracted_coverage"] == 0.5
    assert len(build_planning_readiness(run)["planning_obligations"]) == 9


def test_recorded_call_counts_come_from_receipts_not_from_replay():
    calls = build_recorded_replay()["recorded_calls"]
    assert calls["extraction_calls"] == 2 and calls["continuation_calls"] == 2
    assert calls["continuation_roles"] == ["Adversarial Skeptic Agent", "Hypothesis Agent"]
    assert calls["recorded_date_taipei"] == "2026-10-28"


def test_tampered_recorded_file_fails_closed(tmp_path):
    for path in RUNS.glob("*.json"):
        shutil.copy(path, tmp_path / path.name)
    target = tmp_path / "nim_research_extraction_20261028.json"
    data = json.loads(target.read_text(encoding="utf-8"))
    data["receipt"]["run"]["audit"]["verified_claims"][0]["stance"] = "supports"
    target.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(PermissionError):
        build_recorded_replay(tmp_path)


def test_selection_that_authorizes_planning_is_rejected(tmp_path):
    for path in RUNS.glob("*.json"):
        shutil.copy(path, tmp_path / path.name)
    target = tmp_path / "researcher_method_selection_20261028.json"
    data = json.loads(target.read_text(encoding="utf-8"))
    data["planning_approved"] = True
    target.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(PermissionError):
        build_recorded_replay(tmp_path)


def test_app_first_view_renders_replay_with_computed_numbers(no_model_or_network):
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    replay = next(e for e in app.expander if e.label == REPLAY_EXPANDER)
    metrics = {m.label: m.value for m in replay.metric}
    assert metrics["Source trace coverage"] == "100%"
    assert metrics["Strict EXTRACTED coverage"] == "50%"
    assert metrics["Planning obligations"] == "9"
    assert metrics["Model calls in this replay"] == "0"
    assert metrics["Required planning obligations"] == "9"
    assert metrics["Planning approved"] == "NO"
    banner = " ".join(i.value for i in replay.info)
    assert "RECORDED REAL RUN · REPLAY ONLY" in banner and "2026-10-28" in banner
    assert "makes 0 model calls" in banner
    assert [t.label for t in replay.tabs][:4] == [
        "Research Operating Interface", "Planning readiness", "Evidence graph", "Trajectory"]
    assert any("Judge path" in m.value for m in app.markdown)
    with pytest.raises(KeyError):
        app.session_state["frontier_result"]


def test_synthetic_run_shows_one_banner_and_fail_closed_coverage_caption(no_model_or_network):
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    next(b for b in app.button if b.label == "Run research audit").click().run()
    assert not app.exception
    assert app.session_state["frontier_result"].mode == "demo"
    banners = [w.value for w in app.warning if w.value.startswith("SYNTHETIC / FICTIONAL MODE")]
    assert len(banners) == 1
    assert not any(w.value.startswith("SYNTHETIC FIXTURE") for w in app.warning)
    note = next(c.value for c in app.caption if "by design (fail-closed)" in c.value)
    assert "strict EXTRACTED coverage is 0%" in note
    assert "100% source / 50% strict" in note


def test_unavailable_modes_are_labelled_on_the_public_space(monkeypatch):
    monkeypatch.delenv("FRONTIERLAB_NIM_RESEARCH", raising=False)
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    radio = app.radio[0]
    assert radio.value == "Synthetic audit demonstration"
    assert any("Meta via NVIDIA · not available on the public Space" in o for o in radio.options)


def _http_error(url, status):
    response = requests.Response()
    response.status_code = status
    response.url = url
    return requests.HTTPError(f"{status} Server Error for url: {url}", response=response)


def test_europepmc_errors_get_friendly_message():
    message = europepmc_error_message(_http_error(EPMC_ENDPOINT + "?query=x", 503))
    assert "temporarily unavailable (HTTP 503)" in message and "no model was called" in message
    assert "HTTP 429" in europepmc_error_message(_http_error(EPMC_ENDPOINT + "?q", 429))
    assert europepmc_error_message(_http_error("http://127.0.0.1:8080/v1/models", 503)) is None
    assert europepmc_error_message(ValueError("x")) is None
    timeout = requests.Timeout("slow", request=SimpleNamespace(url=EPMC_ENDPOINT + "?q"))
    assert "did not respond in time" in europepmc_error_message(timeout)


def test_app_shows_friendly_europepmc_error(monkeypatch):
    monkeypatch.delenv("FRONTIERLAB_NIM_RESEARCH", raising=False)
    def failing(*args, **kwargs):
        raise _http_error(EPMC_ENDPOINT + "?query=x", 502)
    monkeypatch.setattr(pipeline, "run_research", failing)
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.radio[0].set_value("Live Europe PMC metadata (no model calls)").run()
    next(b for b in app.button if b.label == "Run research audit").click().run()
    assert not app.exception
    errors = [e.value for e in app.error]
    assert any("Europe PMC is temporarily unavailable (HTTP 502)" in e for e in errors)
    assert not any("HTTPError" in e for e in errors)


def test_package_version_matches_central_version():
    assert frontierlab.__version__ == __version__

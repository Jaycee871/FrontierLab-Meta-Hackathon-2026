"""Deployment packaging and recorded researcher judgments; no external calls."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest
from frontierlab.models import Paper, Claim, Audit, Run
from frontierlab.review import review_packet, save_review
from scripts.deploy_hf_space import deploy, SPACE_ID

ROOT = Path(__file__).resolve().parents[1]


def test_saved_user_review_matches_original_sources_and_ready_gate():
    original = json.loads((ROOT / "docs/runs/nim_research_extraction_20261028.json").read_text())
    data = original["receipt"]["run"]
    papers = [Paper(**p) for p in data["papers"]]
    audit = Audit(**{**data["audit"], "verified_claims": [Claim(**c) for c in data["audit"]["verified_claims"]]})
    run = Run(**{**data, "papers": papers, "audit": audit})
    saved = json.loads((ROOT / "docs/runs/nim_claim_review_completed_20261028.json").read_text())
    assert saved["dataset_id"] == review_packet(run)["dataset_id"]
    replayed = save_review(run, saved["cases"])
    assert replayed["cases"] == saved["cases"]
    assert replayed["status"] == "READY_FOR_HUMAN_GATED_SYNTHESIS"
    assert replayed["review_stats"]["supported_distinct_sources"] == 2
    assert all(c["review_note"] and c["review_label"] == "SUPPORTED" for c in saved["cases"])
    assert not run.hypotheses and run.plan is None


class Api:
    def __init__(self, hardware="cpu-basic"):
        self.hardware = hardware
        self.commits = []
    def whoami(self): return {"name": "Jaycee766"}
    def space_info(self, repo):
        assert repo == SPACE_ID
        return SimpleNamespace(id=repo, private=False, sdk="docker", sha="old-space")
    def get_space_runtime(self, repo):
        return SimpleNamespace(hardware=self.hardware, requested_hardware=self.hardware)
    def create_commit(self, **kwargs):
        self.commits.append(kwargs)
        return SimpleNamespace(oid="new-space")


def test_snapshot_allowlist_revision_and_no_secret_or_hardware_mutations():
    api = Api()
    receipt = deploy(api, lambda **kw: kw, root=ROOT, source_sha="a" * 40)
    commit = api.commits[0]
    assert commit["parent_commit"] == "old-space"
    files = {o["path_in_repo"]: o["path_or_fileobj"] for o in commit["operations"]}
    metadata = json.loads(files["deployment.json"])
    assert metadata["source_sha"] == "a" * 40
    assert "docs/runs/nim_claim_review_completed_20261028.json" in files
    assert {".streamlit/config.toml", "docs/assets/flatland-hero.svg",
            "docs/assets/flatland-sphere-icon.png"} <= set(files)
    assert b"COPY --chown=user:user .streamlit/" in files["Dockerfile"]
    assert {"LICENSE", "NOTICE"} <= set(files)
    assert files["LICENSE"] == (ROOT / "LICENSE").read_bytes()
    assert files["NOTICE"] == (ROOT / "NOTICE").read_bytes()
    assert b"Llama 3.1 is licensed under the Llama 3.1 Community License" in files["NOTICE"]
    assert b"COPY --chown=user:user app.py deployment.json LICENSE NOTICE ./" in files["Dockerfile"]
    assert {"LICENSE", "NOTICE"} <= set(metadata["file_sha256"])
    assert all(not p.startswith((".github/", ".git/", "scripts/", "tests/")) for p in files)
    assert all("secret" not in p.lower() and ".env" not in p for p in files)
    assert b"git clone" not in files["Dockerfile"]
    assert receipt["nvidia_secret_transferred"] is False
    assert receipt["hardware_changed"] is False
    assert receipt["status"] == "HF_SOURCE_COMMITTED_BUILD_PENDING"


def test_deploy_refuses_paid_hardware_before_upload():
    api = Api(hardware="t4-medium")
    with pytest.raises(PermissionError, match="CPU Basic"):
        deploy(api, lambda **kw: kw, root=ROOT, source_sha="a" * 40)
    assert not api.commits


def test_ui_displays_saved_review_without_creating_model_client(monkeypatch):
    monkeypatch.delenv("FRONTIERLAB_NIM_RESEARCH", raising=False)
    app = AppTest.from_file(str(ROOT / "app.py")).run()
    assert not app.exception
    assert any("Jaycee871 reviewed both claims as SUPPORTED" in s.value for s in app.success)
    with pytest.raises(KeyError):
        app.session_state["frontier_model_client"]

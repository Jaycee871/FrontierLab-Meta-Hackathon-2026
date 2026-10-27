"""Static security regression tests for OpenCode optional project config."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read_config():
    return json.loads((ROOT/"opencode.json").read_text(encoding="utf-8"))
def test_no_tokens_or_model_providers():
    conf=read_config()
    assert "provider" not in conf
    assert "model" not in conf
    assert conf["$schema"] == "https://opencode.ai/config.json"
def test_permission_defaults_restrict_mutation():
    perm=read_config()["permission"]
    assert perm["*"]=="ask"
    assert perm["edit"]=="ask"
    assert perm["external_directory"]=="deny"
    assert perm["bash"]["*"]=="ask"
    assert perm["bash"]["git push*"]=="deny"
    assert perm["bash"]["gh secret*"]=="deny"
    assert perm["read"]["*.env"]=="deny"
def test_subagent_is_read_only():
    agent=read_config()["agent"]["frontierlab-review"]
    assert agent["mode"]=="subagent"
    for tool in ("edit","bash","webfetch","websearch","external_directory","task"):
        assert agent["permission"][tool]=="deny"

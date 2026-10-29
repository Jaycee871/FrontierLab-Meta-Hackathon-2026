from pathlib import Path


def test_central_version_matches_current_release():
    from frontierlab.version import __version__
    assert __version__ == "0.32"


def test_app_uses_central_version_not_hardcoded_legacy_label():
    app = Path("app.py").read_text(encoding="utf-8")
    assert "from frontierlab.version import __version__" in app
    assert "v0.16" not in app
    assert 'v{__version__}' in app


def test_hf_deploy_script_uses_central_version():
    script = Path("scripts/deploy_hf_space.py").read_text(encoding="utf-8")
    assert "from frontierlab.version import __version__" in script
    assert '"version": "v0.16"' not in script
    assert "Deploy FrontierLab v0.16" not in script
    assert 'f"v{__version__}"' in script

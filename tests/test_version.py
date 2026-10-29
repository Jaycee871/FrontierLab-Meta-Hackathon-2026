from pathlib import Path


def test_central_version_matches_current_release():
    from frontierlab.version import __version__
    assert __version__ == "0.32"


def test_app_uses_central_version_not_hardcoded_legacy_label():
    app = Path("app.py").read_text(encoding="utf-8")
    assert "from frontierlab.version import __version__" in app
    assert "v0.16" not in app
    assert 'v{__version__}' in app

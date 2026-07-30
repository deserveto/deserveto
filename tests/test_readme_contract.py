from pathlib import Path

README_PATH = Path("README.md")


def test_readme_is_full_animation_takeover() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    assert './assets/bad-apple-lua.gif' in text
    assert 'width="100%"' in text
    for legacy in (
        "## About Me",
        "## Featured Projects",
        "## Technology Stack",
        "## Contributions",
        "## Contact",
        "./avi-ascii.svg",
        "./info-card.svg",
    ):
        assert legacy not in text


def test_readme_has_accessible_alt_text() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    assert 'alt="Bad Apple rendered in a Lua-style terminal"' in text

from pathlib import Path
README_PATH = Path("README.md")


def test_readme_contains_required_sections_and_assets() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    for required in (
        "Fikri Tri Wibowo", "Information Technology Student", "## About Me",
        "## Featured Projects", "## Technology Stack", "## Contributions",
        "## Contact", "./avi-ascii.svg", "./info-card.svg", "./contrib-heatmap.svg",
    ):
        assert required in text


def test_readme_contains_approved_links() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    for url in (
        "https://github.com/deserveto",
        "https://github.com/deserveto/vulnscan-toolkit",
        "https://github.com/deserveto/ZipLift",
        "https://www.linkedin.com/in/fikri-tri-wibowo-446034296/",
        "https://www.instagram.com/fikritw_/",
    ):
        assert url in text


def test_readme_contains_no_unverified_project_link_or_template_copy() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    for forbidden in ("YOUR_NAME", "YOURHANDLE", "yoursite.com", "Avi Vashishta", "PhishGNN-EEF](", "Azure VM Portfolio]("):
        assert forbidden not in text

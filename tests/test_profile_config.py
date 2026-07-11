from scripts import profile_config as config


def test_approved_profile_content_is_exact() -> None:
    assert config.PROFILE_HOST == "deserveto"
    assert config.PROFILE_NAME == "Fikri Tri Wibowo"
    assert config.HEADLINE == (
        "Information Technology Student · Cybersecurity · AI/ML · "
        "Software Development"
    )
    assert config.CONTACT_LINKS == {
        "GitHub": "https://github.com/deserveto",
        "LinkedIn": (
            "https://www.linkedin.com/in/"
            "fikri-tri-wibowo-446034296/"
        ),
        "Instagram": "https://www.instagram.com/fikritw_/",
    }


def test_featured_projects_cover_the_approved_four_items() -> None:
    names = [project["name"] for project in config.FEATURED_PROJECTS]
    assert names == [
        "PhishGNN-EEF",
        "VulnScan Toolkit",
        "ZipLift",
        "Azure VM Portfolio",
    ]
    assert config.FEATURED_PROJECTS[0]["url"] is None
    assert config.FEATURED_PROJECTS[1]["url"] == (
        "https://github.com/deserveto/vulnscan-toolkit"
    )
    assert config.FEATURED_PROJECTS[2]["url"] == (
        "https://github.com/deserveto/ZipLift"
    )
    assert config.FEATURED_PROJECTS[3]["url"] is None


def test_configuration_contains_no_template_identity() -> None:
    rendered = repr(
        (
            config.PROFILE_NAME,
            config.HEADLINE,
            config.CONTACT_LINKS,
            config.INFO_CARD_ROWS,
            config.FEATURED_PROJECTS,
            config.STACK_GROUPS,
        )
    )
    for forbidden in ("YOUR_", "Avi Vashishta", "avi@github", "you@github"):
        assert forbidden not in rendered

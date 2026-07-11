"""Approved, user-reviewed content for the GitHub profile."""

from typing import Final

PROFILE_HOST: Final[str] = "deserveto"
PROFILE_NAME: Final[str] = "Fikri Tri Wibowo"
HEADLINE: Final[str] = (
    "Information Technology Student · Cybersecurity · AI/ML · "
    "Software Development"
)
ABOUT: Final[str] = (
    "I am an Information Technology student at Telkom University with a "
    "strong interest in cybersecurity, artificial intelligence, networking, "
    "cloud infrastructure, and software development. I enjoy building "
    "practical systems, exploring security problems, and applying machine "
    "learning to real-world challenges."
)

CONTACT_LINKS: Final[dict[str, str]] = {
    "GitHub": "https://github.com/deserveto",
    "LinkedIn": (
        "https://www.linkedin.com/in/"
        "fikri-tri-wibowo-446034296/"
    ),
    "Instagram": "https://www.instagram.com/fikritw_/",
}

INFO_CARD_ROWS: Final[tuple[tuple[str, ...], ...]] = (
    ("host",),
    ("kv", "Role", "Information Technology Student"),
    ("kv", "Focus", "Cybersecurity · AI / ML"),
    ("kv", "Study", "Telkom University"),
    ("gap",),
    ("sec", "Core Stack"),
    ("kv", "Code", "Python · TypeScript · PHP"),
    ("kv", "ML", "PyTorch · PyG · scikit-learn"),
    ("kv", "Web", "Laravel · Next.js · Tailwind"),
    ("kv", "Cloud", "Azure · GCP · Linux"),
    ("gap",),
    ("sec", "Highlights"),
    ("bul", "Phishing detection research with GNN"),
    ("bul", "Security, networking, and cloud projects"),
)

FEATURED_PROJECTS: Final[tuple[dict[str, str | None], ...]] = (
    {
        "name": "PhishGNN-EEF",
        "description": (
            "Research on phishing website detection using Graph Neural "
            "Networks with enhanced edge features on hyperlink graphs."
        ),
        "url": None,
        "label": "Research project",
    },
    {
        "name": "VulnScan Toolkit",
        "description": (
            "A command-line vulnerability scanner that combines Nmap "
            "service discovery, NSE checks, CVE correlation, and "
            "minimalist HTML reporting."
        ),
        "url": "https://github.com/deserveto/vulnscan-toolkit",
        "label": "Repository",
    },
    {
        "name": "ZipLift",
        "description": (
            "A cross-platform archive manager built with Tauri, Rust, "
            "React, and TypeScript for creating, browsing, and extracting "
            "common archive formats."
        ),
        "url": "https://github.com/deserveto/ZipLift",
        "label": "Repository",
    },
    {
        "name": "Azure VM Portfolio",
        "description": (
            "A portfolio deployment on an Ubuntu virtual machine using "
            "Apache, PHP, Git, and firewall configuration."
        ),
        "url": None,
        "label": "Infrastructure project",
    },
)

STACK_GROUPS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    ("Languages", ("Python", "JavaScript", "TypeScript", "PHP", "Java", "C++")),
    (
        "AI / ML",
        ("PyTorch", "PyTorch Geometric", "Graph Neural Networks", "scikit-learn"),
    ),
    ("Web", ("Laravel", "Next.js", "HTML", "CSS", "Tailwind CSS")),
    ("Cloud and infrastructure", ("Azure", "Google Cloud", "Linux", "Apache")),
    (
        "Security and networking",
        (
            "Vulnerability assessment",
            "Phishing detection",
            "Wireshark",
            "Packet Tracer",
        ),
    ),
    ("Tools", ("Git", "GitHub", "Docker", "VS Code")),
)

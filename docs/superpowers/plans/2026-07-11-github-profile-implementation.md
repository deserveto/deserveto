# GitHub Profile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a minimal professional GitHub profile README for `deserveto/deserveto` with an animated ASCII portrait, a matching information card, four featured projects, a grouped technology stack, contact links, and a daily refreshed animated contribution graph.

**Architecture:** Static profile content and generated SVG assets live in the profile repository. Small Python modules handle contribution scraping, statistics, SVG rendering, and portrait conversion; each renderer exposes pure functions so output can be tested without network access. A narrowly scoped GitHub Actions workflow refreshes only `data/contributions.json` and `contrib-heatmap.svg`.

**Tech Stack:** Python 3.11+, Pillow, Requests 2.32.4+, Beautiful Soup 4, pytest, SVG/XML, Markdown, GitHub Actions.

## Global Constraints

- Repository: `deserveto/deserveto`, default branch `main`, public visibility.
- Profile name: `Fikri Tri Wibowo`.
- Headline: `Information Technology Student · Cybersecurity · AI/ML · Software Development`.
- Visual direction: minimal professional, neutral grayscale, clean spacing, subtle borders, no rainbow or glitch effects.
- Animation is limited to the ASCII portrait reveal and contribution-graph reveal.
- Original portrait files and intermediate processed images must never be committed.
- LinkedIn URL: `https://www.linkedin.com/in/fikri-tri-wibowo-446034296/`.
- Instagram URL: `https://www.instagram.com/fikritw_/`.
- Featured work: PhishGNN-EEF, VulnScan Toolkit, ZipLift, and Azure VM Portfolio.
- Projects without a verified public URL remain visible without a fake link.
- The workflow may request only `contents: write`.
- Use `requests>=2.32.4,<3`.
- The workflow fetches only public GitHub contribution data.
- Generated SVGs must contain no JavaScript, remote images, event-handler attributes, or `foreignObject`.
- The original uploaded photo remains outside the repository.
- Every task is implemented test-first and committed separately.

---

## File Structure

```text
README.md
avi-ascii.svg
info-card.svg
contrib-heatmap.svg
.gitignore
pyproject.toml
requirements-dev.txt

scripts/
  __init__.py
  profile_config.py
  fetch_contributions.py
  render_heatmap_svg.py
  make_ascii_svg.py
  make_info_card.py
  requirements.txt
  requirements-local.txt
  verify_profile.py

data/
  contributions.json

tests/
  test_profile_config.py
  test_fetch_contributions.py
  test_render_heatmap_svg.py
  test_make_info_card.py
  test_make_ascii_svg.py
  test_readme_contract.py
  test_workflow_contract.py
  test_verify_profile.py

.github/workflows/
  update-profile-art.yml

docs/superpowers/specs/
  2026-07-11-github-profile-design.md

docs/superpowers/plans/
  2026-07-11-github-profile-implementation.md
```

### Responsibility Map

- `scripts/profile_config.py`: approved identity, contact, project, stack, and information-card content.
- `scripts/fetch_contributions.py`: fetch public GitHub HTML, parse contribution days, calculate statistics, write JSON.
- `scripts/render_heatmap_svg.py`: validate contribution JSON and create a safe monochrome animated heatmap.
- `scripts/make_ascii_svg.py`: convert a preprocessed grayscale portrait into an animated monochrome ASCII SVG.
- `scripts/make_info_card.py`: render approved profile facts into a matching animated information card.
- `scripts/verify_profile.py`: enforce repository privacy, SVG safety, required files, and README-link rules.
- `README.md`: final profile presentation using repository-relative asset paths.
- `.github/workflows/update-profile-art.yml`: daily and manual contribution refresh.
- `tests/`: deterministic tests that do not depend on live GitHub responses.

---

### Task 1: Profile Configuration and Test Harness

**Files:**
- Create: `pyproject.toml`
- Create: `requirements-dev.txt`
- Create: `.gitignore`
- Create: `scripts/__init__.py`
- Create: `scripts/profile_config.py`
- Create: `scripts/requirements.txt`
- Create: `scripts/requirements-local.txt`
- Create: `tests/test_profile_config.py`

**Interfaces:**
- Produces: `PROFILE_HOST: str`, `PROFILE_NAME: str`, `HEADLINE: str`, `ABOUT: str`, `CONTACT_LINKS: dict[str, str]`, `INFO_CARD_ROWS: tuple[tuple[str, ...], ...]`, `FEATURED_PROJECTS: tuple[dict[str, str | None], ...]`, and `STACK_GROUPS: tuple[tuple[str, tuple[str, ...]], ...]`.
- Consumes: no earlier task output.

- [ ] **Step 1: Create the Python test configuration**

Create `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
addopts = "-q"
```

Create `requirements-dev.txt`:

```text
pytest>=8.2,<9
```

Create `scripts/requirements.txt`:

```text
requests>=2.32.4,<3
beautifulsoup4>=4.12.3,<5
```

Create `scripts/requirements-local.txt`:

```text
Pillow>=10.4,<12
```

Create `scripts/__init__.py` as an empty file.

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.coverage
htmlcov/
.env
.env.*
source-photo.*
source-prepped.*
*.onnx
.DS_Store
Thumbs.db
```

- [ ] **Step 2: Write the failing configuration test**

Create `tests/test_profile_config.py`:

```python
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
```

- [ ] **Step 3: Run the test and verify failure**

Run:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/test_profile_config.py -v
```

Expected: collection fails because `scripts.profile_config` does not exist.

- [ ] **Step 4: Implement the approved profile configuration**

Create `scripts/profile_config.py`:

```python
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
```

- [ ] **Step 5: Run the configuration tests**

Run:

```bash
python -m pytest tests/test_profile_config.py -v
```

Expected: `3 passed`.

- [ ] **Step 6: Commit**

```bash
git add .gitignore pyproject.toml requirements-dev.txt scripts tests/test_profile_config.py
git commit -m "chore: add profile configuration and test harness"
```

---

### Task 2: Public Contribution Fetcher and Statistics

**Files:**
- Create: `scripts/fetch_contributions.py`
- Create: `tests/test_fetch_contributions.py`

**Interfaces:**
- Consumes: `PROFILE_HOST` from `scripts.profile_config`.
- Produces:
  - `parse_contribution_days(html_text: str) -> list[dict[str, str | int]]`
  - `compute_current_streak(days: list[dict[str, str | int]]) -> tuple[int, str | None, str | None]`
  - `compute_longest_streak(days: list[dict[str, str | int]]) -> tuple[int, str | None, str | None]`
  - `build_data(days: list[dict[str, str | int]], username: str, generated_at: str | None = None) -> dict[str, object]`
  - `fetch_contribution_html(username: str) -> str`
  - `write_data(data: dict[str, object], output_path: Path) -> None`
  - `main() -> int`

- [ ] **Step 1: Write contribution parsing and statistics tests**

Create `tests/test_fetch_contributions.py`:

```python
import json
from pathlib import Path

import pytest

from scripts.fetch_contributions import (
    build_data,
    compute_current_streak,
    compute_longest_streak,
    parse_contribution_days,
    write_data,
)


SAMPLE_HTML = """
<table>
  <tr>
    <td class="ContributionCalendar-day" data-date="2026-07-07" id="d1"></td>
    <td class="ContributionCalendar-day" data-date="2026-07-08" id="d2"></td>
    <td class="ContributionCalendar-day" data-date="2026-07-09" id="d3"></td>
    <td class="ContributionCalendar-day" data-date="2026-07-10" id="d4"></td>
  </tr>
</table>
<tool-tip for="d1">2 contributions on July 7, 2026</tool-tip>
<tool-tip for="d2">No contributions on July 8, 2026</tool-tip>
<tool-tip for="d3">4 contributions on July 9, 2026</tool-tip>
<tool-tip for="d4">No contributions on July 10, 2026</tool-tip>
"""


def test_parse_contribution_days() -> None:
    assert parse_contribution_days(SAMPLE_HTML) == [
        {"date": "2026-07-07", "count": 2},
        {"date": "2026-07-08", "count": 0},
        {"date": "2026-07-09", "count": 4},
        {"date": "2026-07-10", "count": 0},
    ]


def test_parse_contribution_days_rejects_missing_calendar() -> None:
    with pytest.raises(ValueError, match="No contribution calendar cells"):
        parse_contribution_days("<html></html>")


def test_current_streak_ignores_unfinished_zero_day() -> None:
    days = [
        {"date": "2026-07-07", "count": 0},
        {"date": "2026-07-08", "count": 3},
        {"date": "2026-07-09", "count": 1},
        {"date": "2026-07-10", "count": 0},
    ]
    assert compute_current_streak(days) == (
        2,
        "2026-07-08",
        "2026-07-09",
    )


def test_longest_streak() -> None:
    days = [
        {"date": "2026-07-05", "count": 1},
        {"date": "2026-07-06", "count": 1},
        {"date": "2026-07-07", "count": 0},
        {"date": "2026-07-08", "count": 2},
    ]
    assert compute_longest_streak(days) == (
        2,
        "2026-07-05",
        "2026-07-06",
    )


def test_build_data_is_deterministic() -> None:
    days = parse_contribution_days(SAMPLE_HTML)
    data = build_data(
        days,
        username="deserveto",
        generated_at="2026-07-11T00:00:00Z",
    )
    assert data["username"] == "deserveto"
    assert data["generated_at"] == "2026-07-11T00:00:00Z"
    assert data["total_contributions"] == 6
    assert data["active_days"] == 2
    assert data["avg_per_active_day"] == 3.0
    assert data["best_day"] == {"date": "2026-07-09", "count": 4}


def test_build_data_rejects_empty_days() -> None:
    with pytest.raises(ValueError, match="at least one contribution day"):
        build_data([], username="deserveto")


def test_write_data_creates_parent_directory(tmp_path: Path) -> None:
    output = tmp_path / "data" / "contributions.json"
    write_data({"username": "deserveto"}, output)
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "username": "deserveto"
    }
```

- [ ] **Step 2: Run the fetcher tests and verify failure**

Run:

```bash
python -m pip install -r scripts/requirements.txt
python -m pytest tests/test_fetch_contributions.py -v
```

Expected: collection fails because `scripts.fetch_contributions` does not exist.

- [ ] **Step 3: Implement the contribution fetcher**

Create `scripts/fetch_contributions.py`:

```python
#!/usr/bin/env python3
"""Fetch public GitHub contribution data and write normalized JSON."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from scripts.profile_config import PROFILE_HOST

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "data" / "contributions.json"
COUNT_PATTERN = re.compile(r"^([\d,]+)\s+contribution", re.IGNORECASE)


def parse_contribution_days(html_text: str) -> list[dict[str, str | int]]:
    soup = BeautifulSoup(html_text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        raise ValueError("No contribution calendar cells were found")

    days: list[dict[str, str | int]] = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue

        tooltip_id = cell.get("id")
        tooltip = (
            soup.find("tool-tip", attrs={"for": tooltip_id})
            if tooltip_id
            else None
        )
        text = tooltip.get_text(" ", strip=True) if tooltip else ""

        if re.search(r"\bno contributions?\b", text, re.IGNORECASE):
            count = 0
        else:
            match = COUNT_PATTERN.match(text)
            count = int(match.group(1).replace(",", "")) if match else 0

        days.append({"date": date, "count": count})

    if not days:
        raise ValueError("Contribution calendar cells contained no dated days")

    days.sort(key=lambda item: str(item["date"]))
    return days


def compute_current_streak(
    days: list[dict[str, str | int]],
) -> tuple[int, str | None, str | None]:
    if not days:
        return 0, None, None

    index = len(days) - 1
    if int(days[index]["count"]) == 0:
        index -= 1

    end_index = index
    streak = 0
    while index >= 0 and int(days[index]["count"]) > 0:
        streak += 1
        index -= 1

    if streak == 0:
        return 0, None, None

    start_index = index + 1
    return (
        streak,
        str(days[start_index]["date"]),
        str(days[end_index]["date"]),
    )


def compute_longest_streak(
    days: list[dict[str, str | int]],
) -> tuple[int, str | None, str | None]:
    longest = 0
    run = 0
    run_start = 0
    longest_start: str | None = None
    longest_end: str | None = None

    for index, day in enumerate(days):
        if int(day["count"]) > 0:
            if run == 0:
                run_start = index
            run += 1
            if run > longest:
                longest = run
                longest_start = str(days[run_start]["date"])
                longest_end = str(day["date"])
        else:
            run = 0

    return longest, longest_start, longest_end


def build_data(
    days: list[dict[str, str | int]],
    username: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if not days:
        raise ValueError("build_data requires at least one contribution day")

    total = sum(int(day["count"]) for day in days)
    active_days = sum(1 for day in days if int(day["count"]) > 0)
    best = max(days, key=lambda day: int(day["count"]))
    current = compute_current_streak(days)
    longest = compute_longest_streak(days)

    monthly: dict[str, int] = {}
    for day in days:
        month = str(day["date"])[:7]
        monthly[month] = monthly.get(month, 0) + int(day["count"])

    timestamp = generated_at or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    return {
        "username": username,
        "generated_at": timestamp,
        "range": {
            "start": str(days[0]["date"]),
            "end": str(days[-1]["date"]),
        },
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": (
            round(total / active_days, 1) if active_days else 0
        ),
        "current_streak": {
            "length": current[0],
            "start": current[1],
            "end": current[2],
        },
        "longest_streak": {
            "length": longest[0],
            "start": longest[1],
            "end": longest[2],
        },
        "best_day": {
            "date": str(best["date"]),
            "count": int(best["count"]),
        },
        "monthly": [
            {"month": month, "total": total_count}
            for month, total_count in sorted(monthly.items())
        ],
        "days": days,
    }


def fetch_contribution_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(
        url,
        headers={"User-Agent": "deserveto-profile-readme/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def write_data(data: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    username = os.environ.get("GH_PROFILE_USER", PROFILE_HOST)
    html_text = fetch_contribution_html(username)
    days = parse_contribution_days(html_text)
    data = build_data(days, username=username)
    write_data(data, DEFAULT_OUTPUT)
    print(
        f"Wrote {DEFAULT_OUTPUT}: "
        f"{data['total_contributions']} contributions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the fetcher tests**

Run:

```bash
python -m pytest tests/test_fetch_contributions.py -v
```

Expected: `7 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_contributions.py tests/test_fetch_contributions.py
git commit -m "feat: add public contribution data fetcher"
```

---

### Task 3: Safe Monochrome Contribution Heatmap

**Files:**
- Create: `scripts/render_heatmap_svg.py`
- Create: `tests/test_render_heatmap_svg.py`

**Interfaces:**
- Consumes: the normalized JSON shape returned by `build_data`.
- Produces:
  - `level_for(count: int) -> int`
  - `build_grid(days: list[dict[str, str | int]]) -> list[list[tuple[str, int, int] | None]]`
  - `validate_data(data: dict[str, object]) -> None`
  - `render(data: dict[str, object]) -> str`
  - `write_svg(svg: str, output_path: Path) -> None`

- [ ] **Step 1: Write renderer tests**

Create `tests/test_render_heatmap_svg.py`:

```python
import xml.etree.ElementTree as ET

import pytest

from scripts.render_heatmap_svg import (
    build_grid,
    level_for,
    render,
    validate_data,
)


def sample_data() -> dict[str, object]:
    return {
        "username": "deserveto",
        "generated_at": "2026-07-11T00:00:00Z",
        "range": {"start": "2026-07-05", "end": "2026-07-11"},
        "total_contributions": 12,
        "active_days": 4,
        "avg_per_active_day": 3.0,
        "current_streak": {
            "length": 2,
            "start": "2026-07-10",
            "end": "2026-07-11",
        },
        "longest_streak": {
            "length": 2,
            "start": "2026-07-10",
            "end": "2026-07-11",
        },
        "best_day": {"date": "2026-07-10", "count": 5},
        "monthly": [{"month": "2026-07", "total": 12}],
        "days": [
            {"date": "2026-07-05", "count": 0},
            {"date": "2026-07-06", "count": 1},
            {"date": "2026-07-07", "count": 2},
            {"date": "2026-07-08", "count": 0},
            {"date": "2026-07-09", "count": 4},
            {"date": "2026-07-10", "count": 5},
            {"date": "2026-07-11", "count": 0},
        ],
    }


@pytest.mark.parametrize(
    ("count", "expected"),
    [(0, 0), (1, 1), (5, 1), (6, 2), (15, 2), (16, 3), (31, 4), (51, 5)],
)
def test_level_for(count: int, expected: int) -> None:
    assert level_for(count) == expected


def test_grid_starts_on_sunday() -> None:
    grid = build_grid(sample_data()["days"])  # type: ignore[arg-type]
    assert len(grid) == 1
    assert grid[0][0] == ("2026-07-05", 0, 0)


def test_validate_data_rejects_empty_days() -> None:
    data = sample_data()
    data["days"] = []
    with pytest.raises(ValueError, match="non-empty days"):
        validate_data(data)


def test_render_is_valid_safe_monochrome_svg() -> None:
    svg = render(sample_data())
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert "<script" not in svg.lower()
    assert "foreignObject" not in svg
    assert "href=" not in svg
    assert "avi@github" not in svg
    assert "deserveto@github" in svg
    for forbidden_color in ("#22d3ee", "#39d353", "#f2cc60"):
        assert forbidden_color not in svg
    assert "@keyframes cell" in svg
    assert "12 contributions" in svg
```

- [ ] **Step 2: Run the renderer tests and verify failure**

Run:

```bash
python -m pytest tests/test_render_heatmap_svg.py -v
```

Expected: collection fails because `scripts.render_heatmap_svg` does not exist.

- [ ] **Step 3: Implement the heatmap module**

Create `scripts/render_heatmap_svg.py` by adapting the reviewed Drive script with these exact public interfaces and visual constants:

```python
#!/usr/bin/env python3
"""Render normalized contribution data as a safe monochrome SVG."""

from __future__ import annotations

from datetime import date
import html
import json
from pathlib import Path
from typing import Any

from scripts.profile_config import PROFILE_HOST

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "data" / "contributions.json"
OUTPUT_PATH = ROOT / "contrib-heatmap.svg"

PALETTE = (
    "#161b22",
    "#30363d",
    "#484f58",
    "#6e7681",
    "#8b949e",
    "#f0f6fc",
)
CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT_LABEL_WIDTH = 30
TOP_LABEL_HEIGHT = 20
TITLEBAR_HEIGHT = 30
BACKGROUND = "#0d1117"
BACKGROUND_TOP = "#161b22"
FRAME = "#30363d"
MUTED = "#8b949e"
TEXT = "#f0f6fc"
DOTS = ("#8b949e", "#6e7681", "#484f58")
COLUMN_DELAY = 0.018
ROW_DELAY = 0.045
CELL_DURATION = 0.42


def level_for(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def build_grid(
    days: list[dict[str, str | int]],
) -> list[list[tuple[str, int, int] | None]]:
    first = date.fromisoformat(str(days[0]["date"]))
    leading = (first.weekday() + 1) % 7
    grid: list[list[tuple[str, int, int] | None]] = []
    column: list[tuple[str, int, int] | None] = [None] * leading

    for item in days:
        day_date = date.fromisoformat(str(item["date"]))
        weekday = (day_date.weekday() + 1) % 7
        while len(column) < weekday:
            column.append(None)

        count = int(item["count"])
        column.append((str(item["date"]), count, level_for(count)))
        if len(column) == 7:
            grid.append(column)
            column = []

    if column:
        column.extend([None] * (7 - len(column)))
        grid.append(column)

    return grid


def validate_data(data: dict[str, Any]) -> None:
    days = data.get("days")
    if not isinstance(days, list) or not days:
        raise ValueError("Contribution data requires a non-empty days list")

    for item in days:
        if not isinstance(item, dict):
            raise ValueError("Each contribution day must be an object")
        date.fromisoformat(str(item.get("date")))
        count = item.get("count")
        if not isinstance(count, int) or count < 0:
            raise ValueError("Each contribution count must be a non-negative integer")


def render(data: dict[str, Any]) -> str:
    validate_data(data)
    days = data["days"]
    grid = build_grid(days)
    columns = len(grid)
    art_width = columns * STEP
    art_height = 7 * STEP
    canvas_width = PAD + LEFT_LABEL_WIDTH + art_width + PAD
    stats_height = 88
    canvas_height = (
        TITLEBAR_HEIGHT
        + TOP_LABEL_HEIGHT
        + art_height
        + stats_height
        + PAD
    )

    css = (
        "@keyframes cell{0%{opacity:0;transform:translateY(-6px)}"
        "100%{opacity:1;transform:translateY(0)}}"
        f".c{{opacity:0;animation:cell {CELL_DURATION:.2f}s "
        "cubic-bezier(.2,.8,.2,1) both}}"
    )

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{canvas_width}" height="{canvas_height}" '
            f'viewBox="0 0 {canvas_width} {canvas_height}" '
            'font-family="ui-monospace, SFMono-Regular, Menlo, '
            'Consolas, monospace">'
        ),
        f"<style>{css}</style>",
        (
            '<defs><linearGradient id="background" x1="0" y1="0" '
            'x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BACKGROUND_TOP}"/>'
            f'<stop offset="1" stop-color="{BACKGROUND}"/>'
            "</linearGradient></defs>"
        ),
        (
            f'<rect width="{canvas_width}" height="{canvas_height}" '
            'rx="12" fill="url(#background)"/>'
        ),
        (
            f'<rect x="0.5" y="0.5" width="{canvas_width - 1}" '
            f'height="{canvas_height - 1}" rx="12" fill="none" '
            f'stroke="{FRAME}"/>'
        ),
        (
            f'<line x1="0" y1="{TITLEBAR_HEIGHT}" '
            f'x2="{canvas_width}" y2="{TITLEBAR_HEIGHT}" '
            f'stroke="{FRAME}"/>'
        ),
    ]

    for index, dot_color in enumerate(DOTS):
        parts.append(
            f'<circle cx="{PAD + index * 16}" '
            f'cy="{TITLEBAR_HEIGHT / 2}" r="5" fill="{dot_color}"/>'
        )

    parts.append(
        f'<text x="{canvas_width / 2}" '
        f'y="{TITLEBAR_HEIGHT / 2 + 4}" fill="{MUTED}" '
        f'font-size="12" text-anchor="middle">'
        f'{html.escape(PROFILE_HOST)}@github: contributions</text>'
    )

    grid_top = TITLEBAR_HEIGHT + TOP_LABEL_HEIGHT
    grid_left = PAD + LEFT_LABEL_WIDTH

    seen_months: set[tuple[int, int]] = set()
    for column_index, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            current_date = date.fromisoformat(cell[0])
            key = (current_date.year, current_date.month)
            if key not in seen_months and current_date.day <= 7:
                seen_months.add(key)
                parts.append(
                    f'<text x="{grid_left + column_index * STEP}" '
                    f'y="{TITLEBAR_HEIGHT + 14}" fill="{MUTED}" '
                    f'font-size="10">{current_date.strftime("%b")}</text>'
                )
            break

    for row_index, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = grid_top + row_index * STEP + CELL * 0.78
        parts.append(
            f'<text x="{PAD}" y="{y:.1f}" fill="{MUTED}" '
            f'font-size="9">{label}</text>'
        )

    for column_index, column in enumerate(grid):
        x = grid_left + column_index * STEP
        for row_index, cell in enumerate(column):
            if cell is None:
                continue
            date_text, count, level = cell
            y = grid_top + row_index * STEP
            delay = column_index * COLUMN_DELAY + row_index * ROW_DELAY
            noun = "contribution" if count == 1 else "contributions"
            parts.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" '
                f'height="{CELL}" rx="2.5" fill="{PALETTE[level]}" '
                f'style="animation-delay:{delay:.3f}s">'
                f'<title>{html.escape(date_text)}: {count} {noun}</title>'
                "</rect>"
            )

    legend_y = grid_top + art_height + 6
    legend_x = canvas_width - PAD - (len(PALETTE) * (CELL - 1) + 70)
    parts.append(
        f'<text x="{legend_x}" y="{legend_y + CELL * 0.8:.1f}" '
        f'fill="{MUTED}" font-size="10" text-anchor="end">Less</text>'
    )
    current_x = legend_x + 8
    for color in PALETTE:
        parts.append(
            f'<rect x="{current_x}" y="{legend_y}" width="{CELL - 1}" '
            f'height="{CELL - 1}" rx="2.2" fill="{color}"/>'
        )
        current_x += CELL
    parts.append(
        f'<text x="{current_x + 4}" '
        f'y="{legend_y + CELL * 0.8:.1f}" fill="{MUTED}" '
        'font-size="10">More</text>'
    )

    separator_y = legend_y + CELL + 14
    parts.append(
        f'<line x1="0" y1="{separator_y}" x2="{canvas_width}" '
        f'y2="{separator_y}" stroke="{FRAME}"/>'
    )

    current_streak = int(data["current_streak"]["length"])
    longest_streak = int(data["longest_streak"]["length"])
    total = int(data["total_contributions"])
    best = data["best_day"]
    contribution_range = data["range"]
    line_y = separator_y + 24

    parts.append(
        f'<text x="{PAD}" y="{line_y}" font-size="13" fill="{TEXT}">'
        f'<tspan font-weight="700">{total:,}</tspan>'
        f'<tspan fill="{MUTED}"> contributions in the last year</tspan>'
        "</text>"
    )
    parts.append(
        f'<text x="{canvas_width - PAD}" y="{line_y}" '
        f'font-size="12" fill="{MUTED}" text-anchor="end">'
        f'{contribution_range["start"]} &#8594; '
        f'{contribution_range["end"]}</text>'
    )

    line_y += 24
    parts.append(
        f'<text x="{PAD}" y="{line_y}" font-size="13" fill="{MUTED}">'
        f'current streak <tspan fill="{TEXT}" font-weight="700">'
        f'{current_streak} days</tspan>'
        f'<tspan>   &#183;   longest </tspan>'
        f'<tspan fill="{TEXT}" font-weight="700">'
        f'{longest_streak} days</tspan></text>'
    )
    parts.append(
        f'<text x="{canvas_width - PAD}" y="{line_y}" '
        f'font-size="12" fill="{MUTED}" text-anchor="end">'
        f'best day <tspan fill="{TEXT}" font-weight="700">'
        f'{best["count"]}</tspan> on {best["date"]}</text>'
    )

    parts.append("</svg>")
    return "".join(parts)


def write_svg(svg: str, output_path: Path) -> None:
    output_path.write_text(svg + "\n", encoding="utf-8")


def main() -> int:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    svg = render(data)
    write_svg(svg, OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the renderer tests**

Run:

```bash
python -m pytest tests/test_render_heatmap_svg.py -v
```

Expected: all parameterized and renderer tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/render_heatmap_svg.py tests/test_render_heatmap_svg.py
git commit -m "feat: add monochrome contribution heatmap"
```

---

### Task 4: Matching Information Card

**Files:**
- Create: `scripts/make_info_card.py`
- Create: `tests/test_make_info_card.py`

**Interfaces:**
- Consumes: `PROFILE_HOST` and `INFO_CARD_ROWS` from `scripts.profile_config`.
- Produces:
  - `render_info_card(host: str, rows: tuple[tuple[str, ...], ...], static: bool = False) -> str`
  - `write_svg(svg: str, output_path: Path) -> None`

- [ ] **Step 1: Write information-card tests**

Create `tests/test_make_info_card.py`:

```python
import xml.etree.ElementTree as ET

from scripts.make_info_card import render_info_card
from scripts.profile_config import INFO_CARD_ROWS, PROFILE_HOST


def test_info_card_contains_approved_content() -> None:
    svg = render_info_card(PROFILE_HOST, INFO_CARD_ROWS, static=True)
    ET.fromstring(svg)
    assert "deserveto@github" in svg
    assert "Information Technology Student" in svg
    assert "Telkom University" in svg
    assert "Phishing detection research with GNN" in svg
    assert "Avi Vashishta" not in svg
    assert "Your current role" not in svg


def test_info_card_is_safe_and_monochrome() -> None:
    svg = render_info_card(PROFILE_HOST, INFO_CARD_ROWS, static=False)
    assert "<script" not in svg.lower()
    assert "foreignObject" not in svg
    assert "href=" not in svg
    assert "#ffa657" not in svg
    assert "#58a6ff" not in svg
    assert "#22d3ee" not in svg
    assert "animateTransform" in svg
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pytest tests/test_make_info_card.py -v
```

Expected: collection fails because `scripts.make_info_card` does not exist.

- [ ] **Step 3: Implement the information-card renderer**

Create `scripts/make_info_card.py`:

```python
#!/usr/bin/env python3
"""Render the approved profile facts as a matching animated SVG card."""

from __future__ import annotations

import html
import os
from pathlib import Path

from scripts.profile_config import INFO_CARD_ROWS, PROFILE_HOST

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "info-card.svg"

WIDTH = 480
HEIGHT = 376
PAD = 20
TITLEBAR_HEIGHT = 30
KEY_X = PAD
VALUE_X = PAD + 92
LINE_HEIGHT = 20.5

BACKGROUND = "#0d1117"
BACKGROUND_TOP = "#161b22"
FRAME = "#30363d"
MUTED = "#8b949e"
TEXT = "#f0f6fc"
KEY = "#c9d1d9"
SECTION = "#8b949e"
DOTS = ("#8b949e", "#6e7681", "#484f58")


def animated_group(inner: str, index: int, static: bool) -> str:
    if static:
        return f"<g>{inner}</g>"

    delay = 0.15 + index * 0.06
    return (
        '<g opacity="0" transform="translate(0,5)">'
        f"{inner}"
        f'<animate attributeName="opacity" from="0" to="1" '
        f'begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 5" to="0 0" begin="{delay:.2f}s" dur="0.4s" '
        'fill="freeze" calcMode="spline" '
        'keySplines="0.2 0.8 0.2 1"/>'
        "</g>"
    )


def render_info_card(
    host: str,
    rows: tuple[tuple[str, ...], ...],
    static: bool = False,
) -> str:
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
            f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
            'font-family="ui-monospace, SFMono-Regular, Menlo, '
            'Consolas, monospace">'
        ),
        (
            '<defs><linearGradient id="background" x1="0" y1="0" '
            'x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BACKGROUND_TOP}"/>'
            f'<stop offset="1" stop-color="{BACKGROUND}"/>'
            "</linearGradient></defs>"
        ),
        (
            f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" '
            'fill="url(#background)"/>'
        ),
        (
            f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" '
            f'height="{HEIGHT - 1}" rx="12" fill="none" '
            f'stroke="{FRAME}"/>'
        ),
        (
            f'<line x1="0" y1="{TITLEBAR_HEIGHT}" x2="{WIDTH}" '
            f'y2="{TITLEBAR_HEIGHT}" stroke="{FRAME}"/>'
        ),
    ]

    for index, dot_color in enumerate(DOTS):
        parts.append(
            f'<circle cx="{PAD + index * 16}" '
            f'cy="{TITLEBAR_HEIGHT / 2}" r="5" fill="{dot_color}"/>'
        )

    parts.append(
        f'<text x="{WIDTH / 2}" y="{TITLEBAR_HEIGHT / 2 + 4}" '
        f'fill="{MUTED}" font-size="12" text-anchor="middle">'
        f'{html.escape(host)}@github: profile</text>'
    )

    y = TITLEBAR_HEIGHT + 30
    for index, row in enumerate(rows):
        kind = row[0]
        if kind == "gap":
            y += LINE_HEIGHT * 0.5
            continue

        if kind == "host":
            host_text = html.escape(host)
            rule_x = KEY_X + (len(host) + 7) * 8 + 8
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{TEXT}" '
                f'font-size="14" font-weight="700">'
                f'{host_text}@github</text>'
                f'<line x1="{rule_x}" y1="{y - 4:.1f}" '
                f'x2="{WIDTH - PAD}" y2="{y - 4:.1f}" '
                f'stroke="{FRAME}"/>'
            )
        elif kind == "sec":
            title = html.escape(row[1])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" '
                f'font-size="12.5" font-weight="700">'
                f'&#8212; {title}</text>'
                f'<line x1="{KEY_X + 12 + len(row[1]) * 8}" '
                f'y1="{y - 4:.1f}" x2="{WIDTH - PAD}" '
                f'y2="{y - 4:.1f}" stroke="{FRAME}"/>'
            )
        elif kind == "kv":
            key = html.escape(row[1])
            value = html.escape(row[2])
            inner = (
                f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" '
                f'font-size="12.5" font-weight="700">{key}</text>'
                f'<text x="{VALUE_X}" y="{y:.1f}" fill="{TEXT}" '
                f'font-size="12.5">{value}</text>'
            )
        elif kind == "bul":
            text = html.escape(row[1])
            inner = (
                f'<circle cx="{KEY_X + 3}" cy="{y - 4:.1f}" '
                f'r="2.5" fill="{KEY}"/>'
                f'<text x="{KEY_X + 14}" y="{y:.1f}" fill="{TEXT}" '
                f'font-size="12.5">{text}</text>'
            )
        else:
            raise ValueError(f"Unsupported row kind: {kind}")

        parts.append(animated_group(inner, index, static))
        y += LINE_HEIGHT

    if y > HEIGHT - 12:
        raise ValueError(
            f"Information-card content exceeds the {HEIGHT}px canvas"
        )

    parts.append("</svg>")
    return "".join(parts)


def write_svg(svg: str, output_path: Path) -> None:
    output_path.write_text(svg + "\n", encoding="utf-8")


def main() -> int:
    static = bool(os.environ.get("STATIC"))
    svg = render_info_card(PROFILE_HOST, INFO_CARD_ROWS, static=static)
    write_svg(svg, OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run information-card tests**

Run:

```bash
python -m pytest tests/test_make_info_card.py -v
```

Expected: `2 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/make_info_card.py tests/test_make_info_card.py
git commit -m "feat: add professional profile information card"
```

---

### Task 5: Animated ASCII Portrait Generator

**Files:**
- Create: `scripts/make_ascii_svg.py`
- Create: `tests/test_make_ascii_svg.py`

**Interfaces:**
- Consumes: a local grayscale portrait path that is not stored in the repository.
- Produces:
  - `image_to_ascii_rows(image: Image.Image, cols: int = 100, rows: int = 53) -> list[str]`
  - `render_ascii_svg(rows: list[str], host: str, display_name: str, static: bool = False) -> str`
  - `generate(input_path: Path, output_path: Path, static: bool = False) -> None`

- [ ] **Step 1: Write portrait-generator tests**

Create `tests/test_make_ascii_svg.py`:

```python
import xml.etree.ElementTree as ET

from PIL import Image

from scripts.make_ascii_svg import image_to_ascii_rows, render_ascii_svg


def test_image_to_ascii_rows_has_requested_dimensions() -> None:
    image = Image.new("L", (20, 20), color=64)
    rows = image_to_ascii_rows(image, cols=10, rows=4)
    assert len(rows) == 4
    assert all(len(row) == 10 for row in rows)


def test_white_pixels_become_spaces() -> None:
    image = Image.new("L", (4, 2), color=255)
    rows = image_to_ascii_rows(image, cols=4, rows=2)
    assert rows == ["    ", "    "]


def test_portrait_svg_uses_approved_identity_and_safe_animation() -> None:
    rows = [" .:-", "=+*#", "%@  "]
    svg = render_ascii_svg(
        rows,
        host="deserveto",
        display_name="Fikri Tri Wibowo",
        static=False,
    )
    ET.fromstring(svg)
    assert "deserveto@github" in svg
    assert "Fikri Tri Wibowo" in svg
    assert "Avi Vashishta" not in svg
    assert "<script" not in svg.lower()
    assert "foreignObject" not in svg
    assert "href=" not in svg
    assert "#ff5f56" not in svg
    assert "<animate " in svg
```

- [ ] **Step 2: Run tests and verify failure**

Run:

```bash
python -m pip install -r scripts/requirements-local.txt
python -m pytest tests/test_make_ascii_svg.py -v
```

Expected: collection fails because `scripts.make_ascii_svg` does not exist.

- [ ] **Step 3: Implement the portrait generator**

Create `scripts/make_ascii_svg.py` with the reviewed Drive algorithm, refactored into pure functions and changed to the approved identity and neutral palette. Use these exact constants and function boundaries:

```python
#!/usr/bin/env python3
"""Convert a local grayscale portrait into an animated monochrome ASCII SVG."""

from __future__ import annotations

import html
import os
from pathlib import Path
import sys

from PIL import Image, ImageEnhance

from scripts.profile_config import PROFILE_HOST, PROFILE_NAME

RAMP = " .`:-=+*cs#%@"
DEFAULT_COLUMNS = 100
DEFAULT_ROWS = 53
CELL_WIDTH = 8
CELL_HEIGHT = 15
CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.18
WHITE_FLOOR = 0.80
PAD = 20
TITLEBAR_HEIGHT = 30
STATUS_HEIGHT = 30
BACKGROUND = "#0d1117"
BACKGROUND_TOP = "#161b22"
FRAME = "#30363d"
MUTED = "#8b949e"
TEXT = "#f0f6fc"
DOTS = ("#8b949e", "#6e7681", "#484f58")
ROW_DURATION = 0.11
ROW_STAGGER = 0.11


def image_to_ascii_rows(
    image: Image.Image,
    cols: int = DEFAULT_COLUMNS,
    rows: int = DEFAULT_ROWS,
) -> list[str]:
    grayscale = image.convert("L")
    grayscale = ImageEnhance.Brightness(grayscale).enhance(BRIGHTNESS)
    grayscale = ImageEnhance.Contrast(grayscale).enhance(CONTRAST)
    grayscale = grayscale.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = grayscale.load()

    output: list[str] = []
    for y in range(rows):
        characters: list[str] = []
        for x in range(cols):
            luminance = float(pixels[x, y]) / 255.0
            luminance = pow(luminance, GAMMA)
            if luminance >= WHITE_FLOOR:
                characters.append(" ")
                continue

            index = int((1.0 - luminance) * (len(RAMP) - 1) + 0.5)
            index = max(0, min(len(RAMP) - 1, index))
            characters.append(RAMP[index])
        output.append("".join(characters))

    return output


def render_ascii_svg(
    rows: list[str],
    host: str,
    display_name: str,
    static: bool = False,
) -> str:
    if not rows or not rows[0]:
        raise ValueError("ASCII rows must be non-empty")
    if any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("All ASCII rows must have the same width")

    columns = len(rows[0])
    row_count = len(rows)
    art_width = columns * CELL_WIDTH
    art_height = row_count * CELL_HEIGHT
    canvas_width = art_width + PAD * 2
    canvas_height = (
        TITLEBAR_HEIGHT + art_height + STATUS_HEIGHT + PAD
    )
    art_top = TITLEBAR_HEIGHT + PAD * 0.35

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{canvas_width}" height="{canvas_height}" '
            f'viewBox="0 0 {canvas_width} {canvas_height}" '
            'font-family="ui-monospace, SFMono-Regular, Menlo, '
            'Consolas, monospace">'
        ),
        (
            '<defs><linearGradient id="background" x1="0" y1="0" '
            'x2="0" y2="1">'
            f'<stop offset="0" stop-color="{BACKGROUND_TOP}"/>'
            f'<stop offset="1" stop-color="{BACKGROUND}"/>'
            "</linearGradient></defs>"
        ),
        (
            f'<rect width="{canvas_width}" height="{canvas_height}" '
            'rx="12" fill="url(#background)"/>'
        ),
        (
            f'<rect x="0.5" y="0.5" width="{canvas_width - 1}" '
            f'height="{canvas_height - 1}" rx="12" fill="none" '
            f'stroke="{FRAME}"/>'
        ),
        (
            f'<line x1="0" y1="{TITLEBAR_HEIGHT}" '
            f'x2="{canvas_width}" y2="{TITLEBAR_HEIGHT}" '
            f'stroke="{FRAME}"/>'
        ),
    ]

    for index, dot_color in enumerate(DOTS):
        parts.append(
            f'<circle cx="{PAD + index * 16}" '
            f'cy="{TITLEBAR_HEIGHT / 2}" r="5" fill="{dot_color}"/>'
        )

    parts.append(
        f'<text x="{canvas_width / 2}" '
        f'y="{TITLEBAR_HEIGHT / 2 + 4}" fill="{MUTED}" '
        f'font-size="12" text-anchor="middle">'
        f'{html.escape(host)}@github: portrait</text>'
    )

    font_size = CELL_HEIGHT * 0.86
    for row_index, line in enumerate(rows):
        y = art_top + row_index * CELL_HEIGHT + CELL_HEIGHT * 0.74
        row_y = art_top + row_index * CELL_HEIGHT
        delay = row_index * ROW_STAGGER
        safe_line = html.escape(line)
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" '
            f'fill="{TEXT}" font-size="{font_size:.1f}" '
            f'textLength="{art_width}" lengthAdjust="spacing">'
            f"{safe_line}</text>"
        )

        if static:
            parts.append(text)
            continue

        parts.append(
            f'<clipPath id="row-{row_index}">'
            f'<rect x="{PAD}" y="{row_y:.1f}" '
            f'height="{CELL_HEIGHT}" width="0">'
            f'<animate attributeName="width" from="0" '
            f'to="{art_width}" begin="{delay:.3f}s" '
            f'dur="{ROW_DURATION:.2f}s" fill="freeze"/>'
            "</rect></clipPath>"
        )
        parts.append(
            f'<g clip-path="url(#row-{row_index})">{text}</g>'
        )
        parts.append(
            f'<rect y="{row_y + 1:.1f}" width="{CELL_WIDTH}" '
            f'height="{CELL_HEIGHT - 2}" fill="{TEXT}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" '
            f'to="{PAD + art_width}" begin="{delay:.3f}s" '
            f'dur="{ROW_DURATION:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" '
            f'begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" '
            f'begin="{delay + ROW_DURATION:.3f}s"/>'
            "</rect>"
        )

    status_line_y = TITLEBAR_HEIGHT + art_height + PAD * 0.35
    status_y = status_line_y + 19
    parts.append(
        f'<line x1="0" y1="{status_line_y:.1f}" '
        f'x2="{canvas_width}" y2="{status_line_y:.1f}" '
        f'stroke="{FRAME}"/>'
    )
    parts.append(
        f'<text x="{PAD}" y="{status_y:.1f}" fill="{MUTED}" '
        f'font-size="13">{html.escape(host)}@github:~$ whoami '
        f'<tspan fill="{TEXT}">{html.escape(display_name)}</tspan>'
        "</text>"
    )
    parts.append(
        f'<rect x="{PAD + 284}" y="{status_y - 12:.1f}" '
        f'width="8" height="14" fill="{TEXT}">'
        '<animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.5;0.51;1" dur="1s" '
        'repeatCount="indefinite"/></rect>'
    )

    parts.append("</svg>")
    return "".join(parts)


def generate(
    input_path: Path,
    output_path: Path,
    static: bool = False,
) -> None:
    with Image.open(input_path) as image:
        rows = image_to_ascii_rows(image)
    svg = render_ascii_svg(
        rows,
        host=PROFILE_HOST,
        display_name=PROFILE_NAME,
        static=static,
    )
    output_path.write_text(svg + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    arguments = argv if argv is not None else sys.argv[1:]
    if not arguments:
        raise SystemExit(
            "Usage: python scripts/make_ascii_svg.py "
            "<preprocessed-image> [output.svg]"
        )

    input_path = Path(arguments[0])
    output_path = Path(arguments[1]) if len(arguments) > 1 else Path(
        "avi-ascii.svg"
    )
    generate(
        input_path,
        output_path,
        static=bool(os.environ.get("STATIC")),
    )
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run portrait-generator tests**

Run:

```bash
python -m pytest tests/test_make_ascii_svg.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add scripts/make_ascii_svg.py tests/test_make_ascii_svg.py scripts/requirements-local.txt
git commit -m "feat: add animated ASCII portrait generator"
```

---

### Task 6: Final Profile README

**Files:**
- Create: `README.md`
- Create: `tests/test_readme_contract.py`

**Interfaces:**
- Consumes: `avi-ascii.svg`, `info-card.svg`, `contrib-heatmap.svg`, approved identity and links.
- Produces: the profile page rendered by GitHub.

- [ ] **Step 1: Write README contract tests**

Create `tests/test_readme_contract.py`:

```python
from pathlib import Path


README_PATH = Path("README.md")


def test_readme_contains_required_sections_and_assets() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    for required in (
        "Fikri Tri Wibowo",
        "Information Technology Student",
        "## About Me",
        "## Featured Projects",
        "## Technology Stack",
        "## Contributions",
        "## Contact",
        "./avi-ascii.svg",
        "./info-card.svg",
        "./contrib-heatmap.svg",
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
    for forbidden in (
        "YOUR_NAME",
        "YOURHANDLE",
        "yoursite.com",
        "Avi Vashishta",
        "PhishGNN-EEF](",
        "Azure VM Portfolio](",
    ):
        assert forbidden not in text
```

- [ ] **Step 2: Run README tests and verify failure**

Run:

```bash
python -m pytest tests/test_readme_contract.py -v
```

Expected: all tests fail because `README.md` does not exist.

- [ ] **Step 3: Create the final README**

Create `README.md`:

```markdown
<div align="center">

<table>
<tr>
<td valign="top"><img src="./avi-ascii.svg" width="370" alt="Animated ASCII portrait of Fikri Tri Wibowo" /></td>
<td valign="top"><img src="./info-card.svg" width="490" alt="Profile information for Fikri Tri Wibowo" /></td>
</tr>
</table>

# Fikri Tri Wibowo

**Information Technology Student · Cybersecurity · AI/ML · Software Development**

[GitHub](https://github.com/deserveto) ·
[LinkedIn](https://www.linkedin.com/in/fikri-tri-wibowo-446034296/) ·
[Instagram](https://www.instagram.com/fikritw_/)

</div>

## About Me

I am an Information Technology student at Telkom University with a strong interest in cybersecurity, artificial intelligence, networking, cloud infrastructure, and software development. I enjoy building practical systems, exploring security problems, and applying machine learning to real-world challenges.

## Featured Projects

| Project | Description | Access |
| --- | --- | --- |
| **PhishGNN-EEF** | Research on phishing website detection using Graph Neural Networks with enhanced edge features on hyperlink graphs. | Research project |
| **[VulnScan Toolkit](https://github.com/deserveto/vulnscan-toolkit)** | A command-line vulnerability scanner that combines Nmap service discovery, NSE checks, CVE correlation, and minimalist HTML reporting. | Public repository |
| **[ZipLift](https://github.com/deserveto/ZipLift)** | A cross-platform archive manager built with Tauri, Rust, React, and TypeScript for creating, browsing, and extracting common archive formats. | Public repository |
| **Azure VM Portfolio** | A portfolio deployment on an Ubuntu virtual machine using Apache, PHP, Git, and firewall configuration. | Infrastructure project |

## Technology Stack

- **Languages:** Python, JavaScript, TypeScript, PHP, Java, C++
- **AI / ML:** PyTorch, PyTorch Geometric, Graph Neural Networks, scikit-learn
- **Web:** Laravel, Next.js, HTML, CSS, Tailwind CSS
- **Cloud and infrastructure:** Azure, Google Cloud, Linux, Apache
- **Security and networking:** Vulnerability assessment, phishing detection, Wireshark, Packet Tracer
- **Tools:** Git, GitHub, Docker, VS Code

## Contributions

<div align="center">
<img src="./contrib-heatmap.svg" width="860" alt="Animated GitHub contribution graph for deserveto" />
</div>

## Contact

- GitHub: [@deserveto](https://github.com/deserveto)
- LinkedIn: [Fikri Tri Wibowo](https://www.linkedin.com/in/fikri-tri-wibowo-446034296/)
- Instagram: [@fikritw_](https://www.instagram.com/fikritw_/)
```

- [ ] **Step 4: Run README tests**

Run:

```bash
python -m pytest tests/test_readme_contract.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/test_readme_contract.py
git commit -m "feat: add expanded professional profile README"
```

---

### Task 7: Generate Initial Profile Assets

**Files:**
- Create: `avi-ascii.svg`
- Create: `info-card.svg`
- Create: `data/contributions.json`
- Create: `contrib-heatmap.svg`

**Interfaces:**
- Consumes:
  - Uploaded portrait at `/mnt/data/Screenshot 2026-04-20 060415.png`.
  - Local-only reviewed preprocessor at `/mnt/data/prep_photo.py`.
  - Public GitHub contribution endpoint for `deserveto`.
- Produces: the four files referenced by `README.md`.
- Privacy boundary: `/tmp/source-prepped.png` and the uploaded source file remain outside Git.

- [ ] **Step 1: Install local-only image preparation dependencies**

Run:

```bash
python -m pip install \
  "Pillow>=10.4,<12" \
  numpy \
  opencv-python-headless \
  rembg \
  onnxruntime
```

Expected: installation completes without changing repository dependency files.

- [ ] **Step 2: Preprocess the uploaded portrait outside the repository**

Run:

```bash
python /mnt/data/prep_photo.py \
  "/mnt/data/Screenshot 2026-04-20 060415.png" \
  /tmp/source-prepped.png
```

Expected: `/tmp/source-prepped.png` exists and no `source-photo` or `source-prepped` file exists inside the repository.

- [ ] **Step 3: Generate a static portrait preview**

Run:

```bash
STATIC=1 python scripts/make_ascii_svg.py \
  /tmp/source-prepped.png \
  /tmp/avi-ascii-static.svg
```

Expected: `/tmp/avi-ascii-static.svg` is valid XML and visibly resembles the uploaded portrait when rendered.

- [ ] **Step 4: Generate the animated portrait**

Run:

```bash
python scripts/make_ascii_svg.py \
  /tmp/source-prepped.png \
  avi-ascii.svg
```

Expected: `avi-ascii.svg` contains SMIL `<animate>` elements and the approved identity.

- [ ] **Step 5: Generate the information card**

Run:

```bash
python scripts/make_info_card.py
```

Expected: `info-card.svg` is created and contains the approved role, study, stack, and highlights.

- [ ] **Step 6: Fetch contribution data**

Run:

```bash
GH_PROFILE_USER=deserveto python scripts/fetch_contributions.py
```

Expected: `data/contributions.json` is created with `username` equal to `deserveto` and a non-empty `days` array.

- [ ] **Step 7: Generate the contribution graph**

Run:

```bash
python scripts/render_heatmap_svg.py
```

Expected: `contrib-heatmap.svg` is created and contains a cell for each item in `data/contributions.json`.

- [ ] **Step 8: Verify generated files are valid XML**

Run:

```bash
python - <<'PY'
from pathlib import Path
import xml.etree.ElementTree as ET

for name in ("avi-ascii.svg", "info-card.svg", "contrib-heatmap.svg"):
    ET.fromstring(Path(name).read_text(encoding="utf-8"))
    print(f"valid: {name}")
PY
```

Expected:

```text
valid: avi-ascii.svg
valid: info-card.svg
valid: contrib-heatmap.svg
```

- [ ] **Step 9: Confirm portrait source files are not tracked**

Run:

```bash
git status --short
git ls-files | grep -Ei 'source-(photo|prepped)|\.(jpg|jpeg|png)$' && exit 1 || true
```

Expected: only generated SVG/JSON files appear; no portrait image is tracked.

- [ ] **Step 10: Commit**

```bash
git add avi-ascii.svg info-card.svg contrib-heatmap.svg data/contributions.json
git commit -m "feat: add generated profile artwork"
```

---

### Task 8: Daily GitHub Actions Refresh

**Files:**
- Create: `.github/workflows/update-profile-art.yml`
- Create: `tests/test_workflow_contract.py`

**Interfaces:**
- Consumes: `scripts/requirements.txt`, `scripts/fetch_contributions.py`, and `scripts/render_heatmap_svg.py`.
- Produces: scheduled updates to `data/contributions.json` and `contrib-heatmap.svg`.
- Permission boundary: `contents: write` only.

- [ ] **Step 1: Write workflow contract tests**

Create `tests/test_workflow_contract.py`:

```python
from pathlib import Path


WORKFLOW = Path(".github/workflows/update-profile-art.yml")


def test_workflow_has_minimal_permissions_and_expected_triggers() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "contents: write" in text
    assert "workflow_dispatch:" in text
    assert "schedule:" in text
    assert "pull-requests: write" not in text
    assert "issues: write" not in text
    assert "id-token: write" not in text


def test_workflow_runs_only_expected_profile_scripts() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "GH_PROFILE_USER=deserveto python scripts/fetch_contributions.py" in text
    assert "python scripts/render_heatmap_svg.py" in text
    assert "scripts/make_ascii_svg.py" not in text
    assert "scripts/make_info_card.py" not in text


def test_workflow_commits_only_contribution_outputs() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "git add data/contributions.json contrib-heatmap.svg" in text
    assert "git add -A" not in text
```

- [ ] **Step 2: Run workflow tests and verify failure**

Run:

```bash
python -m pytest tests/test_workflow_contract.py -v
```

Expected: all tests fail because the workflow file does not exist.

- [ ] **Step 3: Create the workflow**

Create `.github/workflows/update-profile-art.yml`:

```yaml
name: Update profile contributions

on:
  workflow_dispatch:
  schedule:
    - cron: "17 0 * * *"

permissions:
  contents: write

concurrency:
  group: profile-contribution-refresh
  cancel-in-progress: true

jobs:
  refresh:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: scripts/requirements.txt

      - name: Install runtime dependencies
        run: python -m pip install -r scripts/requirements.txt

      - name: Fetch public contribution data
        run: GH_PROFILE_USER=deserveto python scripts/fetch_contributions.py

      - name: Render contribution graph
        run: python scripts/render_heatmap_svg.py

      - name: Commit changed contribution assets
        shell: bash
        run: |
          if git diff --quiet -- data/contributions.json contrib-heatmap.svg; then
            echo "No contribution changes to commit."
            exit 0
          fi

          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/contributions.json contrib-heatmap.svg
          git commit -m "chore: refresh contribution graph"
          git push
```

- [ ] **Step 4: Run workflow contract tests**

Run:

```bash
python -m pytest tests/test_workflow_contract.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/update-profile-art.yml tests/test_workflow_contract.py
git commit -m "ci: refresh profile contributions daily"
```

---

### Task 9: Repository Security Verifier

**Files:**
- Create: `scripts/verify_profile.py`
- Create: `tests/test_verify_profile.py`

**Interfaces:**
- Consumes: a repository root path.
- Produces:
  - `verify_svg(path: Path) -> list[str]`
  - `verify_repository(root: Path) -> list[str]`
  - command exit code `0` on success and `1` on violations.

- [ ] **Step 1: Write verifier tests**

Create `tests/test_verify_profile.py`:

```python
from pathlib import Path

from scripts.verify_profile import verify_repository, verify_svg


SAFE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg">'
    '<rect width="10" height="10"/>'
    "</svg>"
)


def test_verify_svg_accepts_safe_static_content(tmp_path: Path) -> None:
    path = tmp_path / "safe.svg"
    path.write_text(SAFE_SVG, encoding="utf-8")
    assert verify_svg(path) == []


def test_verify_svg_rejects_script_remote_href_and_event_handler(
    tmp_path: Path,
) -> None:
    path = tmp_path / "unsafe.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<script>alert(1)</script>'
        '<image href="https://example.com/a.png" onload="x()"/>'
        "</svg>",
        encoding="utf-8",
    )
    errors = verify_svg(path)
    assert any("script" in error.lower() for error in errors)
    assert any("remote href" in error.lower() for error in errors)
    assert any("event-handler" in error.lower() for error in errors)


def test_verify_repository_rejects_portrait_source(tmp_path: Path) -> None:
    for required in (
        "README.md",
        "avi-ascii.svg",
        "info-card.svg",
        "contrib-heatmap.svg",
    ):
        path = tmp_path / required
        path.write_text(
            SAFE_SVG if required.endswith(".svg") else "# Profile",
            encoding="utf-8",
        )
    (tmp_path / "source-photo.jpg").write_bytes(b"not-an-image")
    errors = verify_repository(tmp_path)
    assert any("source-photo.jpg" in error for error in errors)
```

- [ ] **Step 2: Run verifier tests and verify failure**

Run:

```bash
python -m pytest tests/test_verify_profile.py -v
```

Expected: collection fails because `scripts.verify_profile` does not exist.

- [ ] **Step 3: Implement the verifier**

Create `scripts/verify_profile.py`:

```python
#!/usr/bin/env python3
"""Verify profile repository safety, privacy, and required artifacts."""

from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

REQUIRED_FILES = (
    "README.md",
    "avi-ascii.svg",
    "info-card.svg",
    "contrib-heatmap.svg",
    "data/contributions.json",
)
FORBIDDEN_NAMES = (
    "source-photo.jpg",
    "source-photo.jpeg",
    "source-photo.png",
    "source-prepped.png",
    ".env",
    "id_rsa",
    "id_ed25519",
)
README_FORBIDDEN_TEXT = (
    "YOUR_NAME",
    "YOURHANDLE",
    "yoursite.com",
    "Avi Vashishta",
)


def verify_svg(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return [f"{path}: invalid XML: {exc}"]

    for element in root.iter():
        local_tag = element.tag.split("}")[-1].lower()
        if local_tag == "script":
            errors.append(f"{path}: script elements are forbidden")
        if local_tag == "foreignobject":
            errors.append(f"{path}: foreignObject is forbidden")

        for attribute, value in element.attrib.items():
            local_attribute = attribute.split("}")[-1].lower()
            if local_attribute.startswith("on"):
                errors.append(
                    f"{path}: event-handler attribute {attribute} is forbidden"
                )
            if local_attribute in {"href", "src"} and value.startswith(
                ("http://", "https://", "//")
            ):
                errors.append(f"{path}: remote href/src is forbidden")

    return errors


def verify_repository(root: Path) -> list[str]:
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"Missing required file: {relative}")

    for path in root.rglob("*"):
        if path.is_file() and path.name in FORBIDDEN_NAMES:
            errors.append(f"Forbidden private file: {path.relative_to(root)}")

    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        for forbidden in README_FORBIDDEN_TEXT:
            if forbidden in text:
                errors.append(
                    f"README.md contains template text: {forbidden}"
                )

    for name in ("avi-ascii.svg", "info-card.svg", "contrib-heatmap.svg"):
        path = root / name
        if path.is_file():
            errors.extend(verify_svg(path))

    return errors


def main() -> int:
    root = Path.cwd()
    errors = verify_repository(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Profile repository verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run verifier tests**

Run:

```bash
python -m pytest tests/test_verify_profile.py -v
```

Expected: `3 passed`.

- [ ] **Step 5: Run the verifier against the real repository**

Run:

```bash
python scripts/verify_profile.py
```

Expected:

```text
Profile repository verification passed.
```

- [ ] **Step 6: Commit**

```bash
git add scripts/verify_profile.py tests/test_verify_profile.py
git commit -m "test: add profile privacy and SVG safety checks"
```

---

### Task 10: Documentation, Full Verification, and Publication

**Files:**
- Create: `docs/superpowers/specs/2026-07-11-github-profile-design.md`
- Create: `docs/superpowers/plans/2026-07-11-github-profile-implementation.md`
- Verify: all repository files.

**Interfaces:**
- Consumes: the approved design document and this implementation plan.
- Produces: a documented and published profile repository.

- [ ] **Step 1: Copy the approved design and plan into the repository**

Run:

```bash
mkdir -p docs/superpowers/specs docs/superpowers/plans
cp /mnt/data/2026-07-11-github-profile-design.md \
  docs/superpowers/specs/2026-07-11-github-profile-design.md
cp /mnt/data/2026-07-11-github-profile-implementation.md \
  docs/superpowers/plans/2026-07-11-github-profile-implementation.md
```

Expected: both documents exist under `docs/superpowers/`.

- [ ] **Step 2: Run the complete automated test suite**

Run:

```bash
python -m pytest -v
```

Expected: all tests pass.

- [ ] **Step 3: Compile every Python module**

Run:

```bash
python -m compileall -q scripts tests
```

Expected: command exits with status `0` and prints no syntax errors.

- [ ] **Step 4: Run repository safety verification**

Run:

```bash
python scripts/verify_profile.py
```

Expected:

```text
Profile repository verification passed.
```

- [ ] **Step 5: Review the final Git diff**

Run:

```bash
git status --short
git diff --check
git diff --stat
```

Expected:
- `git diff --check` prints nothing.
- No source portrait or intermediate PNG appears.
- The workflow modifies only contribution JSON and SVG files.
- The README links match the approved destinations.

- [ ] **Step 6: Commit documentation**

```bash
git add docs/superpowers
git commit -m "docs: add profile design and implementation plan"
```

- [ ] **Step 7: Push the complete profile**

Run:

```bash
git push origin main
```

Expected: the push succeeds and `https://github.com/deserveto` renders the new profile README.

- [ ] **Step 8: Enable and manually run the reviewed workflow**

In GitHub:

```text
deserveto/deserveto
→ Settings
→ Actions
→ General
→ Workflow permissions
→ Read and write permissions
→ Save

Actions
→ Update profile contributions
→ Run workflow
```

Expected:
- The run succeeds.
- It changes only `data/contributions.json` and `contrib-heatmap.svg`.
- A second run with unchanged public data creates no commit.

- [ ] **Step 9: Final visual review**

Check the profile page at desktop width and a narrow mobile width.

Acceptance checks:

```text
- Portrait and information card align without obvious height mismatch.
- The portrait is recognizable and the original photo is not in the repository.
- Both animations play once and settle into readable final states.
- Featured-project text is complete and links work.
- PhishGNN-EEF and Azure VM Portfolio appear without fabricated links.
- The grayscale styling is restrained and professional.
- LinkedIn and Instagram links open the approved profiles.
- The contribution graph remains readable.
```

- [ ] **Step 10: Record the final verification commit if adjustments were needed**

```bash
git add README.md avi-ascii.svg info-card.svg contrib-heatmap.svg
git commit -m "fix: refine final profile presentation"
git push origin main
```

Expected: skip this commit when the visual review requires no adjustment.

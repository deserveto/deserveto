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
    assert compute_current_streak(days) == (2, "2026-07-08", "2026-07-09")


def test_longest_streak() -> None:
    days = [
        {"date": "2026-07-05", "count": 1},
        {"date": "2026-07-06", "count": 1},
        {"date": "2026-07-07", "count": 0},
        {"date": "2026-07-08", "count": 2},
    ]
    assert compute_longest_streak(days) == (2, "2026-07-05", "2026-07-06")


def test_build_data_is_deterministic() -> None:
    days = parse_contribution_days(SAMPLE_HTML)
    data = build_data(days, username="deserveto", generated_at="2026-07-11T00:00:00Z")
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
    assert json.loads(output.read_text(encoding="utf-8")) == {"username": "deserveto"}

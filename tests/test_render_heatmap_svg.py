import xml.etree.ElementTree as ET

import pytest

from scripts.render_heatmap_svg import build_grid, level_for, render, validate_data


def sample_data() -> dict[str, object]:
    return {
        "username": "deserveto",
        "generated_at": "2026-07-11T00:00:00Z",
        "range": {"start": "2026-07-05", "end": "2026-07-11"},
        "total_contributions": 12,
        "active_days": 4,
        "avg_per_active_day": 3.0,
        "current_streak": {"length": 2, "start": "2026-07-10", "end": "2026-07-11"},
        "longest_streak": {"length": 2, "start": "2026-07-10", "end": "2026-07-11"},
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


@pytest.mark.parametrize(("count", "expected"), [(0, 0), (1, 1), (5, 1), (6, 2), (15, 2), (16, 3), (31, 4), (51, 5)])
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

def test_bootstrap_data_is_labeled_without_claiming_full_year_total() -> None:
    data = sample_data()
    data["bootstrap_note"] = "Recent public commit seed; run workflow for full data"
    svg = render(data)
    assert "Recent public commit seed; run workflow for full data" in svg
    assert "contributions in the last year" not in svg

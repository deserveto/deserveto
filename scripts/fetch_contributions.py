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

if __package__ in (None, ""):
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
        tooltip = soup.find("tool-tip", attrs={"for": tooltip_id}) if tooltip_id else None
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


def compute_current_streak(days: list[dict[str, str | int]]) -> tuple[int, str | None, str | None]:
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
    return streak, str(days[start_index]["date"]), str(days[end_index]["date"])


def compute_longest_streak(days: list[dict[str, str | int]]) -> tuple[int, str | None, str | None]:
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


def build_data(days: list[dict[str, str | int]], username: str, generated_at: str | None = None) -> dict[str, Any]:
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
    timestamp = generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "username": username,
        "generated_at": timestamp,
        "range": {"start": str(days[0]["date"]), "end": str(days[-1]["date"])},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": current[0], "start": current[1], "end": current[2]},
        "longest_streak": {"length": longest[0], "start": longest[1], "end": longest[2]},
        "best_day": {"date": str(best["date"]), "count": int(best["count"])},
        "monthly": [{"month": month, "total": total_count} for month, total_count in sorted(monthly.items())],
        "days": days,
    }


def fetch_contribution_html(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(url, headers={"User-Agent": "deserveto-profile-readme/1.0"}, timeout=30)
    response.raise_for_status()
    return response.text


def write_data(data: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    username = os.environ.get("GH_PROFILE_USER", PROFILE_HOST)
    html_text = fetch_contribution_html(username)
    days = parse_contribution_days(html_text)
    data = build_data(days, username=username)
    write_data(data, DEFAULT_OUTPUT)
    print(f"Wrote {DEFAULT_OUTPUT}: {data['total_contributions']} contributions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

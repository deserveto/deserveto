#!/usr/bin/env python3
"""Render normalized contribution data as a safe monochrome SVG."""
from __future__ import annotations
from datetime import date
import html
import json
from pathlib import Path
from typing import Any
if __package__ in (None, ""):
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.profile_config import PROFILE_HOST

ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = ROOT / "data" / "contributions.json"
OUTPUT_PATH = ROOT / "contrib-heatmap.svg"
PALETTE = ("#161b22", "#30363d", "#484f58", "#6e7681", "#8b949e", "#f0f6fc")
CELL, GAP, STEP, PAD = 12, 3, 15, 22
LEFT_LABEL_WIDTH, TOP_LABEL_HEIGHT, TITLEBAR_HEIGHT = 30, 20, 30
BACKGROUND, BACKGROUND_TOP, FRAME = "#0d1117", "#161b22", "#30363d"
MUTED, TEXT = "#8b949e", "#f0f6fc"
DOTS = ("#8b949e", "#6e7681", "#484f58")
COLUMN_DELAY, ROW_DELAY, CELL_DURATION = 0.018, 0.045, 0.42


def level_for(count: int) -> int:
    if count <= 0: return 0
    if count <= 5: return 1
    if count <= 15: return 2
    if count <= 30: return 3
    if count <= 50: return 4
    return 5


def build_grid(days: list[dict[str, str | int]]) -> list[list[tuple[str, int, int] | None]]:
    first = date.fromisoformat(str(days[0]["date"]))
    column: list[tuple[str, int, int] | None] = [None] * ((first.weekday() + 1) % 7)
    grid: list[list[tuple[str, int, int] | None]] = []
    for item in days:
        current = date.fromisoformat(str(item["date"]))
        weekday = (current.weekday() + 1) % 7
        while len(column) < weekday:
            column.append(None)
        count = int(item["count"])
        column.append((str(item["date"]), count, level_for(count)))
        if len(column) == 7:
            grid.append(column); column = []
    if column:
        column.extend([None] * (7 - len(column))); grid.append(column)
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
    grid = build_grid(data["days"])
    columns = len(grid)
    art_width, art_height = columns * STEP, 7 * STEP
    width = PAD + LEFT_LABEL_WIDTH + art_width + PAD
    stats_height = 88
    height = TITLEBAR_HEIGHT + TOP_LABEL_HEIGHT + art_height + stats_height + PAD
    css = ("@keyframes cell{0%{opacity:0;transform:translateY(-6px)}"
           "100%{opacity:1;transform:translateY(0)}}"
           f".c{{opacity:0;animation:cell {CELL_DURATION:.2f}s cubic-bezier(.2,.8,.2,1) both}}")
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" data-summary="{int(data["total_contributions"])} contributions" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
         f'<style>{css}</style>',
         f'<defs><linearGradient id="background" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BACKGROUND_TOP}"/><stop offset="1" stop-color="{BACKGROUND}"/></linearGradient></defs>',
         f'<rect width="{width}" height="{height}" rx="12" fill="url(#background)"/>',
         f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{FRAME}"/>',
         f'<line x1="0" y1="{TITLEBAR_HEIGHT}" x2="{width}" y2="{TITLEBAR_HEIGHT}" stroke="{FRAME}"/>']
    for i, color in enumerate(DOTS):
        p.append(f'<circle cx="{PAD+i*16}" cy="{TITLEBAR_HEIGHT/2}" r="5" fill="{color}"/>')
    p.append(f'<text x="{width/2}" y="{TITLEBAR_HEIGHT/2+4}" fill="{MUTED}" font-size="12" text-anchor="middle">{html.escape(PROFILE_HOST)}@github: contributions</text>')
    top, left = TITLEBAR_HEIGHT + TOP_LABEL_HEIGHT, PAD + LEFT_LABEL_WIDTH
    seen: set[tuple[int,int]] = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None: continue
            d = date.fromisoformat(cell[0]); key = (d.year,d.month)
            if key not in seen and d.day <= 7:
                seen.add(key); p.append(f'<text x="{left+ci*STEP}" y="{TITLEBAR_HEIGHT+14}" fill="{MUTED}" font-size="10">{d.strftime("%b")}</text>')
            break
    for ri, label in ((1,"Mon"),(3,"Wed"),(5,"Fri")):
        y = top + ri*STEP + CELL*0.78
        p.append(f'<text x="{PAD}" y="{y:.1f}" fill="{MUTED}" font-size="9">{label}</text>')
    for ci, column in enumerate(grid):
        for ri, cell in enumerate(column):
            if cell is None: continue
            date_text,count,lvl = cell; x=left+ci*STEP; y=top+ri*STEP
            delay=ci*COLUMN_DELAY+ri*ROW_DELAY; noun="contribution" if count==1 else "contributions"
            p.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s"><title>{html.escape(date_text)}: {count} {noun}</title></rect>')
    leg_y=top+art_height+6; leg_x=width-PAD-(len(PALETTE)*(CELL-1)+70)
    p.append(f'<text x="{leg_x}" y="{leg_y+CELL*0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    lx=leg_x+8
    for color in PALETTE:
        p.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL-1}" height="{CELL-1}" rx="2.2" fill="{color}"/>'); lx += CELL
    p.append(f'<text x="{lx+4}" y="{leg_y+CELL*0.8:.1f}" fill="{MUTED}" font-size="10">More</text>')
    sep=leg_y+CELL+14; p.append(f'<line x1="0" y1="{sep}" x2="{width}" y2="{sep}" stroke="{FRAME}"/>')
    total=int(data["total_contributions"]); cs=int(data["current_streak"]["length"]); ls=int(data["longest_streak"]["length"]); best=data["best_day"]; rng=data["range"]
    y=sep+24
    p.append(f'<text x="{PAD}" y="{y}" font-size="13" fill="{TEXT}"><tspan font-weight="700">{total:,}</tspan><tspan fill="{MUTED}"> contributions in the last year</tspan></text>')
    p.append(f'<text x="{width-PAD}" y="{y}" font-size="12" fill="{MUTED}" text-anchor="end">{rng["start"]} &#8594; {rng["end"]}</text>')
    y += 24
    p.append(f'<text x="{PAD}" y="{y}" font-size="13" fill="{MUTED}">current streak <tspan fill="{TEXT}" font-weight="700">{cs} days</tspan><tspan>   &#183;   longest </tspan><tspan fill="{TEXT}" font-weight="700">{ls} days</tspan></text>')
    p.append(f'<text x="{width-PAD}" y="{y}" font-size="12" fill="{MUTED}" text-anchor="end">best day <tspan fill="{TEXT}" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>')
    p.append('</svg>')
    return ''.join(p)


def write_svg(svg: str, output_path: Path) -> None:
    output_path.write_text(svg + "\n", encoding="utf-8")


def main() -> int:
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    svg = render(data); write_svg(svg, OUTPUT_PATH)
    print(f"Wrote {OUTPUT_PATH} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

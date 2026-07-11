#!/usr/bin/env python3
"""Render the approved profile facts as a matching animated SVG card."""
from __future__ import annotations
import html, os
from pathlib import Path
from scripts.profile_config import INFO_CARD_ROWS, PROFILE_HOST
ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "info-card.svg"
WIDTH, HEIGHT, PAD, TITLEBAR_HEIGHT, LINE_HEIGHT = 480, 376, 20, 30, 20.5
KEY_X, VALUE_X = PAD, PAD + 92
BACKGROUND, BACKGROUND_TOP, FRAME = "#0d1117", "#161b22", "#30363d"
MUTED, TEXT, KEY, SECTION = "#8b949e", "#f0f6fc", "#c9d1d9", "#8b949e"
DOTS = ("#8b949e", "#6e7681", "#484f58")


def animated_group(inner: str, index: int, static: bool) -> str:
    if static:
        return f"<g>{inner}</g>"
    delay = 0.15 + index * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


def render_info_card(host: str, rows: tuple[tuple[str, ...], ...], static: bool = False) -> str:
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
       f'<defs><linearGradient id="background" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BACKGROUND_TOP}"/><stop offset="1" stop-color="{BACKGROUND}"/></linearGradient></defs>',
       f'<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#background)"/>',
       f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="12" fill="none" stroke="{FRAME}"/>',
       f'<line x1="0" y1="{TITLEBAR_HEIGHT}" x2="{WIDTH}" y2="{TITLEBAR_HEIGHT}" stroke="{FRAME}"/>']
    for i,c in enumerate(DOTS): p.append(f'<circle cx="{PAD+i*16}" cy="{TITLEBAR_HEIGHT/2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{WIDTH/2}" y="{TITLEBAR_HEIGHT/2+4}" fill="{MUTED}" font-size="12" text-anchor="middle">{html.escape(host)}@github: profile</text>')
    y=TITLEBAR_HEIGHT+30
    for i,row in enumerate(rows):
        kind=row[0]
        if kind=="gap": y += LINE_HEIGHT*0.5; continue
        if kind=="host":
            rule_x=KEY_X+(len(host)+7)*8+8
            inner=f'<text x="{KEY_X}" y="{y:.1f}" fill="{TEXT}" font-size="14" font-weight="700">{html.escape(host)}@github</text><line x1="{rule_x}" y1="{y-4:.1f}" x2="{WIDTH-PAD}" y2="{y-4:.1f}" stroke="{FRAME}"/>'
        elif kind=="sec":
            title=html.escape(row[1]); inner=f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">&#8212; {title}</text><line x1="{KEY_X+12+len(row[1])*8}" y1="{y-4:.1f}" x2="{WIDTH-PAD}" y2="{y-4:.1f}" stroke="{FRAME}"/>'
        elif kind=="kv":
            inner=f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{html.escape(row[1])}</text><text x="{VALUE_X}" y="{y:.1f}" fill="{TEXT}" font-size="12.5">{html.escape(row[2])}</text>'
        elif kind=="bul":
            inner=f'<circle cx="{KEY_X+3}" cy="{y-4:.1f}" r="2.5" fill="{KEY}"/><text x="{KEY_X+14}" y="{y:.1f}" fill="{TEXT}" font-size="12.5">{html.escape(row[1])}</text>'
        else: raise ValueError(f"Unsupported row kind: {kind}")
        p.append(animated_group(inner,i,static)); y += LINE_HEIGHT
    if y > HEIGHT-12: raise ValueError(f"Information-card content exceeds the {HEIGHT}px canvas")
    p.append('</svg>'); return ''.join(p)


def write_svg(svg: str, output_path: Path) -> None: output_path.write_text(svg+'\n', encoding='utf-8')
def main() -> int:
    svg=render_info_card(PROFILE_HOST, INFO_CARD_ROWS, static=bool(os.environ.get('STATIC'))); write_svg(svg,OUTPUT_PATH); print(f"Wrote {OUTPUT_PATH} ({len(svg)} bytes)"); return 0
if __name__=='__main__': raise SystemExit(main())

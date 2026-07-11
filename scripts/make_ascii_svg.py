#!/usr/bin/env python3
"""Convert a local portrait into an animated monochrome ASCII SVG."""
from __future__ import annotations
import html, os, sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
if __package__ in (None, ""):
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.profile_config import PROFILE_HOST, PROFILE_NAME
RAMP = " .`:-=+*cs#%@"
DEFAULT_COLUMNS, DEFAULT_ROWS = 80, 42
CELL_WIDTH, CELL_HEIGHT = 8, 15
CONTRAST, BRIGHTNESS, GAMMA, WHITE_FLOOR = 1.18, 1.0, 1.12, 0.92
PAD, TITLEBAR_HEIGHT, STATUS_HEIGHT = 20, 30, 30
BACKGROUND, BACKGROUND_TOP, FRAME = "#0d1117", "#161b22", "#30363d"
MUTED, TEXT = "#8b949e", "#f0f6fc"
DOTS = ("#8b949e", "#6e7681", "#484f58")
ROW_DURATION, ROW_STAGGER = 0.10, 0.075


def image_to_ascii_rows(image: Image.Image, cols: int = DEFAULT_COLUMNS, rows: int = DEFAULT_ROWS) -> list[str]:
    grayscale = ImageOps.autocontrast(image.convert("L"), cutoff=1)
    grayscale = ImageEnhance.Brightness(grayscale).enhance(BRIGHTNESS)
    grayscale = ImageEnhance.Contrast(grayscale).enhance(CONTRAST)
    grayscale = grayscale.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = grayscale.load(); output=[]
    for y in range(rows):
        chars=[]
        for x in range(cols):
            luminance = pow(float(pixels[x,y])/255.0, GAMMA)
            if luminance >= WHITE_FLOOR: chars.append(" "); continue
            index = max(0, min(len(RAMP)-1, int((1.0-luminance)*(len(RAMP)-1)+0.5)))
            chars.append(RAMP[index])
        output.append(''.join(chars))
    return output


def render_ascii_svg(rows: list[str], host: str, display_name: str, static: bool = False) -> str:
    if not rows or not rows[0]: raise ValueError("ASCII rows must be non-empty")
    if any(len(row)!=len(rows[0]) for row in rows): raise ValueError("All ASCII rows must have the same width")
    columns,row_count=len(rows[0]),len(rows); art_width=columns*CELL_WIDTH; art_height=row_count*CELL_HEIGHT
    width=art_width+PAD*2; height=TITLEBAR_HEIGHT+art_height+STATUS_HEIGHT+PAD; art_top=TITLEBAR_HEIGHT+PAD*0.35
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
       f'<defs><linearGradient id="background" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BACKGROUND_TOP}"/><stop offset="1" stop-color="{BACKGROUND}"/></linearGradient></defs>',
       f'<rect width="{width}" height="{height}" rx="12" fill="url(#background)"/>',
       f'<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="12" fill="none" stroke="{FRAME}"/>',
       f'<line x1="0" y1="{TITLEBAR_HEIGHT}" x2="{width}" y2="{TITLEBAR_HEIGHT}" stroke="{FRAME}"/>']
    for i,c in enumerate(DOTS): p.append(f'<circle cx="{PAD+i*16}" cy="{TITLEBAR_HEIGHT/2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{width/2}" y="{TITLEBAR_HEIGHT/2+4}" fill="{MUTED}" font-size="12" text-anchor="middle">{html.escape(host)}@github: portrait</text>')
    font_size=CELL_HEIGHT*0.86
    for i,line in enumerate(rows):
        y=art_top+i*CELL_HEIGHT+CELL_HEIGHT*0.74; row_y=art_top+i*CELL_HEIGHT; delay=i*ROW_STAGGER
        text=f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{TEXT}" font-size="{font_size:.1f}" textLength="{art_width}" lengthAdjust="spacing">{html.escape(line)}</text>'
        if static: p.append(text); continue
        p.append(f'<clipPath id="row-{i}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_HEIGHT}" width="0"><animate attributeName="width" from="0" to="{art_width}" begin="{delay:.3f}s" dur="{ROW_DURATION:.2f}s" fill="freeze"/></rect></clipPath>')
        p.append(f'<g clip-path="url(#row-{i})">{text}</g>')
    status_line_y=TITLEBAR_HEIGHT+art_height+PAD*0.35; status_y=status_line_y+19
    p.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{width}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
    p.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{MUTED}" font-size="13">{html.escape(host)}@github:~$ whoami <tspan fill="{TEXT}">{html.escape(display_name)}</tspan></text>')
    p.append(f'<rect x="{PAD+284}" y="{status_y-12:.1f}" width="8" height="14" fill="{TEXT}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')
    p.append('</svg>'); return ''.join(p)


def generate(input_path: Path, output_path: Path, static: bool=False) -> None:
    with Image.open(input_path) as image: rows=image_to_ascii_rows(image)
    output_path.write_text(render_ascii_svg(rows, PROFILE_HOST, PROFILE_NAME, static)+'\n', encoding='utf-8')

def main(argv: list[str] | None=None) -> int:
    args=argv if argv is not None else sys.argv[1:]
    if not args: raise SystemExit("Usage: python scripts/make_ascii_svg.py <image> [output.svg]")
    generate(Path(args[0]), Path(args[1]) if len(args)>1 else Path('avi-ascii.svg'), static=bool(os.environ.get('STATIC')))
    return 0
if __name__=='__main__': raise SystemExit(main())

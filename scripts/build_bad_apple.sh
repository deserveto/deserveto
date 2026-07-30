#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INPUT="${1:-}"
OUTPUT="${2:-$ROOT/assets/bad-apple-lua.gif}"
FPS="${FPS:-10}"
COLS=76
ROWS=40

if [[ -z "$INPUT" || ! -f "$INPUT" ]]; then
  echo "Usage: $0 /path/to/bad-apple.mp4 [output.gif]" >&2
  exit 2
fi
for command in ffmpeg luatex; do
  command -v "$command" >/dev/null 2>&1 || { echo "Missing required command: $command" >&2; exit 3; }
done
mkdir -p "$(dirname "$OUTPUT")"
TMP="${OUTPUT%.gif}.tmp.gif"
rm -f "$TMP"

ffmpeg -hide_banner -loglevel error -i "$INPUT" -an \
  -vf "fps=$FPS,scale=${COLS}:${ROWS}:flags=lanczos,format=gray" \
  -f rawvideo -pix_fmt gray - \
| luatex --luaonly "$ROOT/bad_apple.lua" "$COLS" "$ROWS" "$FPS" \
| ffmpeg -hide_banner -loglevel error \
  -f image2pipe -framerate "$FPS" -vcodec pgm -i - \
  -an -vf "format=rgb8" -loop 0 -gifflags +transdiff "$TMP"

mv "$TMP" "$OUTPUT"
BYTES=$(wc -c < "$OUTPUT")
MIB=$(python - "$BYTES" <<'PY'
import sys
print(f"{int(sys.argv[1]) / 1024 / 1024:.2f}")
PY
)
echo "Created $OUTPUT ($MIB MiB)"
if (( BYTES >= 100 * 1024 * 1024 )); then
  echo "ERROR: GIF exceeds GitHub's 100 MiB limit. Re-run with FPS=6." >&2
  exit 4
fi

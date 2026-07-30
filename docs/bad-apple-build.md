# Bad Apple Lua-Style README Build

The profile animation is a silent, full-length GIF generated from a locally supplied video. The original video is intentionally excluded from Git.

## Requirements

- FFmpeg 6 or newer
- LuaTeX (`luatex --luaonly`) or a compatible Lua 5.3+ launcher
- Bash on Linux/macOS, or PowerShell on Windows

## Linux/macOS

```bash
./scripts/build_bad_apple.sh "/path/to/Bad Apple.mp4"
```

To reduce size:

```bash
FPS=6 ./scripts/build_bad_apple.sh "/path/to/Bad Apple.mp4"
```

## Windows PowerShell

```powershell
./scripts/build_bad_apple.ps1 -InputVideo "C:\path\to\Bad Apple.mp4"
```

Use `-Fps 6` when the generated file is too large.

## Output contract

The renderer creates `assets/bad-apple-lua.gif` at 480×360, loops indefinitely, has no audio, and must remain below GitHub's 100 MiB single-file limit.

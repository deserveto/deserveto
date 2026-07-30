# Bad Apple Lua-Style README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the profile README with a reproducible full-length Lua-style Bad Apple GIF.

**Architecture:** FFmpeg downsamples the legal local MP4 to 76×40 grayscale frames. `bad_apple.lua` maps each pixel to a 5×7 terminal glyph and streams 480×360 PGM frames to FFmpeg, which writes the looping GIF.

**Tech Stack:** Lua 5.3+/LuaTeX, FFmpeg, Bash, PowerShell, Python, pytest, Pillow.

## Global Constraints

- The README contains only the full-width animation.
- The animation is silent, full-length, 480×360, and loops indefinitely.
- The committed GIF remains below 100 MiB.
- The original MP4 is never committed.

---

### Task 1: Renderer and build pipeline

**Files:** `bad_apple.lua`, `scripts/build_bad_apple.sh`, `scripts/build_bad_apple.ps1`

- [x] Stream grayscale source frames into Lua.
- [x] Map brightness to fixed terminal glyphs.
- [x] Emit PGM frames and encode a looping GIF.
- [x] Fail clearly for missing tools, missing input, or oversized output.

### Task 2: README takeover and documentation

**Files:** `README.md`, `.gitignore`, `docs/bad-apple-build.md`

- [x] Replace visible README content with the GIF embed.
- [x] Exclude source videos and temporary GIFs.
- [x] Document Linux/macOS and Windows build commands.

### Task 3: Contract tests and verification

**Files:** `tests/test_readme_contract.py`, `tests/test_bad_apple_assets.py`, `tests/test_verify_profile.py`, `scripts/verify_profile.py`

- [x] Verify takeover markup and accessible alt text.
- [x] Verify GIF dimensions, animation, loop, and size.
- [x] Verify all reproducibility files exist.

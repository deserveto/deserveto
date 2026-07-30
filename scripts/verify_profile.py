#!/usr/bin/env python3
"""Verify the profile README takeover and committed animation asset."""
from __future__ import annotations
from pathlib import Path
import sys

REQUIRED_FILES = (
    "README.md",
    "assets/bad-apple-lua.gif",
    "bad_apple.lua",
    "scripts/build_bad_apple.sh",
    "scripts/build_bad_apple.ps1",
    "docs/bad-apple-build.md",
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
    "## About Me",
    "## Featured Projects",
    "## Technology Stack",
    "## Contact",
)


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
        if './assets/bad-apple-lua.gif' not in text:
            errors.append("README.md does not reference the Bad Apple GIF")
        for forbidden in README_FORBIDDEN_TEXT:
            if forbidden in text:
                errors.append(f"README.md contains forbidden text: {forbidden}")
    gif = root / "assets/bad-apple-lua.gif"
    if gif.is_file() and gif.stat().st_size >= 100 * 1024 * 1024:
        errors.append("assets/bad-apple-lua.gif exceeds GitHub's 100 MiB limit")
    return errors


def main() -> int:
    errors = verify_repository(Path.cwd())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Bad Apple profile verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from pathlib import Path
from scripts.verify_profile import verify_repository


def populate_required_files(root: Path) -> None:
    for relative in (
        "README.md",
        "assets/bad-apple-lua.gif",
        "bad_apple.lua",
        "scripts/build_bad_apple.sh",
        "scripts/build_bad_apple.ps1",
        "docs/bad-apple-build.md",
    ):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative == "README.md":
            path.write_text('<img src="./assets/bad-apple-lua.gif" />', encoding="utf-8")
        else:
            path.write_bytes(b"GIF89a" if relative.endswith(".gif") else b"placeholder")


def test_verify_repository_accepts_takeover_contract(tmp_path: Path) -> None:
    populate_required_files(tmp_path)
    assert verify_repository(tmp_path) == []


def test_verify_repository_rejects_missing_gif_reference(tmp_path: Path) -> None:
    populate_required_files(tmp_path)
    (tmp_path / "README.md").write_text("# Profile", encoding="utf-8")
    errors = verify_repository(tmp_path)
    assert any("does not reference" in error for error in errors)

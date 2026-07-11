from pathlib import Path
from scripts.verify_profile import verify_repository, verify_svg

SAFE_SVG = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>'

def test_verify_svg_accepts_safe_static_content(tmp_path: Path) -> None:
    path = tmp_path / "safe.svg"
    path.write_text(SAFE_SVG, encoding="utf-8")
    assert verify_svg(path) == []

def test_verify_svg_rejects_script_remote_href_and_event_handler(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.svg"
    path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script><image href="https://example.com/a.png" onload="x()"/></svg>', encoding="utf-8")
    errors = verify_svg(path)
    assert any("script" in error.lower() for error in errors)
    assert any("remote href" in error.lower() for error in errors)
    assert any("event-handler" in error.lower() for error in errors)

def test_verify_repository_rejects_portrait_source(tmp_path: Path) -> None:
    for required in ("README.md", "avi-ascii.svg", "info-card.svg", "contrib-heatmap.svg"):
        path = tmp_path / required
        path.write_text(SAFE_SVG if required.endswith(".svg") else "# Profile", encoding="utf-8")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "contributions.json").write_text("{}", encoding="utf-8")
    (tmp_path / "source-photo.jpg").write_bytes(b"not-an-image")
    errors = verify_repository(tmp_path)
    assert any("source-photo.jpg" in error for error in errors)

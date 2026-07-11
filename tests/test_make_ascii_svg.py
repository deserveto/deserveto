import xml.etree.ElementTree as ET
from PIL import Image
from scripts.make_ascii_svg import image_to_ascii_rows, render_ascii_svg


def test_image_to_ascii_rows_has_requested_dimensions() -> None:
    image = Image.new("L", (20, 20), color=64)
    rows = image_to_ascii_rows(image, cols=10, rows=4)
    assert len(rows) == 4
    assert all(len(row) == 10 for row in rows)


def test_white_pixels_become_spaces() -> None:
    image = Image.new("L", (4, 2), color=255)
    rows = image_to_ascii_rows(image, cols=4, rows=2)
    assert rows == ["    ", "    "]


def test_portrait_svg_uses_approved_identity_and_safe_animation() -> None:
    rows = [" .:-", "=+*#", "%@  "]
    svg = render_ascii_svg(rows, host="deserveto", display_name="Fikri Tri Wibowo", static=False)
    ET.fromstring(svg)
    assert "deserveto@github" in svg
    assert "Fikri Tri Wibowo" in svg
    assert "Avi Vashishta" not in svg
    assert "<script" not in svg.lower()
    assert "foreignObject" not in svg
    assert "href=" not in svg
    assert "#ff5f56" not in svg
    assert "<animate " in svg

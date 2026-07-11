import xml.etree.ElementTree as ET
from scripts.make_info_card import render_info_card
from scripts.profile_config import INFO_CARD_ROWS, PROFILE_HOST


def test_info_card_contains_approved_content() -> None:
    svg = render_info_card(PROFILE_HOST, INFO_CARD_ROWS, static=True)
    ET.fromstring(svg)
    assert "deserveto@github" in svg
    assert "Information Technology Student" in svg
    assert "Telkom University" in svg
    assert "Phishing detection research with GNN" in svg
    assert "Avi Vashishta" not in svg
    assert "Your current role" not in svg


def test_info_card_is_safe_and_monochrome() -> None:
    svg = render_info_card(PROFILE_HOST, INFO_CARD_ROWS, static=False)
    assert "<script" not in svg.lower()
    assert "foreignObject" not in svg
    assert "href=" not in svg
    assert "#ffa657" not in svg
    assert "#58a6ff" not in svg
    assert "#22d3ee" not in svg
    assert "animateTransform" in svg

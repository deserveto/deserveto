from pathlib import Path
WORKFLOW = Path(".github/workflows/update-profile-art.yml")

def test_workflow_has_minimal_permissions_and_expected_triggers() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "contents: write" in text
    assert "workflow_dispatch:" in text
    assert "schedule:" in text
    assert "pull-requests: write" not in text
    assert "issues: write" not in text
    assert "id-token: write" not in text

def test_workflow_runs_only_expected_profile_scripts() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "GH_PROFILE_USER=deserveto python scripts/fetch_contributions.py" in text
    assert "python scripts/render_heatmap_svg.py" in text
    assert "scripts/make_ascii_svg.py" not in text
    assert "scripts/make_info_card.py" not in text

def test_workflow_commits_only_contribution_outputs() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "git add data/contributions.json contrib-heatmap.svg" in text
    assert "git add -A" not in text

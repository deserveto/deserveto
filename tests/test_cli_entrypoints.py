import subprocess
import sys
from pathlib import Path


def test_make_info_card_runs_as_a_direct_script(tmp_path: Path) -> None:
    script = Path.cwd() / "scripts" / "make_info_card.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (Path.cwd() / "info-card.svg").is_file()

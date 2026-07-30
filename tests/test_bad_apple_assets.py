import json
from pathlib import Path
import shutil
import subprocess

GIF_PATH = Path("assets/bad-apple-lua.gif")


def test_required_bad_apple_files_exist() -> None:
    for path in (
        Path("bad_apple.lua"),
        Path("scripts/build_bad_apple.sh"),
        Path("scripts/build_bad_apple.ps1"),
        Path("docs/bad-apple-build.md"),
        GIF_PATH,
    ):
        assert path.is_file(), f"Missing required file: {path}"


def test_gif_is_animated_full_size_and_under_github_limit() -> None:
    assert GIF_PATH.stat().st_size < 100 * 1024 * 1024
    assert shutil.which("ffprobe"), "ffprobe is required for animation verification"
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,nb_frames,r_frame_rate:format=duration",
            "-of",
            "json",
            str(GIF_PATH),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    stream = data["streams"][0]
    assert (stream["width"], stream["height"]) == (480, 360)
    assert int(stream["nb_frames"]) > 1000
    assert stream["r_frame_rate"] == "10/1"
    assert 219.0 <= float(data["format"]["duration"]) <= 219.2

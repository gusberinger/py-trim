from pathlib import Path
from packaging.version import parse as parse_version
import typer
import subprocess
import re
from .main import get_duration

TESTED_VERSION = "5.1.2"

app = typer.Typer()


def check_ffmpeg_version():
    """Check that ffmpeg is installed and is the correct version."""
    version_output = subprocess.run(
        ["ffmpeg", "-version"], capture_output=True, text=True
    ).stdout
    version = re.match(r"ffmpeg version (\d+\.\d+\.\d+)", version_output)
    if version is None:
        raise typer.BadParameter("FFmpeg is not installed.")

    version = parse_version(version.group(1))
    if version < parse_version(TESTED_VERSION):
        raise typer.warning(
            f"Tested with FFmpeg version {TESTED_VERSION}, but you have version {version}"
        )


@app.command()
def main(
    source_file: Path = typer.Argument(
        ...,
        help="The path to the video file that will be trimmed.",
        exists=True,
        dir_okay=False,
    ),
    from_time: str = typer.Argument(..., help=""),
    to_time: str = typer.Argument(..., help=""),
    dest_file: Path = typer.Argument(
        ...,
        help="The path that the trimmed video will be saved to.",
        dir_okay=False,
    ),
):
    from_duration = get_duration(from_time)
    to_duration = get_duration(to_time)
    if from_duration > to_duration:
        raise typer.BadParameter("Start time must be before end time.")

    commands = [
        "ffmpeg",
        "-ss",
        from_time,
        "-i",
        str(source_file.absolute()),
        "-t",
        f"{to_duration - from_duration:.4f}",
        "-async",
        "1",
        str(dest_file.absolute()),
    ]
    subprocess.run(commands)

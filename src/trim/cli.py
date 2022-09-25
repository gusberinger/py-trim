import argparse
import re
from pathlib import Path
import subprocess


HOUR_REGEX = r"(\d{1,2}):(\d{2}):(\d{2})(\.\d+)?"
MINUTES_REGEX = r"(\d{1,2}):(\d{2})(\.\d+)?"
SECONDS_REGEX = r"(\d{1,2})(\.\d+)?"
TIME_REGEX = r"\d{1,2}(?::\d{2}){0,2}(?:\.\d+)?"


class DurationParseError(Exception):
    """Timestamp incorrect."""


def convert_num(arg: str | None) -> float:
    """Utility function for get_duration"""
    if arg is None:
        return 0
    else:
        return float(arg)


def get_duration(arg_val: str) -> float:
    """
    Convert timestamp argument to duration (seconds).
    Used for validation of end_time > start_time.
    """
    if match := re.match(HOUR_REGEX, arg_val):
        hour, minute, second, millisec = map(convert_num, match.groups())
        if hour > 60 or minute > 60 or second > 60:
            raise DurationParseError(arg_val)
        millisec = 0 if millisec is None else millisec
        return hour * 60 * 60 + minute * 60 + second + millisec

    elif match := re.match(MINUTES_REGEX, arg_val):
        minute, second, millisec = map(convert_num, match.groups())
        if minute > 60 or second > 60:
            raise DurationParseError(arg_val)
        millisec = 0 if millisec is None else millisec
        return minute * 60 + second + millisec

    elif match := re.match(SECONDS_REGEX, arg_val):
        second, millisec = map(convert_num, match.groups())
        if second > 60:
            raise DurationParseError(arg_val)
        millisec = 0 if millisec is None else millisec
        return second + millisec

    else:
        raise DurationParseError(arg_val)


def parse(args=None):
    description = "A wrapper around ffmpeg to trim videos"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "source_file",
        type=Path,
        help="The path to the video file that will be trimmed.",
    )
    parser.add_argument(
        "start_time",
        type=str,
        help="The start time of the clip in the original video. Format: HH:MM:SS or MM:SS or SS",
    )
    parser.add_argument(
        "end_time",
        type=str,
        help="The end time of the clip in the orginal video. Format: HH:MM:SS or MM:SS or SS.",
    )
    parser.add_argument(
        "dest_file", type=Path, help="The path that the trimmed video will be saved to."
    )
    args = parser.parse_args(None)
    if get_duration(args.start_time) > get_duration(args.end_time):
        parser.error("The end_time must be after the start_time")
    if not args.source_file.exists():
        parser.error("The source file does not exist.")

    return args


def main():
    args = parse()
    commands = [
        "ffmpeg",
        "-i",
        str(args.source_file.absolute()),
        "-ss",
        args.start_time,
        "-to",
        args.end_time,
        "-async",
        "1",
        str(args.dest_file.absolute()),
    ]
    subprocess.run(commands)


if __name__ == "__main__":
    assert get_duration("22:45.2") == (22 * 60) + 45.2
    assert get_duration("22:45") == (22 * 60) + 45
    assert get_duration("22") == 22
    assert get_duration("22.9") == 22.9
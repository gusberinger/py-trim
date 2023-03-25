import re


HOUR_REGEX = r"(\d{1,2}):(\d{2}):(\d{2})(\.\d+)?"
MINUTES_REGEX = r"(\d{1,2}):(\d{2})(\.\d+)?"
SECONDS_REGEX = r"(\d{1,2})(\.\d+)?"
TIME_REGEX = r"\d{1,2}(?::\d{2}){0,2}(?:\.\d+)?"


class DurationParseError(Exception):
    """Timestamp incorrect."""


def convert_num(arg: str | None) -> float:
    """
    :param arg: String to convert to float.
    :return: Float value of arg or 0 if arg is None.
    """
    if arg is None:
        return 0
    else:
        return float(arg)


def get_duration(timestamp: str) -> float:
    """
    :param timestamp: Timestamp in format HH:MM:SS.MS where values can be ommited if it is still a valid timestamp.
    :return: Duration in seconds

    Convert timestamp argument to duration (seconds).
    Used for validation of end_time > start_time.
    """
    if match := re.match(HOUR_REGEX, timestamp):
        hour, minute, second, millisec = (convert_num(arg) for arg in match.groups())
        if hour > 60 or minute > 60 or second > 60:
            raise DurationParseError(timestamp)
        millisec = 0 if millisec is None else millisec
        return hour * 60 * 60 + minute * 60 + second + millisec

    elif match := re.match(MINUTES_REGEX, timestamp):
        minute, second, millisec = (convert_num(arg) for arg in match.groups())
        if minute > 60 or second > 60:
            raise DurationParseError(timestamp)
        millisec = 0 if millisec is None else millisec
        return minute * 60 + second + millisec

    elif match := re.match(SECONDS_REGEX, timestamp):
        second, millisec = (convert_num(arg) for arg in match.groups())
        if second > 60:
            raise DurationParseError(timestamp)
        millisec = 0 if millisec is None else millisec
        return second + millisec

    else:
        raise DurationParseError(timestamp)

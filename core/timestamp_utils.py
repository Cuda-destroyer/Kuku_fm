"""
Timestamp parsing, normalization, calculation, and formatting utilities.
Supports MM:SS.SS, (MM:SS.SS), HH:MM:SS.SS, and variations.
"""
import re
from typing import Union, Tuple, Optional


def clean_timestamp_string(raw: str) -> str:
    """Strips parentheses, whitespace, brackets from timestamp strings."""
    if not raw:
        return "00:00.00"
    cleaned = re.sub(r"[()\[\]\s]", "", str(raw))
    return cleaned


def parse_timestamp(ts: Union[str, float, int]) -> float:
    """
    Parses a timestamp string into float seconds.
    Supports formats:
    - MM:SS.SS (e.g. '01:23.45', '(00:11.30)')
    - HH:MM:SS.SS (e.g. '01:02:03.45')
    - MM:SS (e.g. '01:23')
    - Pure numbers / seconds (e.g. 75.4)
    """
    if isinstance(ts, (int, float)):
        return max(0.0, float(ts))

    cleaned = clean_timestamp_string(ts)

    # If it's already pure float / int
    try:
        return max(0.0, float(cleaned))
    except ValueError:
        pass

    # Split by colon
    parts = cleaned.split(":")
    if len(parts) == 1:
        try:
            return max(0.0, float(parts[0]))
        except ValueError:
            return 0.0
    elif len(parts) == 2:
        # MM:SS or MM:SS.SS
        try:
            minutes = float(parts[0])
            seconds = float(parts[1])
            return max(0.0, minutes * 60.0 + seconds)
        except ValueError:
            return 0.0
    elif len(parts) == 3:
        # HH:MM:SS or HH:MM:SS.SS
        try:
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            return max(0.0, hours * 3600.0 + minutes * 60.0 + seconds)
        except ValueError:
            return 0.0

    return 0.0


def format_seconds(seconds: float, include_ms: bool = True) -> str:
    """Formats numeric seconds into standard MM:SS.SS or HH:MM:SS.SS string."""
    seconds = max(0.0, float(seconds))
    hours = int(seconds // 3600)
    remainder = seconds % 3600
    minutes = int(remainder // 60)
    secs = remainder % 60

    if hours > 0:
        if include_ms:
            return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
        else:
            return f"{hours:02d}:{minutes:02d}:{int(secs):02d}"
    else:
        if include_ms:
            return f"{minutes:02d}:{secs:05.2f}"
        else:
            return f"{minutes:02d}:{int(secs):02d}"


def calculate_duration(start_ts: Union[str, float], end_ts: Union[str, float]) -> float:
    """Calculates duration in seconds between start and end timestamps."""
    start_sec = parse_timestamp(start_ts)
    end_sec = parse_timestamp(end_ts)
    return max(0.0, end_sec - start_sec)


def is_valid_timestamp_range(start_ts: str, end_ts: str) -> Tuple[bool, str]:
    """Validates that timestamps are non-empty, parseable, and start < end."""
    try:
        start_sec = parse_timestamp(start_ts)
        end_sec = parse_timestamp(end_ts)
    except Exception as e:
        return False, f"Could not parse timestamp: {e}"

    if start_sec < 0.0 or end_sec < 0.0:
        return False, "Negative timestamp value detected."

    if end_sec <= start_sec:
        return False, f"End time ({end_ts} -> {end_sec:.2f}s) must be strictly greater than start time ({start_ts} -> {start_sec:.2f}s)."

    return True, "Valid timestamp range."


def format_duration_human(seconds: float) -> str:
    """Human readable duration string, e.g. '34s' or '1m 24s'."""
    sec = int(round(seconds))
    if sec < 60:
        return f"{sec}s"
    mins = sec // 60
    rem = sec % 60
    return f"{mins}m {rem}s" if rem > 0 else f"{mins}m"

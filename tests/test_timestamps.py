"""
Unit tests for timestamp parsing, calculations, and validation.
"""
import pytest
from core.timestamp_utils import (
    parse_timestamp,
    format_seconds,
    calculate_duration,
    is_valid_timestamp_range,
    clean_timestamp_string,
)


def test_parse_timestamp_formats():
    assert parse_timestamp("00:00.00") == 0.0
    assert parse_timestamp("01:23.45") == pytest.approx(83.45)
    assert parse_timestamp("(00:11.30)") == pytest.approx(11.30)
    assert parse_timestamp("01:02:03.50") == pytest.approx(3723.50)
    assert parse_timestamp("45.5") == pytest.approx(45.5)
    assert parse_timestamp(30) == 30.0


def test_format_seconds():
    assert format_seconds(0.0) == "00:00.00"
    assert format_seconds(83.45) == "01:23.45"
    assert format_seconds(3723.5) == "01:02:03.50"
    assert format_seconds(45.0, include_ms=False) == "00:45"


def test_calculate_duration():
    dur = calculate_duration("00:10.00", "00:45.50")
    assert dur == pytest.approx(35.50)
    # Negative or inverted should return 0.0
    assert calculate_duration("01:00.00", "00:30.00") == 0.0


def test_is_valid_timestamp_range():
    valid, msg = is_valid_timestamp_range("00:10.00", "00:40.00")
    assert valid is True

    # Inverted
    invalid, msg = is_valid_timestamp_range("00:50.00", "00:20.00")
    assert invalid is False
    assert "must be strictly greater" in msg

    # Identical
    invalid2, msg2 = is_valid_timestamp_range("00:30.00", "00:30.00")
    assert invalid2 is False


def test_clean_timestamp_string():
    assert clean_timestamp_string("(00:12.30)") == "00:12.30"
    assert clean_timestamp_string(" [01:45.00] ") == "01:45.00"

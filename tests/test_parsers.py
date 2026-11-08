"""
Unit tests for screenplay parsers.
"""
import pytest
from core.parsers import ScreenplayParser
from tests.fixtures.synthetic_screenplays import (
    SYNTHETIC_EPISODE_1,
    SYNTHETIC_EPISODE_WEAK,
    SYNTHETIC_MALFORMED_TIMESTAMPS,
)


def test_parse_synthetic_episode_1():
    ep = ScreenplayParser.parse_text(SYNTHETIC_EPISODE_1, filename="syn_ep01.txt")
    assert ep.episode_id == "EP01"
    assert ep.episode_number == 1
    assert "betrayed heiress" in ep.logline.lower()
    assert len(ep.scenes) == 1
    sc = ep.scenes[0]
    assert sc.scene_number == 1
    assert "BALLROOM" in sc.heading
    assert len(sc.elements) >= 8

    # Check characters
    assert "LADY ELENA" in ep.characters
    assert "LORD MARCUS" in ep.characters

    # Check timed elements
    dialogues = sc.dialogues
    assert len(dialogues) >= 4
    first_dlg = dialogues[0]
    assert first_dlg.speaker == "LADY ELENA"
    assert "signed the deed" in first_dlg.text
    assert first_dlg.start_seconds == pytest.approx(2.0)
    assert first_dlg.end_seconds == pytest.approx(5.5)


def test_parse_weak_episode():
    ep = ScreenplayParser.parse_text(SYNTHETIC_EPISODE_WEAK, filename="syn_ep02.txt")
    assert ep.episode_id == "EP02"
    assert "SERVANT JOHN" in ep.characters
    assert "SERVANT MARY" in ep.characters


def test_parse_malformed_timestamps():
    ep = ScreenplayParser.parse_text(SYNTHETIC_MALFORMED_TIMESTAMPS, filename="syn_ep03.txt")
    assert ep.episode_id == "EP03"
    assert len(ep.scenes) == 1
    sc = ep.scenes[0]
    assert len(sc.elements) >= 1
    assert sc.elements[0].start_seconds == pytest.approx(50.0)
    assert sc.elements[0].end_seconds == pytest.approx(20.0)

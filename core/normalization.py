"""
Text, character, and episode identifier normalization.
"""
import re
from typing import Tuple, Optional


def normalize_episode_id(raw_str: str, fallback_idx: int = 1) -> Tuple[str, int]:
    """
    Extracts a standardized episode identifier like 'EP01' and integer index.
    Matches 'Episode 1', 'episode-001', 'EP01', 'EP_1', etc.
    """
    # Try finding episode number
    m = re.search(r"episode\s*[-_]?\s*(\d+)", raw_str, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        return f"EP{num:02d}", num

    m_ep = re.search(r"ep\s*(\d+)", raw_str, re.IGNORECASE)
    if m_ep:
        num = int(m_ep.group(1))
        return f"EP{num:02d}", num

    # Generic digit match
    m_num = re.search(r"\b(\d+)\b", raw_str)
    if m_num:
        num = int(m_num.group(1))
        return f"EP{num:02d}", num

    return f"EP{fallback_idx:02d}", fallback_idx


def clean_character_name(raw_name: str) -> Tuple[str, Optional[str]]:
    """
    Splits character name and parenthetical direction.
    E.g.: 'LADY JULIANA (Confused, Breathless)' -> ('LADY JULIANA', 'Confused, Breathless')
    """
    raw_name = raw_name.strip()
    m = re.match(r"^([^(]+)(?:\(([^)]+)\))?$", raw_name)
    if m:
        name = m.group(1).strip()
        emotion = m.group(2).strip() if m.group(2) else None
        return name, emotion
    return raw_name, None


def normalize_dialogue_text(text: str) -> str:
    """Removes surrounding quotes and normalizes internal whitespace."""
    if not text:
        return ""
    text = text.strip()
    # Strip leading/trailing double or single quotes
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    # Replace curly quotes
    text = text.replace('“', '"').replace('”', '"').replace("‘", "'").replace("’", "'")
    return text


def clean_scene_heading(heading: str) -> str:
    """Normalizes scene heading / slugline."""
    return re.sub(r"\s+", " ", heading).strip().upper()

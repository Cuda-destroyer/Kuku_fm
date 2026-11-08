"""
Token utilities for prompt budgeting, estimation, and context truncation.
"""
import re
from typing import Union, List


def estimate_tokens(text: str) -> int:
    """Rough estimation of token count (~4 characters per token for English)."""
    if not text:
        return 0
    words = len(re.findall(r"\w+|[^\w\s]", text, re.UNICODE))
    chars = len(text)
    return max(int(chars / 3.8), int(words * 1.2))


def truncate_context(text: str, max_tokens: int = 3000) -> str:
    """Truncates text safely preserving line breaks to stay within token budget."""
    estimated = estimate_tokens(text)
    if estimated <= max_tokens:
        return text

    max_chars = int(max_tokens * 3.5)
    truncated = text[:max_chars]
    last_newline = truncated.rfind("\n")
    if last_newline > int(max_chars * 0.8):
        truncated = truncated[:last_newline]
    return truncated + "\n... [Screenplay text truncated for context budget]"

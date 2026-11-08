"""
Cliffhanger detection engine for unresolved, high-anticipation promo endings.
"""
from typing import List
from models.episode import Episode
from models.promo import CliffhangerCandidate
from llm.base_provider import BaseLLMProvider


class CliffhangerDetectionEngine:
    """Discovers and evaluates unresolved cliffhangers in screenplays."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def detect_cliffhangers(self, episode: Episode) -> List[CliffhangerCandidate]:
        """Discovers cliffhanger candidates in the episode using the LLM provider."""
        return self.provider.detect_cliffhangers(episode)

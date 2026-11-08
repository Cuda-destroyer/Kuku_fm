"""
Hook detection engine for mobile short-form video promos (first 3 seconds).
"""
from typing import List
from models.episode import Episode
from models.promo import HookCandidate
from llm.base_provider import BaseLLMProvider


class HookDetectionEngine:
    """Discovers and evaluates opening scroll-stopping hooks in screenplays."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def detect_hooks(self, episode: Episode) -> List[HookCandidate]:
        """Discovers hook candidates in the episode using the LLM provider."""
        return self.provider.detect_hooks(episode)

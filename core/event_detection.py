"""
Dramatic event detection engine.
"""
from typing import List
from models.episode import Episode, StoryEvent
from llm.base_provider import BaseLLMProvider


class EventDetectionEngine:
    """Discovers high-stakes turning points and dramatic incidents."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def detect_events(self, episode: Episode) -> List[StoryEvent]:
        """Detects high-intensity events within an episode."""
        analysis = self.provider.analyze_episode(episode)
        return analysis.key_events

"""
Character dynamic extraction and cross-episode tracking.
"""
from typing import List, Dict, Any
from models.episode import Episode, CharacterProfile
from llm.base_provider import BaseLLMProvider


class CharacterAnalysisEngine:
    """Tracks and classifies characters across the series."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def extract_characters(self, episode: Episode) -> List[CharacterProfile]:
        """Extracts character profiles from an episode using the LLM provider."""
        profiles = self.provider.extract_characters(episode)
        episode.character_profiles = profiles
        return profiles

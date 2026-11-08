"""
Story understanding engine and cross-episode story memory index.
"""
from typing import List, Dict, Any, Optional
import logging
from models.episode import Episode, StoryEvent, CharacterProfile
from models.schemas import LLMEpisodeAnalysis
from llm.base_provider import BaseLLMProvider

logger = logging.getLogger("kuku.core.story_analysis")


class StoryAnalysisEngine:
    """Consolidates screenplay understanding across single episodes and full series."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider
        self.episode_analyses: Dict[str, LLMEpisodeAnalysis] = {}
        self.global_character_index: Dict[str, Dict[str, Any]] = {}
        self.global_events: List[StoryEvent] = []

    def analyze_episode(self, episode: Episode) -> LLMEpisodeAnalysis:
        """Runs LLM story analysis for a single episode."""
        analysis = self.provider.analyze_episode(episode)
        self.episode_analyses[episode.episode_id] = analysis

        # Update global character index
        for char in analysis.characters:
            if char.name not in self.global_character_index:
                self.global_character_index[char.name] = {
                    "role": char.role,
                    "description": char.description,
                    "episodes_appeared": [episode.episode_id],
                    "relationships": dict(char.relationships),
                }
            else:
                self.global_character_index[char.name]["episodes_appeared"].append(episode.episode_id)
                self.global_character_index[char.name]["relationships"].update(char.relationships)

        # Update global events
        self.global_events.extend(analysis.key_events)
        episode.processing_status = "ANALYZED"
        episode.character_profiles = analysis.characters
        episode.events = analysis.key_events

        return analysis

    def get_series_synopsis(self, max_episodes: int = 50) -> str:
        """Builds a compact series overview from analyzed episodes."""
        lines = ["SERIES STORY CONTEXT:"]
        for ep_id, ana in list(self.episode_analyses.items())[:max_episodes]:
            lines.append(f"- {ep_id}: {ana.main_conflict} (Arc: {ana.emotional_arc})")
        return "\n".join(lines)

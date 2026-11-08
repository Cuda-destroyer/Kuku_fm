"""
Core business logic package for Kuku Promo Intelligence.
"""
from core.timestamp_utils import (
    parse_timestamp,
    format_seconds,
    calculate_duration,
    is_valid_timestamp_range,
    format_duration_human,
)
from core.normalization import (
    normalize_episode_id,
    clean_character_name,
    normalize_dialogue_text,
    clean_scene_heading,
)
from core.parsers import ScreenplayParser
from core.ingestion import IngestionEngine
from core.story_analysis import StoryAnalysisEngine
from core.character_analysis import CharacterAnalysisEngine
from core.event_detection import EventDetectionEngine
from core.hook_detection import HookDetectionEngine
from core.cliffhanger_detection import CliffhangerDetectionEngine
from core.context_evaluation import ContextEvaluationEngine
from core.candidate_generation import CandidateGenerationEngine
from core.scoring import ScoringEngine
from core.validation import ValidationEngine
from core.deduplication import DeduplicationEngine
from core.pipeline import PromoDiscoveryPipeline, PipelineState

__all__ = [
    "parse_timestamp",
    "format_seconds",
    "calculate_duration",
    "is_valid_timestamp_range",
    "format_duration_human",
    "normalize_episode_id",
    "clean_character_name",
    "normalize_dialogue_text",
    "clean_scene_heading",
    "ScreenplayParser",
    "IngestionEngine",
    "StoryAnalysisEngine",
    "CharacterAnalysisEngine",
    "EventDetectionEngine",
    "HookDetectionEngine",
    "CliffhangerDetectionEngine",
    "ContextEvaluationEngine",
    "CandidateGenerationEngine",
    "ScoringEngine",
    "ValidationEngine",
    "DeduplicationEngine",
    "PromoDiscoveryPipeline",
    "PipelineState",
]

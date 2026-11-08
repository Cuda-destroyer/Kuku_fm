"""
Abstract Base LLM Provider interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, TypeVar, Tuple
from pydantic import BaseModel
from models.episode import Episode, CharacterProfile, StoryEvent
from models.promo import HookCandidate, CliffhangerCandidate, PromoCandidate
from models.schemas import (
    LLMEpisodeAnalysis,
    LLMHookItem,
    LLMCliffhangerItem,
    LLMContextEvaluation,
    LLMPromoCandidateRaw,
)

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract interface for all language model providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider, e.g. 'huggingface' or 'mock'."""
        pass

    @property
    @abstractmethod
    def model_id(self) -> str:
        """Model identifier."""
        pass

    @abstractmethod
    def health_check(self) -> Tuple[bool, str]:
        """Verify API connectivity and authentication. Returns (is_healthy, message)."""
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.3,
    ) -> str:
        """Raw completion or chat generation."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2,
    ) -> T:
        """Generate and validate structured output against a Pydantic schema."""
        pass

    @abstractmethod
    def analyze_episode(self, episode: Episode) -> LLMEpisodeAnalysis:
        """Extract story arcs, conflict, characters, and events from an episode."""
        pass

    @abstractmethod
    def extract_characters(self, episode: Episode) -> List[CharacterProfile]:
        """Extract active characters and their traits from an episode."""
        pass

    @abstractmethod
    def detect_hooks(self, episode: Episode) -> List[HookCandidate]:
        """Discover opening hook candidates in the first 3 seconds / key moments."""
        pass

    @abstractmethod
    def detect_cliffhangers(self, episode: Episode) -> List[CliffhangerCandidate]:
        """Discover unresolved cliffhangers suitable for promo endings."""
        pass

    @abstractmethod
    def evaluate_context(
        self, promo_title: str, segment_type: str, segments_summary: str, dialogue_summary: str
    ) -> LLMContextEvaluation:
        """Evaluate standalone context for a new viewer."""
        pass

    @abstractmethod
    def generate_candidates(
        self, episode: Episode, show_context: Optional[str] = None
    ) -> List[LLMPromoCandidateRaw]:
        """Generate promo candidate sequence definitions."""
        pass

    @abstractmethod
    def evaluate_promo(self, candidate: PromoCandidate) -> Dict[str, Any]:
        """Final promotional assessment and marketing appeal review."""
        pass

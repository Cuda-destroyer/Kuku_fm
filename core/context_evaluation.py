"""
Standalone context evaluation engine for evaluating promos from a cold viewer perspective.
"""
from typing import List, Dict, Any
from models.promo import PromoSegment
from models.schemas import LLMContextEvaluation
from llm.base_provider import BaseLLMProvider


class ContextEvaluationEngine:
    """Evaluates whether a candidate promotional clip is fully intelligible without prior series knowledge."""

    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def evaluate_candidate_context(
        self,
        promo_title: str,
        segment_type: str,
        segments: List[PromoSegment],
    ) -> LLMContextEvaluation:
        """Evaluates standalone context using the LLM provider."""
        segments_summary = [
            f"Segment {s.segment_order} ({s.episode_id} {s.start_timestamp}-{s.end_timestamp}): {s.selected_moment}"
            for s in segments
        ]
        dialogue_summary = []
        for s in segments:
            dialogue_summary.extend(s.dialogue_excerpts)

        return self.provider.evaluate_context(
            promo_title=promo_title,
            segment_type=segment_type,
            segments_summary="\n".join(segments_summary),
            dialogue_summary="\n".join(dialogue_summary[:10]) if dialogue_summary else "Dramatic confrontation",
        )

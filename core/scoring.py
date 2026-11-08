"""
Transparent, deterministic scoring and ranking engine for promotional candidates.
"""
from typing import List
from models.promo import PromoCandidate, ScoreBreakdown
from config.settings import settings


class ScoringEngine:
    """Calculates weighted scores out of 100 and classifies promotional tiers."""

    WEIGHTS = settings.SCORING_WEIGHTS

    @classmethod
    def calculate_duration_score(cls, total_duration_seconds: float) -> float:
        """
        Duration suitability scoring (0-100).
        Sweet spot for short-form mobile ads is 30 to 45 seconds (100 pts).
        20-30s and 45-60s receive 80-95 pts.
        Outside 20-60s receives 0 pts.
        """
        dur = float(total_duration_seconds)
        if dur < 20.0 or dur > 60.0:
            return 0.0
        if 30.0 <= dur <= 45.0:
            return 100.0
        elif 25.0 <= dur < 30.0:
            # Linear ramp from 85 to 100
            return 85.0 + (dur - 25.0) * 3.0
        elif 20.0 <= dur < 25.0:
            return 75.0 + (dur - 20.0) * 2.0
        elif 45.0 < dur <= 52.0:
            # Gentle taper from 100 down to 90
            return 100.0 - (dur - 45.0) * 1.4
        else:  # 52.0 < dur <= 60.0
            return 90.0 - (dur - 52.0) * 2.0

    @classmethod
    def calculate_breakdown(
        cls,
        hook_score: float,
        cliffhanger_score: float,
        context_score: float,
        coherence_score: float,
        emotional_score: float,
        curiosity_score: float,
        total_duration_seconds: float,
    ) -> ScoreBreakdown:
        """Calculates transparent score breakdown with weighted total."""
        duration_score = cls.calculate_duration_score(total_duration_seconds)

        hook = min(100.0, max(0.0, float(hook_score)))
        cliff = min(100.0, max(0.0, float(cliffhanger_score)))
        context = min(100.0, max(0.0, float(context_score)))
        coherence = min(100.0, max(0.0, float(coherence_score)))
        emotional = min(100.0, max(0.0, float(emotional_score)))
        curiosity = min(100.0, max(0.0, float(curiosity_score)))

        weighted_total = (
            (cls.WEIGHTS["hook"] / 100.0) * hook
            + (cls.WEIGHTS["cliffhanger"] / 100.0) * cliff
            + (cls.WEIGHTS["context"] / 100.0) * context
            + (cls.WEIGHTS["coherence"] / 100.0) * coherence
            + (cls.WEIGHTS["emotional"] / 100.0) * emotional
            + (cls.WEIGHTS["curiosity"] / 100.0) * curiosity
            + (cls.WEIGHTS["duration"] / 100.0) * duration_score
        )

        return ScoreBreakdown(
            hook_score=round(hook, 2),
            cliffhanger_score=round(cliff, 2),
            context_score=round(context, 2),
            coherence_score=round(coherence, 2),
            emotional_score=round(emotional, 2),
            curiosity_score=round(curiosity, 2),
            duration_score=round(duration_score, 2),
            weighted_total=round(weighted_total, 2),
        )

    @classmethod
    def classify_tier(cls, score: float, validation_status: str) -> str:
        """Assigns editorial ranking tier."""
        if validation_status == "REJECTED":
            return "Rejected candidate"
        if score >= 88.0:
            return "Excellent promotional candidate"
        elif score >= 78.0:
            return "Strong promotional candidate"
        elif score >= 65.0:
            return "Potential candidate — human review required"
        else:
            return "Rejected candidate"

    @classmethod
    def rank_candidates(cls, candidates: List[PromoCandidate]) -> List[PromoCandidate]:
        """Ranks candidates by descending score and assigns rank index."""
        # Valid candidates come first, sorted by score descending
        valid = [c for c in candidates if c.validation_status == "VALID"]
        review = [c for c in candidates if c.validation_status == "NEEDS_REVIEW"]
        rejected = [c for c in candidates if c.validation_status == "REJECTED"]

        valid.sort(key=lambda x: x.score, reverse=True)
        review.sort(key=lambda x: x.score, reverse=True)
        rejected.sort(key=lambda x: x.score, reverse=True)

        ordered = valid + review + rejected

        for idx, cand in enumerate(ordered):
            cand.rank = idx + 1
            cand.ranking_category = cls.classify_tier(cand.score, cand.validation_status)

        return ordered

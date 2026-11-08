"""
Promo candidate, segment, score breakdown, and validation models.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HookCandidate(BaseModel):
    """An identified opening hook moment."""
    hook_id: str = Field(..., description="Unique hook identifier")
    episode_id: str = Field(..., description="Source episode ID")
    source_timestamp: str = Field(..., description="Timestamp string (MM:SS.SS or range)")
    start_seconds: float = Field(..., ge=0.0)
    end_seconds: float = Field(..., ge=0.0)
    relevant_content: str = Field(..., description="Dialogue line or action triggering the hook")
    hook_type: str = Field(..., description="Type: shocking_statement, betrayal, confrontation, mystery, etc.")
    explanation: str = Field(..., description="Why this hook stops the scroll within the first 3 seconds")
    hook_score: float = Field(..., ge=0.0, le=100.0, description="Hook quality score (0-100)")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Model confidence 0-1")
    screenplay_reference: str = Field("", description="Exact citation / line quote from script")


class CliffhangerCandidate(BaseModel):
    """An identified unresolved cliffhanger moment."""
    cliffhanger_id: str = Field(..., description="Unique cliffhanger identifier")
    episode_id: str = Field(..., description="Source episode ID")
    source_timestamp: str = Field(..., description="Timestamp string (MM:SS.SS or range)")
    start_seconds: float = Field(..., ge=0.0)
    end_seconds: float = Field(..., ge=0.0)
    event_description: str = Field(..., description="Description of the concluding event")
    unresolved_element: str = Field(..., description="What specifically remains unresolved")
    why_viewer_continues: str = Field(..., description="Why the audience will tap through to next episode")
    cliffhanger_score: float = Field(..., ge=0.0, le=100.0, description="Cliffhanger quality score (0-100)")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Model confidence 0-1")
    screenplay_reference: str = Field("", description="Exact citation / line quote from script")


class PromoSegment(BaseModel):
    """An individual segment making up a promo candidate."""
    segment_order: int = Field(..., ge=1, description="Order index 1, 2, ... in the promo sequence")
    episode_id: str = Field(..., description="Source episode ID")
    source_filename: str = Field("", description="Source filename")
    scene_id: Optional[str] = Field(None, description="Optional scene ID")
    start_timestamp: str = Field(..., description="Start timestamp string, e.g. '00:11.30'")
    end_timestamp: str = Field(..., description="End timestamp string, e.g. '00:45.00'")
    start_seconds: float = Field(..., ge=0.0)
    end_seconds: float = Field(..., ge=0.0)
    selected_moment: str = Field(..., description="Summary of narrative action in this cut")
    reason_for_inclusion: str = Field(..., description="Editorial reason for inclusion (hook, context, cliffhanger)")
    dialogue_excerpts: List[str] = Field(default_factory=list, description="Key spoken lines in this segment")

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.end_seconds - self.start_seconds)


class ScoreBreakdown(BaseModel):
    """Transparent weighted score breakdown out of 100."""
    hook_score: float = Field(..., ge=0.0, le=100.0, description="Hook strength (Weight: 20)")
    cliffhanger_score: float = Field(..., ge=0.0, le=100.0, description="Cliffhanger strength (Weight: 20)")
    context_score: float = Field(..., ge=0.0, le=100.0, description="Standalone context (Weight: 20)")
    coherence_score: float = Field(..., ge=0.0, le=100.0, description="Narrative coherence (Weight: 15)")
    emotional_score: float = Field(..., ge=0.0, le=100.0, description="Emotional intensity (Weight: 10)")
    curiosity_score: float = Field(..., ge=0.0, le=100.0, description="Promotional curiosity (Weight: 10)")
    duration_score: float = Field(..., ge=0.0, le=100.0, description="Duration suitability (Weight: 5)")
    weighted_total: float = Field(..., ge=0.0, le=100.0, description="Final calculated weighted total (0-100)")


class ValidationResult(BaseModel):
    """Deterministic validation status and gates."""
    is_valid: bool = Field(..., description="True if passes all hard gates")
    duration_valid: bool = Field(..., description="True if 20s <= duration <= 60s")
    timestamps_valid: bool = Field(..., description="True if timestamps exist, format ok, start < end")
    source_references_valid: bool = Field(..., description="True if references correspond to actual scenes")
    hook_valid: bool = Field(..., description="True if an opening hook exists")
    cliffhanger_valid: bool = Field(..., description="True if an unresolved cliffhanger exists")
    context_acceptable: bool = Field(..., description="True if standalone context is not Poor")
    warnings: List[str] = Field(default_factory=list)
    rejection_reasons: List[str] = Field(default_factory=list)


class PromoCandidate(BaseModel):
    """Complete promotional candidate sequence."""
    promo_id: str = Field(..., description="Unique promo identifier, e.g. 'PROMO-01'")
    title: str = Field(..., description="Compelling editorial ad title")
    rank: int = Field(0, description="Rank position among candidates (1 is top)")
    total_duration_seconds: float = Field(..., ge=0.0, description="Sum of segment durations")
    segment_type: str = Field("continuous", description="'continuous' or 'multi_segment'")
    segments: List[PromoSegment] = Field(..., description="List of timed promo segments in play order")
    hook: HookCandidate = Field(..., description="The opening hook of the promo")
    cliffhanger: CliffhangerCandidate = Field(..., description="The unresolved closing cliffhanger")
    standalone_context: str = Field(..., description="Assessment of viewer understanding without prior knowledge")
    context_rating: str = Field("Good", description="'Excellent', 'Good', 'Weak', 'Poor'")
    narrative_explanation: str = Field(..., description="Why this sequence forms a compelling promotional arc")
    score: float = Field(..., ge=0.0, le=100.0, description="Overall weighted score")
    score_breakdown: ScoreBreakdown = Field(..., description="Detailed weighted scoring")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Model confidence")
    validation_status: str = Field("VALID", description="'VALID', 'REJECTED', 'NEEDS_REVIEW'")
    rejection_reasons: List[str] = Field(default_factory=list)
    ranking_category: str = Field("Strong promotional candidate", description="Human-readable quality tier")
    human_approval_status: str = Field("PENDING", description="'PENDING', 'APPROVED', 'REJECTED'")
    human_feedback: Optional[str] = Field(None, description="Editorial review comments")

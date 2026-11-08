"""
Unit tests for deterministic validation gates.
"""
import pytest
from core.validation import ValidationEngine
from core.scoring import ScoringEngine
from models.promo import PromoCandidate, PromoSegment, HookCandidate, CliffhangerCandidate


def make_dummy_candidate(duration: float, context_rating: str = "Good", hook_score: float = 85.0, cliff_score: float = 85.0) -> PromoCandidate:
    hook = HookCandidate(
        hook_id="H01",
        episode_id="EP01",
        source_timestamp="00:02.00",
        start_seconds=2.0,
        end_seconds=5.0,
        relevant_content="Shocking line",
        hook_type="shocking_statement",
        explanation="Stops scroll",
        hook_score=hook_score,
        confidence=0.9,
    )
    cliff = CliffhangerCandidate(
        cliffhanger_id="C01",
        episode_id="EP01",
        source_timestamp="00:35.00",
        start_seconds=30.0,
        end_seconds=35.0,
        event_description="Cliffhanger ending",
        unresolved_element="Unresolved dilemma",
        why_viewer_continues="Anticipation",
        cliffhanger_score=cliff_score,
        confidence=0.9,
    )
    seg = PromoSegment(
        segment_order=1,
        episode_id="EP01",
        start_timestamp="00:02.00",
        end_timestamp=f"00:{int(2.0 + duration):02d}.00",
        start_seconds=2.0,
        end_seconds=2.0 + duration,
        selected_moment="Full sequence",
        reason_for_inclusion="Opening and closing",
    )
    bd = ScoringEngine.calculate_breakdown(
        hook_score=hook_score,
        cliffhanger_score=cliff_score,
        context_score=80.0,
        coherence_score=80.0,
        emotional_score=80.0,
        curiosity_score=80.0,
        total_duration_seconds=duration,
    )
    return PromoCandidate(
        promo_id="TEST-01",
        title="Test Candidate",
        total_duration_seconds=duration,
        segment_type="continuous",
        segments=[seg],
        hook=hook,
        cliffhanger=cliff,
        standalone_context="Clear confrontation",
        context_rating=context_rating,
        narrative_explanation="Explanation",
        score=bd.weighted_total,
        score_breakdown=bd,
        confidence=0.9,
        validation_status="VALID",
        rejection_reasons=[],
    )


def test_validation_valid_candidate():
    cand = make_dummy_candidate(duration=35.0, context_rating="Good")
    res = ValidationEngine.validate_candidate(cand)
    assert res.is_valid is True
    assert cand.validation_status == "VALID"
    assert len(res.rejection_reasons) == 0


def test_validation_duration_too_short():
    cand = make_dummy_candidate(duration=15.0)  # Under 20s
    res = ValidationEngine.validate_candidate(cand)
    assert res.is_valid is False
    assert res.duration_valid is False
    assert cand.validation_status == "REJECTED"
    assert any("below required minimum" in r for r in res.rejection_reasons)


def test_validation_duration_too_long():
    cand = make_dummy_candidate(duration=75.0)  # Over 60s
    res = ValidationEngine.validate_candidate(cand)
    assert res.is_valid is False
    assert res.duration_valid is False
    assert cand.validation_status == "REJECTED"
    assert any("exceeds maximum allowed limit" in r for r in res.rejection_reasons)


def test_validation_poor_context_rejected():
    cand = make_dummy_candidate(duration=35.0, context_rating="Poor")
    res = ValidationEngine.validate_candidate(cand)
    assert res.is_valid is False
    assert res.context_acceptable is False
    assert cand.validation_status == "REJECTED"
    assert any("context" in r.lower() for r in res.rejection_reasons)


def test_validation_weak_hook_rejected():
    cand = make_dummy_candidate(duration=35.0, hook_score=20.0)
    res = ValidationEngine.validate_candidate(cand)
    assert res.is_valid is False
    assert res.hook_valid is False

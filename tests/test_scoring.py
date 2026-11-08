"""
Unit tests for scoring, duration weights, and ranking.
"""
import pytest
from core.scoring import ScoringEngine


def test_duration_suitability_score():
    # Sweet spot: 30-45 seconds -> 100
    assert ScoringEngine.calculate_duration_score(35.0) == 100.0
    assert ScoringEngine.calculate_duration_score(30.0) == 100.0
    assert ScoringEngine.calculate_duration_score(45.0) == 100.0

    # Outside bounds: < 20s or > 60s -> 0
    assert ScoringEngine.calculate_duration_score(15.0) == 0.0
    assert ScoringEngine.calculate_duration_score(65.0) == 0.0

    # Intermediate ranges: 20-30s and 45-60s
    assert 75.0 <= ScoringEngine.calculate_duration_score(22.0) <= 90.0
    assert 80.0 <= ScoringEngine.calculate_duration_score(55.0) <= 95.0


def test_calculate_breakdown():
    bd = ScoringEngine.calculate_breakdown(
        hook_score=90.0,
        cliffhanger_score=90.0,
        context_score=80.0,
        coherence_score=85.0,
        emotional_score=90.0,
        curiosity_score=85.0,
        total_duration_seconds=35.0,  # 100 pts duration
    )

    # Weights: hook 20, cliff 20, context 20, coherence 15, emotional 10, curiosity 10, duration 5
    # Expected: 0.2*90 + 0.2*90 + 0.2*80 + 0.15*85 + 0.10*90 + 0.10*85 + 0.05*100
    # = 18 + 18 + 16 + 12.75 + 9 + 8.5 + 5 = 87.25
    assert bd.weighted_total == pytest.approx(87.25, abs=0.1)


def test_classify_tier():
    assert ScoringEngine.classify_tier(92.0, "VALID") == "Excellent promotional candidate"
    assert ScoringEngine.classify_tier(80.0, "VALID") == "Strong promotional candidate"
    assert ScoringEngine.classify_tier(70.0, "VALID") == "Potential candidate — human review required"
    assert ScoringEngine.classify_tier(55.0, "VALID") == "Rejected candidate"
    assert ScoringEngine.classify_tier(95.0, "REJECTED") == "Rejected candidate"

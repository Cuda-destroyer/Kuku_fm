"""
Unit tests for candidate generation, multi-segment construction, and deduplication.
"""
import pytest
from core.parsers import ScreenplayParser
from core.candidate_generation import CandidateGenerationEngine
from core.deduplication import DeduplicationEngine
from llm.mock_provider import MockProvider
from tests.fixtures.synthetic_screenplays import SYNTHETIC_EPISODE_1


def test_candidate_generation_synthetic():
    ep = ScreenplayParser.parse_text(SYNTHETIC_EPISODE_1, filename="syn01.txt")
    provider = MockProvider()
    engine = CandidateGenerationEngine(provider)

    hooks = provider.detect_hooks(ep)
    cliffs = provider.detect_cliffhangers(ep)

    assert len(hooks) >= 1
    assert len(cliffs) >= 1

    candidates = engine.generate_candidates_for_episode(ep, hooks, cliffs)
    assert len(candidates) >= 1

    # Check candidate properties
    first = candidates[0]
    assert 20.0 <= first.total_duration_seconds <= 60.0
    assert first.hook is not None
    assert first.cliffhanger is not None
    assert first.validation_status == "VALID"


def test_deduplication():
    ep = ScreenplayParser.parse_text(SYNTHETIC_EPISODE_1, filename="syn01.txt")
    provider = MockProvider()
    engine = CandidateGenerationEngine(provider)
    hooks = provider.detect_hooks(ep)
    cliffs = provider.detect_cliffhangers(ep)
    cands = engine.generate_candidates_for_episode(ep, hooks, cliffs)

    assert len(cands) >= 1

    # Take the top candidate and duplicate it
    base_cand = cands[0]
    dup_cand = base_cand.model_copy(deep=True)
    dup_cand.promo_id = "PROMO-DUP-01"

    # Pass base candidate + exact duplicate
    pair = [base_cand, dup_cand]
    unique, removed = DeduplicationEngine.deduplicate(pair, max_overlap_threshold=0.70)

    assert len(unique) == 1
    assert len(removed) == 1
    assert removed[0].promo_id == "PROMO-DUP-01"

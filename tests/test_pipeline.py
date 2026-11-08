"""
Integration tests for the full discovery and ranking pipeline.
"""
import pytest
from core.parsers import ScreenplayParser
from core.pipeline import PromoDiscoveryPipeline
from llm.mock_provider import MockProvider
from utils.file_utils import ExportManager
from tests.fixtures.synthetic_screenplays import SYNTHETIC_EPISODE_1, SYNTHETIC_EPISODE_WEAK


def test_end_to_end_pipeline_synthetic():
    ep1 = ScreenplayParser.parse_text(SYNTHETIC_EPISODE_1, filename="syn01.txt", fallback_index=1)
    ep2 = ScreenplayParser.parse_text(SYNTHETIC_EPISODE_WEAK, filename="syn02.txt", fallback_index=2)

    provider = MockProvider()
    pipeline = PromoDiscoveryPipeline(provider)

    state = pipeline.run([ep1, ep2])

    assert len(state.episodes) == 2
    assert len(state.manifest) == 2
    assert len(state.hooks) >= 1
    assert len(state.cliffhangers) >= 1
    assert len(state.valid_candidates) >= 1

    # Check top candidate
    top = state.valid_candidates[0]
    assert top.rank == 1
    assert top.score >= 70.0
    assert 20.0 <= top.total_duration_seconds <= 60.0
    assert top.validation_status == "VALID"

    # Test Exports
    json_out = ExportManager.export_json(state.valid_candidates)
    assert len(json_out) > 50
    assert "PROMO" in json_out

    csv_out = ExportManager.export_csv(state.valid_candidates)
    assert "Rank,Promo ID,Title" in csv_out

    md_out = ExportManager.export_markdown_report(state.valid_candidates, state.manifest)
    assert "KUKU PROMO INTELLIGENCE" in md_out
    assert "Rank #1" in md_out

    pdf_out = ExportManager.export_pdf_report(state.valid_candidates)
    assert len(pdf_out) > 100

    edl_out = ExportManager.export_cmx3600_edl(top)
    assert "FCM: NON-DROP FRAME" in edl_out
    assert "001" in edl_out

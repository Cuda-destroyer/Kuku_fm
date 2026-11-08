"""
Hierarchical discovery and ranking pipeline.
Orchestrates ingestion, analysis, hook & cliffhanger discovery,
candidate construction, validation, deduplication, and ranking.
"""
import time
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path

from models.episode import Episode
from models.promo import PromoCandidate, HookCandidate, CliffhangerCandidate
from models.schemas import EpisodeManifestItem
from core.ingestion import IngestionEngine
from core.story_analysis import StoryAnalysisEngine
from core.hook_detection import HookDetectionEngine
from core.cliffhanger_detection import CliffhangerDetectionEngine
from core.candidate_generation import CandidateGenerationEngine
from core.validation import ValidationEngine
from core.scoring import ScoringEngine
from core.deduplication import DeduplicationEngine
from llm.base_provider import BaseLLMProvider
from utils.cache import PipelineCache

logger = logging.getLogger("kuku.core.pipeline")


class PipelineState:
    """Stores intermediate and final state of the promo intelligence pipeline."""
    def __init__(self):
        self.episodes: Dict[str, Episode] = {}
        self.manifest: List[EpisodeManifestItem] = []
        self.hooks: List[HookCandidate] = []
        self.cliffhangers: List[CliffhangerCandidate] = []
        self.raw_candidates: List[PromoCandidate] = []
        self.valid_candidates: List[PromoCandidate] = []
        self.rejected_candidates: List[PromoCandidate] = []
        self.duplicate_candidates: List[PromoCandidate] = []
        self.human_approved_count: int = 0
        self.execution_time_seconds: float = 0.0
        self.logs: List[str] = []


class PromoDiscoveryPipeline:
    """Full end-to-end promotional discovery pipeline."""

    def __init__(self, provider: BaseLLMProvider, cache_dir: Optional[Path] = None):
        self.provider = provider
        self.cache = PipelineCache(cache_dir)
        self.story_engine = StoryAnalysisEngine(provider)
        self.hook_engine = HookDetectionEngine(provider)
        self.cliffhanger_engine = CliffhangerDetectionEngine(provider)
        self.generation_engine = CandidateGenerationEngine(provider)
        self.validation_engine = ValidationEngine()
        self.scoring_engine = ScoringEngine()
        self.dedup_engine = DeduplicationEngine()
        self.state = PipelineState()

    def run(
        self,
        episodes: List[Episode],
        progress_callback: Optional[Callable[[float, str], None]] = None,
        max_episodes: Optional[int] = None,
    ) -> PipelineState:
        """Executes the full promotional discovery pipeline across ingested episodes."""
        start_time = time.time()
        self._log(f"Starting pipeline execution with {len(episodes)} episodes using {self.provider.provider_name} ({self.provider.model_id}).")

        target_episodes = episodes[:max_episodes] if max_episodes else episodes
        self.state.episodes = {ep.episode_id: ep for ep in target_episodes}
        self.state.manifest = IngestionEngine.generate_manifest(target_episodes)

        total_steps = len(target_episodes) + 4
        current_step = 0

        # STAGE 1 & 2 & 3: Hierarchical Episode Analysis & Feature Discovery
        for idx, ep in enumerate(target_episodes):
            current_step += 1
            pct = current_step / total_steps
            msg = f"Analyzing {ep.episode_id} ({idx+1}/{len(target_episodes)}) - Characters, Conflict & Events..."
            if progress_callback:
                progress_callback(pct, msg)
            self._log(msg)

            # Check cache or analyze
            cache_key = f"{ep.episode_id}_{self.provider.model_id}"
            cached_data = self.cache.get(cache_key)

            if cached_data:
                self._log(f"Loaded cached analysis for {ep.episode_id}.")
                ep_hooks = [HookCandidate.model_validate(h) for h in cached_data.get("hooks", [])]
                ep_cliffs = [CliffhangerCandidate.model_validate(c) for c in cached_data.get("cliffhangers", [])]
            else:
                try:
                    self.story_engine.analyze_episode(ep)
                    ep_hooks = self.hook_engine.detect_hooks(ep)
                    ep_cliffs = self.cliffhanger_engine.detect_cliffhangers(ep)

                    # Save to cache
                    self.cache.set(cache_key, {
                        "hooks": [h.model_dump() for h in ep_hooks],
                        "cliffhangers": [c.model_dump() for c in ep_cliffs],
                    })
                except Exception as e:
                    self._log(f"Analysis failed for {ep.episode_id}: {e}")
                    ep.processing_status = "FAILED"
                    ep.warnings.append(str(e))
                    ep_hooks = []
                    ep_cliffs = []

            self.state.hooks.extend(ep_hooks)
            self.state.cliffhangers.extend(ep_cliffs)

            # STAGE 4: Candidate Generation for episode
            cands = self.generation_engine.generate_candidates_for_episode(
                ep, ep_hooks, ep_cliffs, series_context=self.story_engine.get_series_synopsis()
            )
            self.state.raw_candidates.extend(cands)

        # STAGE 5: Validation
        current_step += 1
        if progress_callback:
            progress_callback(current_step / total_steps, "Validating duration, timestamps and context gates...")
        self._log(f"Validating {len(self.state.raw_candidates)} candidate sequences...")

        for cand in self.state.raw_candidates:
            self.validation_engine.validate_candidate(cand, self.state.episodes)

        # STAGE 6: Deduplication
        current_step += 1
        if progress_callback:
            progress_callback(current_step / total_steps, "Removing duplicate sequences and overlapping angles...")
        unique_cands, dups = self.dedup_engine.deduplicate(self.state.raw_candidates)
        self.state.duplicate_candidates = dups
        self._log(f"Removed {len(dups)} duplicate or heavily overlapping candidates.")

        # STAGE 7: Scoring & Ranking
        current_step += 1
        if progress_callback:
            progress_callback(current_step / total_steps, "Scoring and ranking top promotional candidates...")
        ranked_all = self.scoring_engine.rank_candidates(unique_cands)

        self.state.valid_candidates = [c for c in ranked_all if c.validation_status == "VALID"]
        self.state.rejected_candidates = [c for c in ranked_all if c.validation_status != "VALID"]

        self.state.execution_time_seconds = round(time.time() - start_time, 2)
        summary_msg = (
            f"Pipeline completed in {self.state.execution_time_seconds}s. "
            f"Hooks: {len(self.state.hooks)} | Cliffhangers: {len(self.state.cliffhangers)} | "
            f"Valid Promos: {len(self.state.valid_candidates)} | Rejected: {len(self.state.rejected_candidates)}"
        )
        self._log(summary_msg)
        if progress_callback:
            progress_callback(1.0, "Analysis complete!")

        return self.state

    def _log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.state.logs.append(entry)
        logger.info(entry)

"""
Deduplication and diversity filtering for promotional candidates.
"""
from typing import List, Set, Tuple
from models.promo import PromoCandidate


class DeduplicationEngine:
    """Removes overlapping or redundant promo sequences to ensure creative diversity."""

    @classmethod
    def calculate_overlap_ratio(cls, cand_a: PromoCandidate, cand_b: PromoCandidate) -> float:
        """
        Calculates temporal overlap between two candidates.
        Returns a ratio between 0.0 (no overlap) and 1.0 (identical window).
        """
        # If segments from different episodes, no overlap
        eps_a = {s.episode_id for s in cand_a.segments}
        eps_b = {s.episode_id for s in cand_b.segments}
        common_eps = eps_a.intersection(eps_b)
        if not common_eps:
            return 0.0

        total_overlap_seconds = 0.0
        for ep_id in common_eps:
            segs_a = [s for s in cand_a.segments if s.episode_id == ep_id]
            segs_b = [s for s in cand_b.segments if s.episode_id == ep_id]

            for sa in segs_a:
                for sb in segs_b:
                    overlap_start = max(sa.start_seconds, sb.start_seconds)
                    overlap_end = min(sa.end_seconds, sb.end_seconds)
                    if overlap_end > overlap_start:
                        total_overlap_seconds += (overlap_end - overlap_start)

        min_duration = min(cand_a.total_duration_seconds, cand_b.total_duration_seconds)
        if min_duration <= 0.0:
            return 0.0
        return min(1.0, total_overlap_seconds / min_duration)

    @classmethod
    def deduplicate(
        cls, candidates: List[PromoCandidate], max_overlap_threshold: float = 0.70
    ) -> Tuple[List[PromoCandidate], List[PromoCandidate]]:
        """
        Filters candidates preserving highest scoring version when two candidates overlap excessively (>70%).
        Returns (unique_candidates, duplicates_removed).
        """
        # Sort by score descending so higher scoring variants are preserved
        sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
        kept: List[PromoCandidate] = []
        duplicates: List[PromoCandidate] = []

        for cand in sorted_candidates:
            is_dup = False
            for existing in kept:
                # Check identical hook or cliffhanger ID
                identical_hook = cand.hook.hook_id == existing.hook.hook_id
                identical_cliff = cand.cliffhanger.cliffhanger_id == existing.cliffhanger.cliffhanger_id

                overlap = cls.calculate_overlap_ratio(cand, existing)

                if (identical_hook and identical_cliff) or overlap > max_overlap_threshold:
                    is_dup = True
                    break

            if is_dup:
                duplicates.append(cand)
            else:
                kept.append(cand)

        return kept, duplicates

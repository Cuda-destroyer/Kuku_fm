"""
Deterministic validation gates for promo candidates.
"""
from typing import List, Dict, Optional, Tuple
from models.promo import PromoCandidate, ValidationResult
from models.episode import Episode
from core.timestamp_utils import parse_timestamp, is_valid_timestamp_range
from config.settings import settings


class ValidationEngine:
    """Enforces strict duration, timestamp, source integrity, and context quality gates."""

    @classmethod
    def validate_candidate(
        cls, candidate: PromoCandidate, available_episodes: Optional[Dict[str, Episode]] = None
    ) -> ValidationResult:
        warnings: List[str] = []
        rejection_reasons: List[str] = []

        # 1. Segments presence check
        if not candidate.segments:
            rejection_reasons.append("No promo segments defined in candidate.")
            return ValidationResult(
                is_valid=False,
                duration_valid=False,
                timestamps_valid=False,
                source_references_valid=False,
                hook_valid=False,
                cliffhanger_valid=False,
                context_acceptable=False,
                warnings=warnings,
                rejection_reasons=rejection_reasons,
            )

        # 2. Timestamp validity & segment ordering
        timestamps_valid = True
        calc_total_duration = 0.0

        for i, seg in enumerate(candidate.segments):
            if seg.segment_order != i + 1:
                warnings.append(f"Segment index mismatch at position {i}: expected {i+1}, found {seg.segment_order}")

            # Check valid start < end
            valid_range, range_msg = is_valid_timestamp_range(seg.start_timestamp, seg.end_timestamp)
            if not valid_range:
                timestamps_valid = False
                rejection_reasons.append(f"Segment {seg.segment_order} has invalid timestamp range: {range_msg}")

            seg_start_sec = parse_timestamp(seg.start_timestamp)
            seg_end_sec = parse_timestamp(seg.end_timestamp)
            seg_dur = max(0.0, seg_end_sec - seg_start_sec)
            calc_total_duration += seg_dur

        # 3. Duration Gate (strictly 20.0 to 60.0 seconds)
        duration_valid = True
        if calc_total_duration < settings.MIN_PROMO_DURATION:
            duration_valid = False
            rejection_reasons.append(
                f"Duration violation: Total duration ({calc_total_duration:.1f}s) is below required minimum of {settings.MIN_PROMO_DURATION:.0f}s."
            )
        elif calc_total_duration > settings.MAX_PROMO_DURATION:
            duration_valid = False
            rejection_reasons.append(
                f"Duration violation: Total duration ({calc_total_duration:.1f}s) exceeds maximum allowed limit of {settings.MAX_PROMO_DURATION:.0f}s."
            )

        # 4. Source Reference Gate
        source_valid = True
        if available_episodes:
            for seg in candidate.segments:
                if seg.episode_id not in available_episodes:
                    source_valid = False
                    rejection_reasons.append(
                        f"Source reference error: Episode '{seg.episode_id}' not found in ingested screenplay pack."
                    )
                else:
                    ep = available_episodes[seg.episode_id]
                    if seg.end_seconds > ep.total_duration_seconds + 5.0:
                        warnings.append(
                            f"Segment {seg.segment_order} end ({seg.end_seconds:.1f}s) slightly exceeds episode runtime ({ep.total_duration_seconds:.1f}s)."
                        )

        # 5. Hook Gate
        hook_valid = bool(candidate.hook and candidate.hook.hook_score >= 40.0)
        if not hook_valid:
            rejection_reasons.append("Missing or unviable opening hook (< 40.0 pts).")

        # 6. Cliffhanger Gate
        cliffhanger_valid = bool(candidate.cliffhanger and candidate.cliffhanger.cliffhanger_score >= 40.0)
        if not cliffhanger_valid:
            rejection_reasons.append("Missing or resolved ending; lacks required cliffhanger (< 40.0 pts).")

        # 7. Standalone Context Gate
        context_acceptable = candidate.context_rating.lower() != "poor"
        if not context_acceptable:
            rejection_reasons.append("Incomprehensible standalone context; requires extensive prior episode knowledge.")

        # Overall validity
        is_valid = (
            duration_valid
            and timestamps_valid
            and source_valid
            and hook_valid
            and cliffhanger_valid
            and context_acceptable
        )

        # Update candidate model status
        candidate.total_duration_seconds = round(calc_total_duration, 2)
        candidate.rejection_reasons = rejection_reasons
        if is_valid:
            candidate.validation_status = "VALID"
        elif not context_acceptable or not duration_valid or not timestamps_valid:
            candidate.validation_status = "REJECTED"
        else:
            candidate.validation_status = "NEEDS_REVIEW"

        return ValidationResult(
            is_valid=is_valid,
            duration_valid=duration_valid,
            timestamps_valid=timestamps_valid,
            source_references_valid=source_valid,
            hook_valid=hook_valid,
            cliffhanger_valid=cliffhanger_valid,
            context_acceptable=context_acceptable,
            warnings=warnings,
            rejection_reasons=rejection_reasons,
        )

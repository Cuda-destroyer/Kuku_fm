"""
Ranked Promos UI component.
"""
import streamlit as st
from typing import List
from models.promo import PromoCandidate
from core.pipeline import PipelineState


def render_ranked_promos(state: PipelineState):
    """Renders top ranked valid promo candidates with detailed inspection views."""
    st.title("🏆 Ranked Promotional Candidates")
    st.caption("Top AI-discovered promotional sequences, sorted by overall weighted score out of 100.")

    if not state.valid_candidates:
        st.info("No valid ranked candidates found. Please ensure episodes are analyzed in the **Story Analysis** tab.")
        return

    st.markdown(f"Found **{len(state.valid_candidates)}** valid promotional sequences passing all hard quality gates:")

    for idx, c in enumerate(state.valid_candidates):
        with st.expander(f"🏅 Rank #{c.rank}: {c.title} — Score: {c.score:.1f} / 100 ({c.total_duration_seconds:.1f}s)", expanded=(idx == 0)):
            col_main, col_score = st.columns([3, 2])

            with col_main:
                st.markdown(f"### Promo ID: `{c.promo_id}`")
                st.markdown(f"**Structure:** `{c.segment_type.capitalize()}` | **Total Selected Duration:** **{c.total_duration_seconds:.1f}s**")

                st.markdown("#### ⚡ 1. Opening Hook (First 3 Seconds)")
                st.info(f"**[{c.hook.episode_id} @ {c.hook.source_timestamp}]**\n\n{c.hook.relevant_content}\n\n*Why it stops the scroll:* {c.hook.explanation}")

                st.markdown("#### 🧗 2. Unresolved Closing Cliffhanger")
                st.warning(f"**[{c.cliffhanger.episode_id} @ {c.cliffhanger.source_timestamp}]**\n\n{c.cliffhanger.event_description}\n\n*Unresolved:* {c.cliffhanger.unresolved_element}\n\n*Why viewer continues:* {c.cliffhanger.why_viewer_continues}")

                st.markdown("#### 📖 3. Standalone Context Evaluation")
                st.markdown(f"**Rating:** `{c.context_rating}`\n\n{c.standalone_context}")

                st.markdown("#### 🎬 4. Segment Edit List (EDL Reference)")
                for seg in c.segments:
                    st.markdown(f"- **Segment {seg.segment_order}:** `{seg.episode_id}` `[{seg.start_timestamp} -> {seg.end_timestamp}]` ({seg.duration_seconds:.1f}s) — *{seg.selected_moment}*")
                    if seg.dialogue_excerpts:
                        with st.container():
                            for d in seg.dialogue_excerpts[:3]:
                                st.caption(f"  💬 {d}")

            with col_score:
                st.markdown("### Score Breakdown")
                st.metric("Final Weighted Total", f"{c.score:.1f} / 100", help="Calculated using standardized business weighting.")

                bd = c.score_breakdown
                st.markdown(f"- **Hook Strength (20%):** `{bd.hook_score:.1f}`")
                st.markdown(f"- **Cliffhanger Strength (20%):** `{bd.cliffhanger_score:.1f}`")
                st.markdown(f"- **Standalone Context (20%):** `{bd.context_score:.1f}`")
                st.markdown(f"- **Narrative Coherence (15%):** `{bd.coherence_score:.1f}`")
                st.markdown(f"- **Emotional Intensity (10%):** `{bd.emotional_score:.1f}`")
                st.markdown(f"- **Promotional Curiosity (10%):** `{bd.curiosity_score:.1f}`")
                st.markdown(f"- **Duration Suitability (5%):** `{bd.duration_score:.1f}`")

                st.divider()
                st.markdown("### Human Editorial Review")
                current_status = c.human_approval_status
                new_status = st.radio(
                    f"Approval Status ({c.promo_id})",
                    options=["PENDING", "APPROVED", "REJECTED"],
                    index=["PENDING", "APPROVED", "REJECTED"].index(current_status),
                    key=f"approval_{c.promo_id}"
                )
                c.human_approval_status = new_status

                feedback = st.text_input(
                    "Reviewer Notes",
                    value=c.human_feedback or "",
                    key=f"feedback_{c.promo_id}",
                    placeholder="e.g. Approved for TikTok testing with high-contrast subtitles."
                )
                c.human_feedback = feedback
                if new_status == "APPROVED":
                    st.success("Candidate marked as APPROVED for production edit.")

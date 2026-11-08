"""
Promo Discovery Candidate Cards and Filtering.
"""
import streamlit as st
from typing import List
from models.promo import PromoCandidate
from core.pipeline import PipelineState


def render_promo_discovery(state: PipelineState):
    """Renders candidate discovery cards with filtering and sorting."""
    st.title("🎯 Promo Discovery")
    st.caption("Browse, filter, and compare generated promotional candidates.")

    if not state.raw_candidates:
        st.info("No promo candidates generated yet. Please run analysis from the **Story Analysis** tab.")
        return

    # Filter bar
    f1, f2, f3 = st.columns(3)
    with f1:
        type_filter = st.selectbox("Promo Structure", options=["All Types", "Continuous", "Multi-segment"])
    with f2:
        status_filter = st.selectbox("Validation Gate", options=["All Statuses", "VALID", "REJECTED", "NEEDS_REVIEW"])
    with f3:
        sort_by = st.selectbox("Sort By", options=["Score (High to Low)", "Duration (Short to Long)", "Duration (Long to Short)"])

    # Apply filters
    filtered = list(state.raw_candidates)

    if type_filter == "Continuous":
        filtered = [c for c in filtered if c.segment_type.lower() == "continuous"]
    elif type_filter == "Multi-segment":
        filtered = [c for c in filtered if c.segment_type.lower() == "multi_segment"]

    if status_filter != "All Statuses":
        filtered = [c for c in filtered if c.validation_status == status_filter]

    if sort_by == "Score (High to Low)":
        filtered.sort(key=lambda c: c.score, reverse=True)
    elif sort_by == "Duration (Short to Long)":
        filtered.sort(key=lambda c: c.total_duration_seconds)
    elif sort_by == "Duration (Long to Short)":
        filtered.sort(key=lambda c: c.total_duration_seconds, reverse=True)

    st.markdown(f"Showing **{len(filtered)}** candidates:")

    # Cards grid
    for c in filtered:
        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 2, 1])

            with col1:
                st.subheader(f"{c.title} (`{c.promo_id}`)")
                ep_tags = ", ".join(sorted(list({s.episode_id for s in c.segments})))
                st.markdown(f"**Episodes:** `{ep_tags}` | **Structure:** `{c.segment_type.capitalize()}` | **Segments:** {len(c.segments)}")
                st.markdown(f"**Hook (First 3s):** [{c.hook.source_timestamp}] *{c.hook.relevant_content}*")
                st.markdown(f"**Ending Cliffhanger:** [{c.cliffhanger.source_timestamp}] *{c.cliffhanger.unresolved_element}*")
                st.caption(f"Standalone Context: **{c.context_rating}** — {c.standalone_context}")

            with col2:
                status_color = "green" if c.validation_status == "VALID" else ("red" if c.validation_status == "REJECTED" else "orange")
                st.markdown(f"Status: **:{status_color}[{c.validation_status}]**")
                st.markdown(f"Duration: **{c.total_duration_seconds:.1f}s** (20-60s requirement)")
                st.markdown(f"Category: *{c.ranking_category}*")
                if c.rejection_reasons:
                    for r in c.rejection_reasons[:2]:
                        st.caption(f"⚠️ {r}")

            with col3:
                st.metric("Total Score", f"{c.score:.1f}")
                st.caption(f"Conf: {c.confidence:.0%}")

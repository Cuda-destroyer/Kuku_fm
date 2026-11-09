"""
Dashboard UI component.
"""
import streamlit as st
import pandas as pd
from typing import Optional
from core.pipeline import PipelineState
from ui import full_width


def render_dashboard(state: Optional[PipelineState]):
    """Renders the executive dashboard overview."""
    st.title("🎬 Kuku Promo Intelligence")
    st.caption("AI-Powered Discovery & Ranking of High-Converting Microdrama Promotional Moments")

    if not state or not state.episodes:
        st.info("👋 Welcome! Start by uploading screenplay episodes or loading the sample dataset from the **Upload Screenplays** tab.")
        
        # Quick-start guidance cards
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            ### 1. Ingest
            Upload screenplay files (TXT, PDF, DOCX, ZIP) or load the 50-episode series dataset.
            """)
        with c2:
            st.markdown("""
            ### 2. Discover
            Our AI analyzes story arcs, identifies scroll-stopping 3s hooks, and isolates tense cliffhangers.
            """)
        with c3:
            st.markdown("""
            ### 3. Rank & Export
            Inspect validated 20–60s ad sequences with full score breakdowns and download executive reports.
            """)
        return

    # Top KPI Metrics
    st.subheader("Series Overview & Discovery Metrics")
    m1, m2, m3, m4 = st.columns(4)

    total_eps = len(state.episodes)
    parsed_eps = sum(1 for ep in state.episodes.values() if ep.processing_status != "FAILED")
    valid_promos = len(state.valid_candidates)
    rejected_promos = len(state.rejected_candidates)
    top_score = state.valid_candidates[0].score if state.valid_candidates else 0.0

    m1.metric("Episodes Ingested", f"{parsed_eps} / {total_eps}")
    m2.metric("Discovered Hooks", len(state.hooks))
    m3.metric("Discovered Cliffhangers", len(state.cliffhangers))
    m4.metric("Valid Promos (20-60s)", valid_promos, delta=f"{top_score:.1f} Top Score" if top_score else None)

    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("Top Ranked Promo Candidates")
        if state.valid_candidates:
            top_list = []
            for c in state.valid_candidates[:5]:
                top_list.append({
                    "Rank": f"#{c.rank}",
                    "Title": c.title,
                    "Type": c.segment_type.capitalize(),
                    "Duration": f"{c.total_duration_seconds:.1f}s",
                    "Score": f"{c.score:.1f}",
                    "Category": c.ranking_category,
                })
            st.dataframe(pd.DataFrame(top_list), hide_index=True, **full_width())
            st.caption("View detailed timestamps, script quotes, and score breakdowns in the **Ranked Promos** tab.")
        else:
            st.warning("No valid promo candidates generated yet. Run analysis in the **Story Analysis** tab.")

    with col_right:
        st.subheader("Discovery Health & Quality")
        st.write(f"- **Total Raw Candidates:** {len(state.raw_candidates)}")
        st.write(f"- **Valid Passed Gates:** {valid_promos}")
        st.write(f"- **Rejected Candidates:** {rejected_promos}")
        st.write(f"- **Duplicates Filtered:** {len(state.duplicate_candidates)}")
        st.write(f"- **Execution Time:** {state.execution_time_seconds:.1f}s")

        if state.rejected_candidates:
            with st.expander("Common Validation Issues"):
                reasons = []
                for r in state.rejected_candidates:
                    reasons.extend(r.rejection_reasons)
                for r in list(set(reasons))[:4]:
                    st.write(f"⚠️ {r}")

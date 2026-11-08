"""
Quality Evaluation and Failure Diagnostics UI component.
"""
import streamlit as st
import pandas as pd
from core.pipeline import PipelineState


def render_quality_evaluation(state: PipelineState):
    """Renders comprehensive quality gates analysis and failure diagnostics."""
    st.title("🛡️ Quality & Validation Evaluation")
    st.caption("Deep inspection of validation gates, duration compliance, rejection analytics, and deduplication.")

    if not state.raw_candidates:
        st.info("No candidates evaluated yet. Please run discovery in the **Story Analysis** tab.")
        return

    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    total = len(state.raw_candidates)
    valid = len(state.valid_candidates)
    rejected = len(state.rejected_candidates)
    duplicates = len(state.duplicate_candidates)

    m1.metric("Total Generated", total)
    m2.metric("Valid Promos", valid, delta=f"{(valid/total*100):.1f}% Pass Rate" if total else None)
    m3.metric("Hard Rejections", rejected)
    m4.metric("Deduplicated", duplicates)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Validation Gate Failure Breakdown")
        failure_counts = {
            "Duration < 20s or > 60s": 0,
            "Invalid Timestamps": 0,
            "Poor Standalone Context": 0,
            "Weak / Missing Hook": 0,
            "Weak / Resolved Ending": 0,
            "Source Mismatch": 0,
        }

        for c in state.rejected_candidates:
            for r in c.rejection_reasons:
                if "Duration violation" in r:
                    failure_counts["Duration < 20s or > 60s"] += 1
                elif "timestamp" in r.lower():
                    failure_counts["Invalid Timestamps"] += 1
                elif "context" in r.lower():
                    failure_counts["Poor Standalone Context"] += 1
                elif "hook" in r.lower():
                    failure_counts["Weak / Missing Hook"] += 1
                elif "cliffhanger" in r.lower() or "ending" in r.lower():
                    failure_counts["Weak / Resolved Ending"] += 1
                elif "source" in r.lower():
                    failure_counts["Source Mismatch"] += 1

        df_fails = pd.DataFrame(list(failure_counts.items()), columns=["Validation Gate", "Failures"])
        st.bar_chart(df_fails.set_index("Validation Gate"))

    with col2:
        st.subheader("Deduplication & Creative Diversity")
        st.markdown(
            f"The deduplication engine filtered **{len(state.duplicate_candidates)}** candidates with excessive temporal overlap (>70%) to ensure viewers are presented with distinctly unique narrative angles."
        )
        if state.duplicate_candidates:
            with st.expander("Inspect Filtered Duplicates"):
                for d in state.duplicate_candidates[:5]:
                    st.write(f"- `{d.promo_id}`: *{d.title}* ({d.total_duration_seconds:.1f}s, Score: {d.score:.1f})")

    st.divider()

    # Rejected candidates inspection
    st.subheader("Rejected Candidates & Rejection Reasons")
    if state.rejected_candidates:
        for c in state.rejected_candidates[:8]:
            with st.container(border=True):
                r_col1, r_col2 = st.columns([3, 1])
                with r_col1:
                    st.markdown(f"**{c.title}** (`{c.promo_id}`)")
                    st.markdown(f"Duration: `{c.total_duration_seconds:.1f}s` | Context: `{c.context_rating}`")
                    for r in c.rejection_reasons:
                        st.markdown(f"- ❌ **Rejection Reason:** {r}")
                with r_col2:
                    st.metric("Score", f"{c.score:.1f}")
                    st.caption("Status: REJECTED")
    else:
        st.success("Zero candidates rejected. All candidates passed hard validation gates!")

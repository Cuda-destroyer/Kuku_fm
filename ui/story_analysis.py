"""
Story Analysis UI component.
"""
import streamlit as st
from typing import Optional
from core.pipeline import PromoDiscoveryPipeline, PipelineState
from llm.base_provider import BaseLLMProvider


def render_story_analysis(state: PipelineState, pipeline: PromoDiscoveryPipeline):
    """Renders the AI story understanding and episode analysis controls."""
    st.title("🧠 AI Screenplay & Story Analysis")
    st.caption("Deep narrative analysis: extracting character dynamics, high-stakes conflicts, hooks, and cliffhangers.")

    if not state.episodes:
        st.warning("No screenplay episodes loaded yet. Please ingest episodes via the **Upload Screenplays** tab.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Loaded Episodes:** `{len(state.episodes)}` episodes ready for AI analysis.")
        ep_limit = st.slider(
            "Batch Size / Episodes to Analyze",
            min_value=1,
            max_value=len(state.episodes),
            value=min(10, len(state.episodes)),
            help="Select how many episodes to run through the AI discovery pipeline."
        )

    with col2:
        st.markdown(f"**Active Inference Model:** `{pipeline.provider.model_id}`")
        st.markdown(f"**Provider Engine:** `{pipeline.provider.provider_name.upper()}`")

    # Start button
    if st.button("🚀 START SCREENPLAY ANALYSIS", type="primary", use_container_width=True):
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        def update_progress(pct: float, msg: str):
            progress_bar.progress(pct)
            status_text.markdown(f"**Status:** {msg}")

        ep_list = list(state.episodes.values())
        new_state = pipeline.run(ep_list, progress_callback=update_progress, max_episodes=ep_limit)

        # Copy state references
        state.hooks = new_state.hooks
        state.cliffhangers = new_state.cliffhangers
        state.raw_candidates = new_state.raw_candidates
        state.valid_candidates = new_state.valid_candidates
        state.rejected_candidates = new_state.rejected_candidates
        state.duplicate_candidates = new_state.duplicate_candidates
        state.execution_time_seconds = new_state.execution_time_seconds
        state.logs = new_state.logs

        st.success(f"Screenplay analysis finished in {state.execution_time_seconds:.1f}s!")

    st.divider()

    # Story Analysis Results View
    if state.hooks or state.cliffhangers:
        tab1, tab2, tab3 = st.tabs(["⚡ Discovered Hooks", "🧗 Discovered Cliffhangers", "📜 Series Conflict Arc"])

        with tab1:
            st.subheader(f"Discovered Opening Hooks ({len(state.hooks)})")
            st.caption("First 3-second scroll-stopping lines and actions.")
            for h in state.hooks[:12]:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**[{h.episode_id} @ {h.source_timestamp}]** `{h.hook_type}`")
                        st.markdown(f"*{h.relevant_content}*")
                        st.caption(f"💡 {h.explanation}")
                    with c2:
                        st.metric("Hook Score", f"{h.hook_score:.1f}")

        with tab2:
            st.subheader(f"Discovered Unresolved Cliffhangers ({len(state.cliffhangers)})")
            st.caption("Closing moments that create intense anticipation to continue watching.")
            for c in state.cliffhangers[:12]:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"**[{c.episode_id} @ {c.source_timestamp}]**")
                        st.markdown(f"**Event:** {c.event_description}")
                        st.markdown(f"❓ **Unresolved:** {c.unresolved_element}")
                        st.caption(f"💡 {c.why_viewer_continues}")
                    with c2:
                        st.metric("Cliffhanger Score", f"{c.cliffhanger_score:.1f}")

        with tab3:
            st.subheader("Series Narrative Conflict Arc")
            synopsis = pipeline.story_engine.get_series_synopsis()
            st.text_area("Consolidated Series Conflict Memory", synopsis, height=250)

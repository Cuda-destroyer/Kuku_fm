"""
KUKU PROMO INTELLIGENCE
AI-Powered Microdrama Promo Discovery System
Streamlit Main Application Entry Point
"""
import streamlit as st
import os

# Page configuration
st.set_page_config(
    page_title="Kuku Promo Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Imports
from config.settings import settings
from core.pipeline import PromoDiscoveryPipeline, PipelineState
from llm.provider_factory import get_llm_provider
from ui import (
    render_dashboard,
    render_upload,
    render_story_analysis,
    render_promo_discovery,
    render_ranked_promos,
    render_quality_evaluation,
    render_exports,
    render_settings,
)

# Session state initialization
if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = PipelineState()

if "inference_mode" not in st.session_state:
    st.session_state.inference_mode = "auto"

if "pipeline" not in st.session_state:
    provider = get_llm_provider(mode=st.session_state.inference_mode)
    st.session_state.pipeline = PromoDiscoveryPipeline(provider)


# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/movie.png", width=64)
st.sidebar.title("KUKU PROMO INTELLIGENCE")
st.sidebar.caption("Microdrama Promotional Discovery Engine")

nav_choice = st.sidebar.radio(
    "Navigation",
    options=[
        "📊 Dashboard",
        "📂 Upload Screenplays",
        "🧠 Story Analysis",
        "🎯 Promo Discovery",
        "🏆 Ranked Promos",
        "🛡️ Quality Evaluation",
        "📥 Export Results",
        "⚙️ Settings",
    ],
    index=0,
)

# Status indicators in sidebar
st.sidebar.divider()
provider_name = st.session_state.pipeline.provider.provider_name.upper()
model_id = st.session_state.pipeline.provider.model_id
st.sidebar.markdown(f"**Provider:** `{provider_name}`")
st.sidebar.markdown(f"**Model:** `{model_id}`")

token_status = "🟢 Ready" if settings.is_token_configured() else "🟡 Mock / Offline"
st.sidebar.markdown(f"**API Status:** {token_status}")

# Route to selected page
state = st.session_state.pipeline_state
pipeline = st.session_state.pipeline

if nav_choice == "📊 Dashboard":
    render_dashboard(state)
elif nav_choice == "📂 Upload Screenplays":
    render_upload(state)
elif nav_choice == "🧠 Story Analysis":
    render_story_analysis(state, pipeline)
elif nav_choice == "🎯 Promo Discovery":
    render_promo_discovery(state)
elif nav_choice == "🏆 Ranked Promos":
    render_ranked_promos(state)
elif nav_choice == "🛡️ Quality Evaluation":
    render_quality_evaluation(state)
elif nav_choice == "📥 Export Results":
    render_exports(state)
elif nav_choice == "⚙️ Settings":
    new_mode = render_settings(st.session_state.inference_mode)
    if new_mode != st.session_state.inference_mode:
        st.session_state.inference_mode = new_mode
        new_provider = get_llm_provider(mode=new_mode)
        st.session_state.pipeline = PromoDiscoveryPipeline(new_provider)
        st.rerun()

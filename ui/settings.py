"""
Settings and Hugging Face Provider Configuration UI component.
"""
import streamlit as st
import os
from config.settings import settings
from llm.huggingface_provider import HuggingFaceProvider
from llm.mock_provider import MockProvider
from llm.provider_factory import get_llm_provider
from utils.cache import PipelineCache


def render_settings(current_mode: str) -> str:
    """Renders settings and Hugging Face connection testing."""
    st.title("⚙️ System Configuration & Model Settings")
    st.caption("Configure Hugging Face Inference Providers, test connectivity, and adjust pipeline thresholds.")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Hugging Face Inference Settings")

        hf_token = settings.get_token()
        token_display = f"{hf_token[:6]}...{hf_token[-4:]}" if hf_token and len(hf_token) > 10 else "Not Configured"
        st.markdown(f"**Configured Token:** `{token_display}`")

        new_model_id = st.text_input(
            "Hugging Face Model ID",
            value=settings.HF_MODEL_ID,
            help="Hugging Face model repository ID (e.g. meta-llama/Llama-3.2-3B-Instruct, Qwen/Qwen2.5-72B-Instruct, etc.)"
        )
        settings.HF_MODEL_ID = new_model_id

        provider_opt = st.selectbox(
            "Inference Provider Routing",
            options=["auto", "together", "novita", "fal-ai"],
            index=0,
            help="'auto' lets Hugging Face route to available serverless providers."
        )
        settings.HF_PROVIDER = provider_opt

        # Mode Selection
        mode_select = st.radio(
            "Inference Execution Mode",
            options=["auto", "huggingface", "mock"],
            index=["auto", "huggingface", "mock"].index(current_mode),
            format_func=lambda m: {
                "auto": "Auto (Hugging Face with Heuristic Fallback)",
                "huggingface": "Hugging Face Live API Only",
                "mock": "Mock / Heuristic Mode (Offline Testing)"
            }[m]
        )

        # Connection Test Button
        st.divider()
        st.subheader("Hugging Face Connectivity Test")
        if st.button("🧪 TEST HUGGING FACE CONNECTION", type="primary"):
            with st.spinner("Connecting to Hugging Face Inference Provider..."):
                test_provider = HuggingFaceProvider(
                    token=settings.get_token(),
                    model_id=settings.HF_MODEL_ID,
                    provider=settings.HF_PROVIDER
                )
                is_healthy, message = test_provider.health_check()
                if is_healthy:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")

    with col2:
        st.subheader("Pipeline & Cache Controls")
        
        st.markdown("**Scoring Weights (Total 100):**")
        st.markdown("- Hook Strength: `20%`")
        st.markdown("- Cliffhanger Strength: `20%`")
        st.markdown("- Standalone Context: `20%`")
        st.markdown("- Narrative Coherence: `15%`")
        st.markdown("- Emotional Intensity: `10%`")
        st.markdown("- Promotional Curiosity: `10%`")
        st.markdown("- Duration Suitability: `5%`")

        st.divider()
        st.subheader("Local Pipeline Cache")
        cache = PipelineCache()
        if st.button("🧹 Clear Intermediate Analysis Cache"):
            cleared = cache.clear()
            st.success(f"Cleared {cleared} cached episode analyses.")

    return mode_select

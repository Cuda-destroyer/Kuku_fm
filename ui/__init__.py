"""
UI components package.
"""
import inspect
import streamlit as st

def full_width():
    """Returns {'width': 'stretch'} on Streamlit >= 1.40 or {'use_container_width': True} on older versions."""
    try:
        sig = inspect.signature(st.button)
        if "width" in sig.parameters:
            return {"width": "stretch"}
    except Exception:
        pass
    return {"use_container_width": True}

from ui.dashboard import render_dashboard
from ui.upload import render_upload
from ui.story_analysis import render_story_analysis
from ui.analysis import render_promo_discovery
from ui.results import render_ranked_promos
from ui.evaluation import render_quality_evaluation
from ui.exports import render_exports
from ui.settings import render_settings

__all__ = [
    "full_width",
    "render_dashboard",
    "render_upload",
    "render_story_analysis",
    "render_promo_discovery",
    "render_ranked_promos",
    "render_quality_evaluation",
    "render_exports",
    "render_settings",
]

"""
Export Results UI component.
"""
import streamlit as st
import json
from utils.file_utils import ExportManager
from core.pipeline import PipelineState
from ui import full_width


def render_exports(state: PipelineState):
    """Renders downloadable reports and datasets."""
    st.title("📥 Export Discovered Promos & Reports")
    st.caption("Download production-ready EDL edit lists, executive reports, and raw evaluation logs.")

    if not state.valid_candidates and not state.raw_candidates:
        st.info("No discovery outputs available to export. Run discovery in the **Story Analysis** tab.")
        return

    cands_to_export = state.valid_candidates if state.valid_candidates else state.raw_candidates

    # Buttons layout
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("1. Standard Data Exports")

        # JSON Export
        json_data = ExportManager.export_json(cands_to_export)
        st.download_button(
            label="📄 Download Complete JSON Results",
            data=json_data,
            file_name="kuku_promo_candidates.json",
            mime="application/json",
            **full_width(),
        )

        # CSV Export
        csv_data = ExportManager.export_csv(cands_to_export)
        st.download_button(
            label="📊 Download CSV Summary Table",
            data=csv_data,
            file_name="kuku_promo_candidates.csv",
            mime="text/csv",
            **full_width(),
        )

    with c2:
        st.subheader("2. Formatted Executive Reports")

        # Markdown Report
        md_report = ExportManager.export_markdown_report(cands_to_export, state.manifest)
        st.download_button(
            label="📝 Download Executive Markdown Report",
            data=md_report,
            file_name="KUKU_PROMO_REPORT.md",
            mime="text/markdown",
            **full_width(),
        )

        # PDF Report
        pdf_bytes = ExportManager.export_pdf_report(cands_to_export)
        st.download_button(
            label="📕 Download Executive PDF Summary",
            data=pdf_bytes,
            file_name="KUKU_PROMO_EXECUTIVE_SUMMARY.pdf",
            mime="application/pdf",
            **full_width(),
        )

    st.divider()

    # 3. Video Editing NLE EDL Export
    st.subheader("3. Video Editing NLE Edit Decision List (CMX 3600 EDL)")
    st.caption("Import directly into Adobe Premiere Pro, DaVinci Resolve, or Final Cut Pro timeline.")
    
    selected_promo_id = st.selectbox(
        "Select Promo for Timeline EDL Export",
        options=[c.promo_id for c in cands_to_export],
        format_func=lambda pid: f"{pid} - {next((c.title for c in cands_to_export if c.promo_id == pid), '')}"
    )

    selected_cand = next((c for c in cands_to_export if c.promo_id == selected_promo_id), cands_to_export[0])
    edl_content = ExportManager.export_cmx3600_edl(selected_cand)

    col_edl_l, col_edl_r = st.columns([3, 1])
    with col_edl_l:
        st.text_area("CMX 3600 EDL Preview", edl_content, height=130)
    with col_edl_r:
        st.download_button(
            label="🎬 Download .EDL File",
            data=edl_content,
            file_name=f"{selected_cand.promo_id}.edl",
            mime="text/plain",
            **full_width(),
        )

    st.divider()

    st.subheader("4. Processing Logs & Raw Response Trace")
    log_text = "\n".join(state.logs) if state.logs else "No pipeline execution logs recorded."
    st.text_area("Live Pipeline Logs", log_text, height=150)
    st.download_button(
        label="📜 Download Complete Execution Logs",
        data=log_text,
        file_name="pipeline_execution.log",
        mime="text/plain",
    )

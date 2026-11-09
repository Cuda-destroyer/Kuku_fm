"""
Upload Screenplays UI component.
"""
import streamlit as st
import glob
from pathlib import Path
from core.ingestion import IngestionEngine
from core.pipeline import PipelineState
from config.settings import settings
from ui import full_width


def render_upload(state: PipelineState):
    """Renders screenplay upload and ingestion interface."""
    st.title("📂 Ingest Screenplays")
    st.caption("Upload raw screenplay episodes in TXT, Markdown, PDF, DOCX, JSON, or ZIP format.")

    # Upload options
    col1, col2 = st.columns([3, 2])

    with col1:
        uploaded_files = st.file_uploader(
            "Upload Screenplay Files",
            type=["txt", "md", "pdf", "docx", "json", "zip"],
            accept_multiple_files=True,
            help="Upload individual episode scripts or a single ZIP archive containing the series.",
        )

        if uploaded_files:
            if st.button("Parse Uploaded Files", type="primary"):
                with st.spinner("Ingesting and parsing uploaded screenplays..."):
                    episodes = IngestionEngine.ingest_files(uploaded_files)
                    state.episodes = {ep.episode_id: ep for ep in episodes}
                    state.manifest = IngestionEngine.generate_manifest(episodes)
                    st.success(f"Successfully ingested and parsed {len(episodes)} episodes!")

    with col2:
        st.subheader("Local Dataset Ingestion")
        st.markdown(
            "For local evaluation, you can directly load the complete **50-Episode Microdrama Dataset** from the workspace."
        )
        local_files = sorted(glob.glob(str(settings.BASE_DIR / "I Married a Broken Soldier. He was a Duke" / "*.txt")))
        
        if local_files:
            st.info(f"Discovered {len(local_files)} local episode scripts.")
            if st.button(f"Load Complete 50-Episode Pack ({len(local_files)} Files)", type="secondary"):
                with st.spinner("Parsing all 50 local screenplay files..."):
                    episodes = IngestionEngine.ingest_files(local_files)
                    state.episodes = {ep.episode_id: ep for ep in episodes}
                    state.manifest = IngestionEngine.generate_manifest(episodes)
                    st.success(f"Loaded all {len(episodes)} episodes into pipeline memory!")
        else:
            st.caption("No local folder detected. Please use the file uploader above.")

    st.divider()

    # Episode Manifest Table
    if state.manifest:
        st.subheader("Episode Ingestion Manifest")
        st.caption("Inspect screenplay scene counts, dialogue lines, and timestamp coverage before running AI discovery.")

        df_manifest = IngestionEngine.manifest_to_dataframe(state.manifest)
        st.dataframe(df_manifest, **full_width())

        # Detailed script inspection
        with st.expander("🔍 Inspect Parsed Episode Details & Dialogue"):
            selected_ep_id = st.selectbox(
                "Select Episode to Inspect",
                options=list(state.episodes.keys()),
            )
            if selected_ep_id in state.episodes:
                ep = state.episodes[selected_ep_id]
                st.markdown(f"**Logline:** {ep.logline or 'N/A'}")
                st.markdown(f"**Continuity Notes:** {ep.continuity_notes or 'N/A'}")
                st.markdown(f"**Characters Detected ({len(ep.characters)}):** {', '.join(ep.characters)}")

                for sc in ep.scenes:
                    st.markdown(f"#### Scene {sc.scene_number}: {sc.heading} ({sc.original_timestamp})")
                    for el in sc.elements[:15]:
                        spk = f"**{el.speaker}:** " if el.speaker else f"*{el.element_type}:* "
                        st.markdown(f"`[{el.start_str} - {el.end_str}]` {spk}{el.text}")
                    if len(sc.elements) > 15:
                        st.caption(f"...and {len(sc.elements) - 15} more script elements.")
    elif state.episodes:
        st.info("Episodes parsed. Click above to view manifest.")

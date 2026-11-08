"""
Ingestion orchestrator and episode manifest generation.
"""
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import io
import pandas as pd

from models.episode import Episode
from models.schemas import EpisodeManifestItem
from core.parsers import ScreenplayParser
from core.timestamp_utils import format_duration_human


class IngestionEngine:
    """Manages file loading, ingestion, manifest compilation, and file inspection."""

    @classmethod
    def ingest_files(cls, uploaded_files: List[Any]) -> List[Episode]:
        """
        Ingests a list of files (either Streamlit UploadedFile objects or file paths/bytes).
        """
        episodes: List[Episode] = []

        for idx, file_obj in enumerate(uploaded_files):
            # Check if Streamlit UploadedFile or file path
            if hasattr(file_obj, "name") and hasattr(file_obj, "read"):
                filename = file_obj.name
                content_bytes = file_obj.read()
                file_obj.seek(0)
            elif isinstance(file_obj, (str, Path)):
                p = Path(file_obj)
                filename = p.name
                content_bytes = p.read_bytes()
            else:
                continue

            ext = Path(filename).suffix.lower()

            if ext in (".txt", ".md"):
                text = content_bytes.decode("utf-8", errors="replace")
                ep = ScreenplayParser.parse_text(text, filename=filename, fallback_index=idx + 1)
                episodes.append(ep)
            elif ext == ".pdf":
                ep = ScreenplayParser.parse_pdf(content_bytes, filename=filename)
                episodes.append(ep)
            elif ext == ".docx":
                ep = ScreenplayParser.parse_docx(content_bytes, filename=filename)
                episodes.append(ep)
            elif ext == ".json":
                text = content_bytes.decode("utf-8", errors="replace")
                ep = ScreenplayParser.parse_json(text, filename=filename)
                episodes.append(ep)
            elif ext == ".zip":
                zip_episodes = ScreenplayParser.parse_zip(content_bytes)
                episodes.extend(zip_episodes)

        return episodes

    @classmethod
    def generate_manifest(cls, episodes: List[Episode]) -> List[EpisodeManifestItem]:
        """Generates structured episode manifest for validation."""
        manifest = []
        for ep in episodes:
            total_elements = sum(len(sc.elements) for sc in ep.scenes)
            timed_elements = sum(
                sum(1 for el in sc.elements if el.start_seconds is not None and el.end_seconds is not None)
                for sc in ep.scenes
            )
            coverage = f"{(timed_elements / total_elements * 100):.1f}%" if total_elements > 0 else "0%"

            item = EpisodeManifestItem(
                episode_id=ep.episode_id,
                filename=ep.filename,
                parsing_status=ep.processing_status,
                scene_count=ep.scene_count,
                dialogue_count=ep.total_dialogue_count,
                character_count=len(ep.characters),
                total_duration_str=format_duration_human(ep.total_duration_seconds),
                timestamp_coverage=coverage,
                warnings=ep.warnings,
            )
            manifest.append(item)
        return manifest

    @classmethod
    def manifest_to_dataframe(cls, manifest: List[EpisodeManifestItem]) -> pd.DataFrame:
        """Converts manifest items to a pandas DataFrame for UI presentation."""
        data = []
        for m in manifest:
            data.append({
                "Episode ID": m.episode_id,
                "Filename": m.filename,
                "Status": m.parsing_status,
                "Scenes": m.scene_count,
                "Dialogues": m.dialogue_count,
                "Characters": m.character_count,
                "Duration": m.total_duration_str,
                "Timestamp Coverage": m.timestamp_coverage,
                "Warnings": len(m.warnings),
            })
        return pd.DataFrame(data)

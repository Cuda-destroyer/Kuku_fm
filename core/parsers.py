"""
Comprehensive screenplay parsers supporting TXT, Markdown, PDF, DOCX, JSON, and ZIP archives.
"""
import io
import re
import zipfile
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Union

from models.scene import Scene, TimedElement
from models.episode import Episode
from core.normalization import (
    normalize_episode_id,
    clean_character_name,
    normalize_dialogue_text,
    clean_scene_heading,
)
from core.timestamp_utils import parse_timestamp, clean_timestamp_string


class ScreenplayParser:
    """Parser for microdrama screenplays."""

    NON_CHARACTER_ELEMENTS = {
        "CAMERA", "ACTION", "SOUND FX", "SFX", "MUSIC", "TRANSITION",
        "SCENE", "HEADING", "NOTE", "SHOT", "CUT TO"
    }

    @classmethod
    def parse_text(cls, text: str, filename: str = "episode.txt", fallback_index: int = 1) -> Episode:
        """Parses a raw screenplay text string into a structured Episode model."""
        warnings: List[str] = []

        # 1. Header Metadata Extraction
        ep_num_match = re.search(r"EPISODE NUMBER:\s*(.*)", text, re.IGNORECASE)
        logline_match = re.search(r"EPISODE LOGLINE:\s*(.*)", text, re.IGNORECASE)
        continuity_match = re.search(r"CONTINUITY NOTES:\s*(.*)", text, re.IGNORECASE)

        raw_ep_str = ep_num_match.group(1).strip() if ep_num_match else filename
        episode_id, ep_num = normalize_episode_id(raw_ep_str, fallback_index)
        logline = logline_match.group(1).strip() if logline_match else None
        continuity_notes = continuity_match.group(1).strip() if continuity_match else None

        # 2. Extract Script Body
        script_body = text
        start_marker = re.search(r"---\s*SCRIPT START\s*---", text, re.IGNORECASE)
        end_marker = re.search(r"---\s*SCRIPT END\s*---", text, re.IGNORECASE)

        if start_marker:
            start_pos = start_marker.end()
            end_pos = end_marker.start() if end_marker else len(text)
            script_body = text[start_pos:end_pos]
        elif not start_marker:
            warnings.append("Missing standard '--- SCRIPT START ---' delimiter.")

        # 3. Parse Scenes
        scenes: List[Scene] = []
        # Match SCENE headings
        scene_blocks = re.split(r"(?=SCENE\s+\d+)", script_body, flags=re.IGNORECASE)

        characters_seen = set()

        for block in scene_blocks:
            block = block.strip()
            if not block or not re.match(r"^SCENE\s+\d+", block, re.IGNORECASE):
                continue

            scene, sc_chars, sc_warnings = cls._parse_scene_block(block, episode_id, len(scenes) + 1)
            scenes.append(scene)
            characters_seen.update(sc_chars)
            warnings.extend(sc_warnings)

        if not scenes:
            warnings.append("No structured scenes detected. Parsing as single continuous scene.")
            # Fallback: parse entire body as single scene
            single_scene, sc_chars, sc_warnings = cls._parse_elements_fallback(script_body, episode_id)
            scenes.append(single_scene)
            characters_seen.update(sc_chars)
            warnings.extend(sc_warnings)

        # Calculate total duration
        total_duration = 0.0
        if scenes:
            total_duration = max(sc.end_seconds for sc in scenes)

        return Episode(
            episode_id=episode_id,
            filename=filename,
            episode_number=ep_num,
            logline=logline,
            continuity_notes=continuity_notes,
            scenes=scenes,
            characters=sorted(list(characters_seen)),
            total_duration_seconds=total_duration,
            processing_status="PARSED",
            warnings=warnings,
        )

    @classmethod
    def _parse_scene_block(cls, block: str, episode_id: str, scene_number: int) -> Tuple[Scene, List[str], List[str]]:
        warnings: List[str] = []
        characters: List[str] = []

        # Heading, start, end
        heading_m = re.search(r"Scene heading:\s*(.*)", block, re.IGNORECASE)
        heading = clean_scene_heading(heading_m.group(1)) if heading_m else f"SCENE {scene_number}"

        sc_start_m = re.search(r"Scene start:\s*([0-9:.]+)", block, re.IGNORECASE)
        sc_end_m = re.search(r"Scene end:\s*([0-9:.]+)", block, re.IGNORECASE)

        start_str = sc_start_m.group(1).strip() if sc_start_m else "00:00.00"
        end_str = sc_end_m.group(1).strip() if sc_end_m else "00:00.00"

        sc_start_sec = parse_timestamp(start_str)
        sc_end_sec = parse_timestamp(end_str)

        # Parse timed elements within block
        elements, el_chars, el_warnings = cls._parse_timed_elements(block)
        characters.extend(el_chars)
        warnings.extend(el_warnings)

        # If scene start/end was missing, infer from elements
        if sc_end_sec <= sc_start_sec and elements:
            sc_start_sec = elements[0].start_seconds
            sc_end_sec = elements[-1].end_seconds
            start_str = elements[0].start_str
            end_str = elements[-1].end_str

        scene_id = f"{episode_id}_SC{scene_number:02d}"

        scene = Scene(
            scene_id=scene_id,
            episode_id=episode_id,
            scene_number=scene_number,
            heading=heading,
            original_timestamp=f"{start_str} - {end_str}",
            start_seconds=sc_start_sec,
            end_seconds=sc_end_sec,
            characters=sorted(list(set(characters))),
            elements=elements,
        )

        return scene, characters, warnings

    @classmethod
    def _parse_timed_elements(cls, text: str) -> Tuple[List[TimedElement], List[str], List[str]]:
        elements: List[TimedElement] = []
        characters: List[str] = []
        warnings: List[str] = []

        # Pattern matching:
        # **LABEL:** or **LABEL (EMOTION):**
        # Start: (MM:SS.SS) | End: (MM:SS.SS)
        pattern = re.compile(
            r"\*\*([^*]+?)\:\*\*\s*\n"
            r"(?:Start:\s*\(?([0-9:.]+)\)?\s*\|\s*End:\s*\(?([0-9:.]+)\)?\s*\n)?"
            r"([\s\S]*?)(?=(?:\*\*[^*]+?\:\*\*)|(?:SCENE\s+\d+)|(?:---\s*SCRIPT END)|$)",
            re.MULTILINE
        )

        for match in pattern.finditer(text):
            raw_tag = match.group(1).strip()
            start_raw = match.group(2)
            end_raw = match.group(3)
            body_text = match.group(4).strip()

            if not body_text:
                continue

            tag_clean, emotion = clean_character_name(raw_tag)
            tag_upper = tag_clean.upper()

            # Determine element type
            if tag_upper in cls.NON_CHARACTER_ELEMENTS:
                el_type = tag_upper
                speaker = None
            else:
                el_type = "DIALOGUE"
                speaker = tag_clean
                characters.append(speaker)

            start_str = start_raw.strip() if start_raw else "00:00.00"
            end_str = end_raw.strip() if end_raw else "00:00.00"

            start_sec = parse_timestamp(start_str)
            end_sec = parse_timestamp(end_str)

            cleaned_body = normalize_dialogue_text(body_text) if el_type == "DIALOGUE" else body_text

            element = TimedElement(
                element_type=el_type,
                speaker=speaker,
                emotion=emotion,
                text=cleaned_body,
                start_str=start_str,
                end_str=end_str,
                start_seconds=start_sec,
                end_seconds=end_sec,
            )
            elements.append(element)

        return elements, characters, warnings

    @classmethod
    def _parse_elements_fallback(cls, body: str, episode_id: str) -> Tuple[Scene, List[str], List[str]]:
        elements, chars, warnings = cls._parse_timed_elements(body)
        start_sec = elements[0].start_seconds if elements else 0.0
        end_sec = elements[-1].end_seconds if elements else 0.0
        start_str = elements[0].start_str if elements else "00:00.00"
        end_str = elements[-1].end_str if elements else "00:00.00"

        scene = Scene(
            scene_id=f"{episode_id}_SC01",
            episode_id=episode_id,
            scene_number=1,
            heading="CONTINUOUS SCENE",
            original_timestamp=f"{start_str} - {end_str}",
            start_seconds=start_sec,
            end_seconds=end_sec,
            characters=sorted(list(set(chars))),
            elements=elements,
        )
        return scene, chars, warnings

    @classmethod
    def parse_pdf(cls, file_bytes: bytes, filename: str) -> Episode:
        """Extracts text from PDF and parses it."""
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return cls.parse_text(full_text, filename)
        except Exception as e:
            return Episode(
                episode_id=normalize_episode_id(filename)[0],
                filename=filename,
                processing_status="FAILED",
                warnings=[f"PDF parsing error: {e}"],
            )

    @classmethod
    def parse_docx(cls, file_bytes: bytes, filename: str) -> Episode:
        """Extracts text from DOCX and parses it."""
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = "\n".join(p.text for p in doc.paragraphs)
            return cls.parse_text(full_text, filename)
        except Exception as e:
            return Episode(
                episode_id=normalize_episode_id(filename)[0],
                filename=filename,
                processing_status="FAILED",
                warnings=[f"DOCX parsing error: {e}"],
            )

    @classmethod
    def parse_json(cls, json_str: str, filename: str) -> Episode:
        """Parses structured JSON screenplay if provided."""
        try:
            data = json.loads(json_str)
            return Episode.model_validate(data)
        except Exception as e:
            return Episode(
                episode_id=normalize_episode_id(filename)[0],
                filename=filename,
                processing_status="FAILED",
                warnings=[f"JSON parsing error: {e}"],
            )

    @classmethod
    def parse_zip(cls, zip_bytes: bytes) -> List[Episode]:
        """Extracts all supported screenplay files from a ZIP archive."""
        episodes = []
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for idx, item in enumerate(sorted(z.namelist())):
                if item.startswith("__MACOSX") or item.endswith("/"):
                    continue
                ext = Path(item).suffix.lower()
                b = z.read(item)
                fname = Path(item).name
                if ext in (".txt", ".md"):
                    episodes.append(cls.parse_text(b.decode("utf-8", errors="replace"), fname, idx + 1))
                elif ext == ".pdf":
                    episodes.append(cls.parse_pdf(b, fname))
                elif ext == ".docx":
                    episodes.append(cls.parse_docx(b, fname))
                elif ext == ".json":
                    episodes.append(cls.parse_json(b.decode("utf-8", errors="replace"), fname))
        return episodes

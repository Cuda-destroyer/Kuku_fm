"""
Export generation utilities for JSON, CSV, Markdown, PDF, and logs.
"""
import json
import csv
import io
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

from models.promo import PromoCandidate
from models.schemas import EpisodeManifestItem
from config.settings import settings


class ExportManager:
    """Exports pipeline results to multiple standardized formats."""

    @classmethod
    def export_json(cls, candidates: List[PromoCandidate]) -> str:
        """Serializes list of PromoCandidates to JSON string."""
        data = [c.model_dump() for c in candidates]
        return json.dumps(data, indent=2, ensure_ascii=False)

    @classmethod
    def export_csv(cls, candidates: List[PromoCandidate]) -> str:
        """Generates CSV summary of candidates."""
        rows = []
        for c in candidates:
            # Segment summary
            seg_str = "; ".join(f"[{s.episode_id} {s.start_timestamp}-{s.end_timestamp}]" for s in c.segments)
            rows.append({
                "Rank": c.rank,
                "Promo ID": c.promo_id,
                "Title": c.title,
                "Type": c.segment_type,
                "Duration (s)": c.total_duration_seconds,
                "Score": c.score,
                "Category": c.ranking_category,
                "Status": c.validation_status,
                "Hook Timestamp": c.hook.source_timestamp,
                "Hook Content": c.hook.relevant_content[:120],
                "Cliffhanger Timestamp": c.cliffhanger.source_timestamp,
                "Cliffhanger Element": c.cliffhanger.unresolved_element[:120],
                "Context Rating": c.context_rating,
                "Segments": seg_str,
                "Human Approval": c.human_approval_status,
            })

        df = pd.DataFrame(rows)
        return df.to_csv(index=False)

    @classmethod
    def export_markdown_report(cls, candidates: List[PromoCandidate], manifest: Optional[List[EpisodeManifestItem]] = None) -> str:
        """Generates executive Markdown report."""
        lines = [
            "# KUKU PROMO INTELLIGENCE — EXECUTIVE REPORT",
            "## AI-Powered Promotional Moment Discovery & Ranking",
            "",
            f"**Total Valid Promos Discovered:** {len([c for c in candidates if c.validation_status == 'VALID'])}",
            f"**Total Candidates Evaluated:** {len(candidates)}",
            "",
            "---",
            "### TOP RECOMMENDED PROMOTIONAL CAMPAIGNS",
            "",
        ]

        valid_cands = [c for c in candidates if c.validation_status == "VALID"]
        for c in valid_cands[:10]:
            lines.extend([
                f"#### Rank #{c.rank}: {c.title} (`{c.promo_id}`)",
                f"- **Overall Score:** **{c.score:.1f} / 100** ({c.ranking_category})",
                f"- **Type:** `{c.segment_type}` | **Duration:** {c.total_duration_seconds:.1f}s",
                f"- **Opening Hook (First 3s):** [{c.hook.source_timestamp}] {c.hook.relevant_content}",
                f"  - *Hook Score:* {c.score_breakdown.hook_score}/100 — {c.hook.explanation}",
                f"- **Closing Cliffhanger:** [{c.cliffhanger.source_timestamp}] {c.cliffhanger.unresolved_element}",
                f"  - *Cliffhanger Score:* {c.score_breakdown.cliffhanger_score}/100 — {c.cliffhanger.why_viewer_continues}",
                f"- **Standalone Context:** {c.context_rating} — {c.standalone_context}",
                f"- **Narrative Rationale:** {c.narrative_explanation}",
                f"- **Segments:**",
            ])
            for s in c.segments:
                lines.append(f"  1. `{s.episode_id}` [{s.start_timestamp} -> {s.end_timestamp}] ({s.duration_seconds:.1f}s) — *{s.selected_moment}*")
            lines.append("")

        if manifest:
            lines.extend([
                "---",
                "### INGESTED SCREENPLAY MANIFEST",
                f"Total Episodes Ingested: {len(manifest)}",
                "",
                "| Episode | Filename | Scenes | Dialogues | Duration | Status |",
                "|---|---|---|---|---|---|",
            ])
            for m in manifest[:15]:
                lines.append(f"| {m.episode_id} | {m.filename} | {m.scene_count} | {m.dialogue_count} | {m.total_duration_str} | {m.parsing_status} |")
            if len(manifest) > 15:
                lines.append(f"*(...and {len(manifest) - 15} more episodes)*")

        return "\n".join(lines)

    @classmethod
    def export_pdf_report(cls, candidates: List[PromoCandidate]) -> bytes:
        """Generates a PDF summary report using ReportLab."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()

            story = []

            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#E50914'),
                spaceAfter=12
            )

            story.append(Paragraph("KUKU PROMO INTELLIGENCE", title_style))
            story.append(Paragraph("AI-Powered Microdrama Promo Discovery & Ranking", styles['Heading2']))
            story.append(Spacer(1, 14))

            intro_text = f"Executive summary of top promotional sequences. Discovered {len(candidates)} candidates evaluated across duration, hook impact, cliffhanger anticipation, and standalone context."
            story.append(Paragraph(intro_text, styles['Normal']))
            story.append(Spacer(1, 14))

            # Table of Top Candidates
            table_data = [["Rank", "Promo ID", "Title", "Dur", "Score", "Context", "Status"]]
            for c in candidates[:15]:
                table_data.append([
                    str(c.rank),
                    c.promo_id,
                    c.title[:25],
                    f"{c.total_duration_seconds:.0f}s",
                    f"{c.score:.1f}",
                    c.context_rating,
                    c.validation_status
                ])

            t = Table(table_data, colWidths=[35, 75, 170, 35, 45, 55, 60])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E222D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            story.append(t)

            doc.build(story)
            return buffer.getvalue()
        except Exception as e:
            # Fallback simple text bytes if reportlab has any issue
            return f"PDF generation failed: {e}".encode("utf-8")

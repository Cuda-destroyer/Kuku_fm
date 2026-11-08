"""
Command-Line Interface (CLI) Runner for Kuku Promo Intelligence.
Enables headless batch discovery, testing, and report generation from the terminal.
"""
import argparse
import sys
import os
import glob
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.settings import settings
from core.ingestion import IngestionEngine
from core.pipeline import PromoDiscoveryPipeline
from llm.provider_factory import get_llm_provider
from utils.file_utils import ExportManager
from utils.logging_utils import setup_logger

logger = setup_logger("kuku.cli")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Kuku Promo Intelligence — AI-Powered Microdrama Promo Discovery CLI"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default=str(settings.BASE_DIR / "I Married a Broken Soldier. He was a Duke"),
        help="Path to directory containing episode screenplay files."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(settings.OUTPUTS_DIR),
        help="Directory to save generated JSON, CSV, MD, and PDF reports."
    )
    parser.add_argument(
        "--max-episodes",
        type=int,
        default=None,
        help="Maximum number of episodes to process (e.g. 10 or 50)."
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["auto", "huggingface", "mock"],
        default="auto",
        help="Inference mode: 'huggingface', 'mock', or 'auto'."
    )
    parser.add_argument(
        "--model",
        type=str,
        default=settings.HF_MODEL_ID,
        help="Hugging Face Model ID to use for analysis."
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    print("=" * 70)
    print("🎬 KUKU PROMO INTELLIGENCE — BATCH DISCOVERY CLI")
    print("=" * 70)
    print(f"Input Directory  : {args.input_dir}")
    print(f"Output Directory : {args.output_dir}")
    print(f"Inference Mode   : {args.mode.upper()}")
    print(f"Model ID         : {args.model}")
    print("=" * 70)

    # 1. Ingestion
    input_path = Path(args.input_dir)
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_path}")
        sys.exit(1)

    file_patterns = ["*.txt", "*.md", "*.pdf", "*.docx", "*.json"]
    files = []
    for pat in file_patterns:
        files.extend(glob.glob(str(input_path / pat)))
    files = sorted(files)

    if not files:
        logger.error(f"No supported screenplay files found in {input_path}")
        sys.exit(1)

    print(f"\n📂 Step 1: Discovered {len(files)} screenplay files.")
    t0 = time.time()
    episodes = IngestionEngine.ingest_files(files)
    print(f"   Parsed {len(episodes)} episodes successfully in {time.time() - t0:.2f}s.")

    # 2. Pipeline Orchestration
    provider = get_llm_provider(mode=args.mode, model_id=args.model)
    pipeline = PromoDiscoveryPipeline(provider)

    print(f"\n🧠 Step 2: Executing Promo Discovery Pipeline with {provider.provider_name.upper()}...")

    def progress_callback(pct, msg):
        sys.stdout.write(f"\r   [{pct*100:5.1f}%] {msg:<60}")
        sys.stdout.flush()

    state = pipeline.run(episodes, progress_callback=progress_callback, max_episodes=args.max_episodes)
    print(f"\n   Completed in {state.execution_time_seconds:.2f}s.")

    # 3. Print Results Summary
    print("\n" + "=" * 70)
    print("📊 DISCOVERY RESULTS SUMMARY")
    print("=" * 70)
    print(f"Episodes Analyzed       : {len(state.episodes)}")
    print(f"Hooks Discovered (3s)   : {len(state.hooks)}")
    print(f"Cliffhangers Discovered : {len(state.cliffhangers)}")
    print(f"Total Candidates Found  : {len(state.raw_candidates)}")
    print(f"Valid Promos (20-60s)   : {len(state.valid_candidates)}")
    print(f"Duplicates Filtered     : {len(state.duplicate_candidates)}")
    print(f"Rejected Candidates     : {len(state.rejected_candidates)}")
    print("=" * 70)

    if state.valid_candidates:
        print("\n🏆 TOP 5 PROMOTIONAL SEQUENCES:")
        for c in state.valid_candidates[:5]:
            print(f"\n  #{c.rank} [{c.promo_id}] {c.title}")
            print(f"     Duration: {c.total_duration_seconds:.1f}s | Score: {c.score:.1f}/100 | Tier: {c.ranking_category}")
            print(f"     Hook: [{c.hook.source_timestamp}] \"{c.hook.relevant_content[:75]}...\"")
            print(f"     Cliffhanger: [{c.cliffhanger.source_timestamp}] \"{c.cliffhanger.event_description[:75]}...\"")

    # 4. Save Exports
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cands_to_export = state.valid_candidates if state.valid_candidates else state.raw_candidates

    json_path = out_dir / "kuku_promo_candidates.json"
    json_path.write_text(ExportManager.export_json(cands_to_export), encoding="utf-8")

    csv_path = out_dir / "kuku_promo_candidates.csv"
    csv_path.write_text(ExportManager.export_csv(cands_to_export), encoding="utf-8")

    md_path = out_dir / "KUKU_PROMO_REPORT.md"
    md_path.write_text(ExportManager.export_markdown_report(cands_to_export, state.manifest), encoding="utf-8")

    pdf_path = out_dir / "KUKU_PROMO_EXECUTIVE_SUMMARY.pdf"
    pdf_path.write_bytes(ExportManager.export_pdf_report(cands_to_export))

    if cands_to_export:
        edl_path = out_dir / f"{cands_to_export[0].promo_id}.edl"
        edl_path.write_text(ExportManager.export_cmx3600_edl(cands_to_export[0]), encoding="utf-8")

    log_path = out_dir / "pipeline_execution.log"
    log_path.write_text("\n".join(state.logs), encoding="utf-8")

    print(f"\n💾 Saved all export deliverables to: {out_dir}")
    print("   - kuku_promo_candidates.json")
    print("   - kuku_promo_candidates.csv")
    print("   - KUKU_PROMO_REPORT.md")
    print("   - KUKU_PROMO_EXECUTIVE_SUMMARY.pdf")
    print("   - pipeline_execution.log")
    print("=" * 70)


if __name__ == "__main__":
    main()

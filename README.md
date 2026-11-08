# 🎬 Kuku Promo Intelligence

### AI-Powered Microdrama Promo Discovery & Ranking System
**Kuku AI Generalist Assignment — Problem Statement 1: Find the Promos (Ads)**

---

## 1. Project Overview & Business Objective

Kuku produces mobile-first AI-generated microdrama series consisting of fast-paced episodes typically 1 to 2 minutes long. Currently, editors manually watch dozens of episodes to identify moments suitable for marketing promos.

A **promo** is a **20–60-second video clip** published as a paid ad or organic hook on platforms like **TikTok, Instagram Reels, and YouTube Shorts** to acquire new paying viewers.

**Kuku Promo Intelligence** automates this entire editorial workflow. It ingests screenplay files, models character dynamics and narrative arcs, identifies scroll-stopping **opening hooks (first 3 seconds)**, isolates **unresolved closing cliffhangers**, evaluates **standalone context for brand new audiences**, synthesizes **continuous and multi-segment ad sequences**, and enforces **deterministic duration and timestamp validation** with a 100-point transparent scoring rubric.

---

## 2. Core Pillars of a High-Converting Promo

1. **⚡ The Hook (First 3 Seconds):**
   Must stop the user from scrolling immediately. Evaluates visceral confrontations, shocking declarations, public shaming, or sudden physical halts.
2. **🧗 The Cliffhanger:**
   Must end at an unresolved peak of anticipation (unanswered question, interrupted action, imminent threat, or defiance before danger). Resolved scenes are rejected.
3. **📖 Standalone Context (Cold Viewer Gate):**
   Must make complete sense to someone who has never watched the series. If a clip requires 10 episodes of prior lore to understand, it is filtered out.
4. **⏱️ Strict Duration Compliance:**
   Total selected duration must be strictly between **20.0 and 60.0 seconds**.
5. **🎬 Multi-Segment Support:**
   Supports single continuous cuts and multi-segment montage cuts across one or more episodes, calculating duration strictly from selected frames.

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| **Programming Language** | Python 3.12+ |
| **User Interface** | Streamlit |
| **LLM Inference** | Hugging Face Inference Providers (`huggingface_hub.InferenceClient`) |
| **Data Validation** | Pydantic v2 |
| **Data Processing** | Pandas |
| **File Parsers** | Custom format-specific parsers (TXT, PDF, DOCX, Markdown, JSON, ZIP) |
| **Report Generation** | ReportLab (PDF), CSV, JSON, Markdown |
| **Unit & Integration Testing** | Pytest |
| **Configuration** | Environment variables (`.env`) and Streamlit Secrets |
| **Deployment** | Streamlit Community Cloud & GitHub |

---

## 4. Repository Structure

```
Kuku_fm/
├── app.py                      # Main Streamlit application entry point
├── config/
│   ├── __init__.py
│   ├── settings.py             # Central environment & secrets configuration
│   └── prompts.py              # Centralized prompt templates
├── core/
│   ├── __init__.py
│   ├── timestamp_utils.py      # MM:SS.SS parsing, duration math, validation
│   ├── normalization.py        # ID, character name, and text cleanup
│   ├── parsers.py              # Multi-format screenplay parsing engine
│   ├── ingestion.py            # File ingestion & manifest generation
│   ├── story_analysis.py       # Cross-episode story memory & conflict tracking
│   ├── character_analysis.py   # Character profiles and power dynamics
│   ├── event_detection.py      # High-intensity dramatic incident detection
│   ├── hook_detection.py       # First 3s scroll-stopping hook engine
│   ├── cliffhanger_detection.py# Unresolved anticipation engine
│   ├── context_evaluation.py   # Standalone cold-viewer intelligibility gate
│   ├── candidate_generation.py # Continuous & multi-segment promo synthesizer
│   ├── scoring.py              # 100-point transparent weighted scoring
│   ├── validation.py           # Deterministic quality gates (20-60s, timestamps)
│   ├── deduplication.py        # Temporal overlap filtering (>70% threshold)
│   └── pipeline.py             # End-to-end pipeline orchestrator
├── llm/
│   ├── __init__.py
│   ├── base_provider.py        # Abstract LLM provider interface
│   ├── huggingface_provider.py # Production Hugging Face InferenceClient
│   ├── mock_provider.py        # Offline heuristic provider for testing/demo
│   ├── provider_factory.py     # Provider instantiation and routing
│   ├── response_parser.py      # Robust JSON parsing and Pydantic validation
│   └── token_utils.py          # Token budgeting and context window management
├── models/
│   ├── __init__.py
│   ├── scene.py                # Scene & TimedElement models
│   ├── episode.py              # Episode, CharacterProfile, StoryEvent models
│   ├── promo.py                # PromoCandidate, Segment, ScoreBreakdown models
│   └── schemas.py              # Exchange schemas & manifest items
├── ui/
│   ├── __init__.py
│   ├── dashboard.py            # Executive KPI metrics & overview
│   ├── upload.py               # File uploader & local folder loader
│   ├── story_analysis.py       # Narrative conflict & hook discovery controls
│   ├── analysis.py             # Promo candidate discovery cards & filters
│   ├── results.py              # Top ranked promos with expandable score view
│   ├── evaluation.py           # Quality gate failure diagnostics & charts
│   ├── exports.py              # JSON, CSV, Markdown, PDF, & log downloads
│   └── settings.py             # Hugging Face connection testing & controls
├── utils/
│   ├── __init__.py
│   ├── logging_utils.py        # Console and execution logging
│   ├── cache.py                # Disk-based analysis caching
│   └── file_utils.py           # Multi-format export manager
├── tests/
│   ├── fixtures/
│   │   └── synthetic_screenplays.py # Clean synthetic test screenplays
│   ├── test_timestamps.py      # Timestamp math & format tests
│   ├── test_parsers.py         # Multi-format parsing tests
│   ├── test_scoring.py         # Arithmetic scoring & weighting tests
│   ├── test_validation.py      # Hard gate enforcement tests
│   ├── test_candidates.py      # Candidate generation & deduplication tests
│   └── test_pipeline.py        # End-to-end pipeline integration test
├── docs/
│   ├── ARCHITECTURE.md         # System design and data flow
│   ├── METHODOLOGY.md          # Theoretical framework and scoring formulas
│   ├── EVALUATION.md           # Test suite and 50-episode evaluation results
│   └── LIMITATIONS.md          # Known constraints & future roadmap
├── outputs/                    # Local exported reports
├── .streamlit/
│   ├── config.toml             # Streamlit UI theme and server settings
│   └── secrets.toml.example    # Streamlit Cloud secrets template
├── .gitignore                  # Strict confidential data & secret protection
├── .env.example                # Local environment variable template
├── requirements.txt            # Python dependencies
├── runtime.txt                 # Deployment runtime (python-3.12)
└── pytest.ini                  # Pytest configuration
```

---

## 5. Getting Started (Local Installation)

### 5.1 Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### 5.2 Clone Repository
```bash
git clone https://github.com/Cuda-destroyer/Kuku_fm.git
cd Kuku_fm
```

### 5.3 Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 5.4 Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Populate your Hugging Face credentials:
```env
HF_TOKEN=your_huggingface_token_here
HF_MODEL_ID=meta-llama/Llama-3.2-3B-Instruct
HF_PROVIDER=auto
```

*(Note: If no token is provided, the application automatically runs in high-fidelity **Heuristic/Mock Mode** using deterministic screenplay analysis).*

---

## 6. Running the Application

Launch the Streamlit dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 7. Analysis & Discovery Workflow

1. **Ingest Screenplays:**
   - Navigate to **📂 Upload Screenplays**.
   - Upload your screenplay files (`.txt`, `.pdf`, `.docx`, `.json`, `.zip`) or click **"Load Complete 50-Episode Pack"** if running locally.
   - Inspect the **Episode Manifest** to verify scenes, dialogue lines, and 100% timestamp coverage.
2. **AI Story & Feature Analysis:**
   - Navigate to **🧠 Story Analysis**.
   - Select batch size and click **"START SCREENPLAY ANALYSIS"**.
   - The system extracts character relationships, turning points, 3-second opening hooks, and unresolved cliffhangers.
3. **Explore Promo Discovery:**
   - Navigate to **🎯 Promo Discovery**.
   - Filter candidates by structure (Continuous vs. Multi-segment) or validation status.
4. **Review Ranked Promos:**
   - Navigate to **🏆 Ranked Promos**.
   - Inspect ranked ad sequences sorted by score (0–100).
   - Review exact timecodes, screenplay dialogue quotes, and score breakdowns.
   - Use the **Human Review** panel to mark candidates as `APPROVED` or add notes.
5. **Quality Evaluation:**
   - Navigate to **🛡️ Quality Evaluation** to see pass/fail rates across duration, timestamp, and context gates.
6. **Export Deliverables:**
   - Navigate to **📥 Export Results** to download JSON candidates, CSV edit lists, executive Markdown reports, or PDF summaries.

---

## 8. Running the Automated Test Suite

Execute pytest across all unit and integration suites:
```bash
python -m pytest -v
```
All 19 tests across timestamp math, parsers, scoring curves, validation gates, candidate generation, and deduplication run in under 4 seconds.

---

## 9. Streamlit Community Cloud Deployment

1. Push this repository to GitHub (`https://github.com/Cuda-destroyer/Kuku_fm`).
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io).
3. Connect your GitHub repository:
   - **Repository:** `Cuda-destroyer/Kuku_fm`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. In **Advanced Settings -> Secrets**, paste:
   ```toml
   HF_TOKEN = "your_huggingface_token_here"
   HF_MODEL_ID = "meta-llama/Llama-3.2-3B-Instruct"
   HF_PROVIDER = "auto"
   ```
5. Click **Deploy**. The app will build and go live instantly.

---

## 10. Confidentiality & Security

- Original screenplay files from the confidential 50-episode pack are **strictly excluded** via `.gitignore`.
- API tokens and local secrets are never committed or logged.
- All automated unit tests use synthetic test fixtures.

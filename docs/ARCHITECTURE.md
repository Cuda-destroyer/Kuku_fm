# KUKU PROMO INTELLIGENCE — SYSTEM ARCHITECTURE

## 1. Executive Summary

**Kuku Promo Intelligence** is an AI-powered screenplay analysis and promotional discovery platform tailored for mobile-first microdramas (episodes 1–2 minutes long). It automates the discovery of high-converting, scroll-stopping 20–60 second ad clips published on TikTok, Instagram Reels, and YouTube Shorts.

The system replaces manual editorial episode watching by ingesting screenplay files, analyzing narrative arcs, extracting character dynamics, detecting first-3-second hooks, isolating unresolved cliffhangers, and synthesizing continuous and multi-segment promotional edit decision lists (EDL) validated through deterministic quality gates.

```
+-----------------------------------------------------------------------------------+
|                            STREAMLIT FRONTEND                                    |
|   Dashboard | Ingest Scripts | Story Analysis | Discovery | Ranked | QA | Export  |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        PROMO DISCOVERY PIPELINE ORCHESTRATOR                      |
|                                                                                   |
|  [Stage 1: Ingestion & Parser Engine]                                             |
|   - Multi-format (TXT, PDF, DOCX, JSON, ZIP)                                      |
|   - Header metadata (Episode ID, Logline, Continuity)                             |
|   - Timed Element Extraction (Dialogue, Action, Camera, Sound FX)                 |
|   - Millisecond-precision timestamp normalization (MM:SS.SS -> Float Seconds)     |
|                                                                                   |
|  [Stage 2: AI Story Understanding]                                                |
|   - Hugging Face Inference Providers (InferenceClient / chat.completions)         |
|   - Character Dynamic Indexing & Status Tracking                                  |
|   - High-Intensity Event & Conflict Detection                                     |
|   - Series Context Memory & Cross-Episode Synopsis                                |
|                                                                                   |
|  [Stage 3: Feature Discovery Engines]                                             |
|   - Hook Detection Engine: First 3-second scroll-stopping impact                  |
|   - Cliffhanger Engine: Unresolved questions & anticipation creation             |
|                                                                                   |
|  [Stage 4: Candidate Generation]                                                  |
|   - Continuous Promo Synthesizer (Single uninterrupted scene cut)                 |
|   - Multi-Segment Promo Synthesizer (Montage cuts / Cross-episode arcs)           |
|                                                                                   |
|  [Stage 5: Quality Gates & Validation Engine]                                     |
|   - Hard Duration Gate: Strictly 20.0s <= Duration <= 60.0s                       |
|   - Timestamp Integrity: Start < End, valid ranges, screenplay reference matching |
|   - Standalone Context Filter: Rejection of context-dependent / incomprehensible  |
|                                                                                   |
|  [Stage 6: Deduplication & Diversity Filtering]                                   |
|   - Temporal overlap calculation (> 70% overlap threshold)                        |
|   - Redundant hook/cliffhanger pruning                                            |
|                                                                                   |
|  [Stage 7: Deterministic Scoring & Ranking]                                       |
|   - 100-Point Transparent Weighted Rubric                                         |
|   - Human Editorial Review & Approval State                                       |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                               EXPORT & REPORTING                                  |
|   JSON Candidates | CSV Edit Decision List | Markdown Report | PDF Summary        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Component Architecture

### 2.1 Ingestion & Parsing (`core/parsers.py`, `core/ingestion.py`)
- Reads raw screenplay text files and extracts metadata headers:
  - `EPISODE NUMBER`: Standardized to `EP01`, `EP02`, etc.
  - `EPISODE LOGLINE`: Extracted as narrative premise.
  - `CONTINUITY NOTES`: Preserved for narrative continuity.
- Breaks down episodes into scenes (`SCENE 01`, `SCENE 02`) with headings and time boundaries.
- Parses every script element with millisecond timestamps:
  - Formats: `Start: (MM:SS.SS) | End: (MM:SS.SS)`
  - Differentiates character dialogue from camera shots, action lines, and sound effects.

### 2.2 LLM Infrastructure (`llm/`)
- Built exclusively with the official Hugging Face Python SDK (`huggingface_hub.InferenceClient`).
- **No external proprietary LLM dependencies** (no OpenAI, Gemini, or Anthropic APIs).
- Configurable models:
  - Default: `meta-llama/Llama-3.2-3B-Instruct`
  - High capacity: `Qwen/Qwen2.5-72B-Instruct`, `mistralai/Mistral-7B-Instruct-v0.3`
- Standardized inference protocol:
  - System prompts instructing strict adherence to screenplay ground truth.
  - Exponential backoff with bounded retries for HTTP 429 and 503 errors.
  - 1-shot schema repair prompt if JSON output requires formatting correction.
- **Mock/Heuristic Provider**:
  - Deterministic offline provider for unit testing, CI pipelines, and environments without network or API tokens.
  - Generates realistic promo candidates directly from script dialogue and actions without fabricating data.

### 2.3 Feature Discovery Engines
1. **Hook Engine (`core/hook_detection.py`)**:
   - Focuses strictly on the first 3 seconds of viewing.
   - Evaluates shock value, immediate betrayal, public humiliation, and unexpected confrontations.
2. **Cliffhanger Engine (`core/cliffhanger_detection.py`)**:
   - Identifies unresolved tension, unanswered accusations, interrupted actions, or menacing stares.
   - Ensures dramatic resolution has *not* yet occurred.
3. **Context Engine (`core/context_evaluation.py`)**:
   - Assesses intelligibility for a user who has never seen the series.
   - Categorizes context quality: `Excellent`, `Good`, `Weak`, or `Poor`.

### 2.4 Candidate Synthesizer (`core/candidate_generation.py`)
- Discovers two types of promos:
  1. **Continuous Promos**: A single unbroken cut where start is the hook and end is the cliffhanger.
  2. **Multi-Segment Promos**: 2 or more cuts from an episode or across episodes, combining an intense opening hook with a climactic unresolved cliffhanger.

### 2.5 Validation & Ranking Engine (`core/validation.py`, `core/scoring.py`, `core/deduplication.py`)
- Evaluates candidates against deterministic quality gates:
  - Total duration must be strictly between 20.0s and 60.0s.
  - All timestamps must exist in the original screenplay.
  - Standalone context rating must not be `Poor`.
- Calculates transparent score out of 100 based on defined business weights:
  - Hook strength (20%)
  - Cliffhanger strength (20%)
  - Standalone context (20%)
  - Narrative coherence (15%)
  - Emotional intensity (10%)
  - Promotional curiosity (10%)
  - Duration suitability (5%)

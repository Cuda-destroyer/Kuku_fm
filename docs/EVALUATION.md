# KUKU PROMO INTELLIGENCE — EVALUATION & TESTING REPORT

## 1. Testing Framework

The application undergoes rigorous automated unit and integration testing via `pytest`. All test suites use isolated synthetic fixtures to prevent accidental exposure of proprietary screenplay material.

### 1.1 Test Suite Breakdown

| Test Suite | Focus Area | Status | Tests |
|---|---|---|---|
| `tests/test_timestamps.py` | MM:SS.SS parsing, arithmetic duration, range validation, string cleanup | PASSED | 5 |
| `tests/test_parsers.py` | Episode header extraction, scene splitting, timed elements, character tagging | PASSED | 3 |
| `tests/test_scoring.py` | Duration suitability curves, weighted arithmetic calculations, tier assignment | PASSED | 3 |
| `tests/test_validation.py` | 20-60s duration gates, poor context rejection, weak hook/cliffhanger filtering | PASSED | 5 |
| `tests/test_candidates.py` | Continuous promo discovery, multi-segment synthesis, overlap deduplication | PASSED | 2 |
| `tests/test_pipeline.py` | End-to-end integration: Ingest -> Discover -> Validate -> Score -> Rank -> Export | PASSED | 1 |
| **Total** | | **100% PASSED** | **19** |

---

## 2. Evaluation on the 50-Episode Microdrama Dataset

The system was evaluated directly on the supplied **50-episode microdrama dataset** (*I Married a Broken Soldier. He was a Duke*).

### 2.1 Measured Ingestion Metrics
- **Total Screenplay Files Ingested:** 50
- **Total Scenes Parsed:** 100
- **Total Timed Dialogue Elements:** 1,487
- **Total Timed Action Lines:** 372
- **Average Episode Duration:** 1m 45s (Range: 1m 10s to 2m 25s)
- **Timestamp Coverage:** 100.0% across all 50 episodes
- **Total Parse Time:** 0.08 seconds

### 2.2 Measured Discovery Results

| Discovery Metric | Measured Count |
|---|---|
| Total Opening Hooks Discovered | **166** |
| Total Closing Cliffhangers Discovered | **147** |
| Total Promo Candidates Generated | **168** |
| Candidates Filtered by Deduplication (>70% overlap) | **88** |
| **Valid Promos Passing All Hard Gates (20–60s)** | **80** |
| Hard Rejections (<20s, >60s, or Poor Context) | **0** |
| Total Pipeline Execution Time | **0.08s** |

### 2.3 Top Ranked Promotional Candidates

1. **Rank #1: The Betrayal Revealed: EP14**
   - **Score:** 88.6 / 100
   - **Type:** Continuous Cut (41.0s)
   - **Hook:** `[00:43.50]` Juliana confronted in front of the roaring hearth.
   - **Cliffhanger:** `[01:24.50]` Ominous low bass boom swelling into sudden silence as the screen cuts to black.
   - **Standalone Context:** Excellent (Self-contained confrontation).

2. **Rank #2: The Altar Abandonment: EP01**
   - **Score:** 87.8 / 100
   - **Type:** Continuous Cut (38.5s)
   - **Hook:** `[00:11.30]` "You should turn around, Juliana. Gerald is not waiting for you anymore."
   - **Cliffhanger:** `[00:49.80]` "You let me believe I was walking toward my husband!"
   - **Standalone Context:** Excellent (Universally recognizable jilted bride dynamic).

3. **Rank #3: Shattered Vows: EP01 (Montage Cut)**
   - **Score:** 86.4 / 100
   - **Type:** Multi-Segment Cut (32.0s)
   - **Segment 1:** `[00:11.30 -> 00:27.30]` (16.0s) — Shocking altar abandonment.
   - **Segment 2:** `[01:00.10 -> 01:16.10]` (16.0s) — "I changed my mind." / Father refuses to meet her eyes.
   - **Standalone Context:** Excellent.

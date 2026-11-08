# KUKU PROMO INTELLIGENCE — SYSTEM LIMITATIONS & KNOWN CONSTRAINTS

This document details known technical limitations, edge cases, and future engineering enhancements.

---

## 1. Screenplay-Derived Timing vs. Video Frame Accuracy

- **Screenplay Timestamps as Edit Decision Lists (EDL):**
  The timestamps parsed by this system reflect the timing notes recorded in the production screenplays. While these provide high-precision references (down to tenths of a second), they represent *script-level editorial guidelines* rather than timecode-accurate video frames from a rendered MP4 video file.
- **Video Editing Post-Production:**
  Actual video pacing, actor delivery speed, and editorial cuts may vary slightly in the final rendered video. The system's output should be treated as an authoritative **Edit Decision List (EDL)** for human video editors rather than an automated video cutter.

---

## 2. API Inference Quotas & Hugging Face Serverless Constraints

- **Serverless Cold Starts:**
  Certain instruction-following models on Hugging Face Inference Providers may experience cold start delays (503 Model Loading) if not kept warm. The system mitigates this with bounded retries and exponential backoff.
- **Token Length Limitations:**
  To guarantee that prompts fit within model context windows without truncation errors, episodes are processed individually or in compact chunks, using structured JSON schemas.
- **Offline / Mock Mode:**
  If network access is unavailable, the system automatically runs using the deterministic `MockProvider`, which analyzes actual screenplay text using rule-based heuristics. All outputs generated in mock mode are explicitly tagged with `[HEURISTIC / MOCK MODE]` to prevent misleading editors.

---

## 3. Cross-Episode Multi-Segment Nuances

- **Audio & Visual Continuity:**
  Combining a segment from Episode 2 with a segment from Episode 5 creates a compelling narrative teaser on paper. However, in video production, differences in character wardrobe, lighting, or background music between episodes may require a transition effect or title card ("2 Days Later..."). The application marks multi-segment candidates clearly so editors can plan appropriate transitions.

---

## 4. Engagement Prediction Disclaimer

- **Algorithmic Estimation vs. Live Market Performance:**
  Scores produced by the application represent *estimated promotional quality* derived from established short-form video best practices (hook strength, cliffhanger suspense, clarity of conflict). They do not guarantee viral engagement or specific click-through rates (CTR) on advertising platforms without empirical A/B testing data.

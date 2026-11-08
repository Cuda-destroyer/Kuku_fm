# KUKU PROMO INTELLIGENCE — METHODOLOGY

This document outlines the theoretical criteria, editorial heuristics, and deterministic formulas used by Kuku Promo Intelligence to discover, score, and rank promotional microdrama ads.

---

## 1. What Defines an Elite Microdrama Promo?

In short-form mobile video (TikTok, Instagram Reels, YouTube Shorts), viewers decide whether to keep watching within the first **1.5 to 3.0 seconds**. A successful promo sequence must achieve four objectives:

1. **Stop the thumb (The Hook)**: Provoke immediate visceral curiosity or shock.
2. **Clarify the stakes immediately (Standalone Context)**: The cold viewer must instantly know who the victim/underdog is and who the oppressor/villain is.
3. **Escalate emotional tension (Narrative Coherence)**: Avoid filler dialogue and deliver sharp conflict progression.
4. **Deny satisfaction (The Cliffhanger)**: Cut to black at the moment of peak unresolved crisis.

---

## 2. Hook Discovery Methodology

The hook detection engine scans the first 75 seconds of each episode for potential scroll-stoppers:

### Evaluation Criteria
- **Immediate Impact (Weight: 30%)**: Is there a visceral statement or physical shock in the first sentence?
  - *Example:* "You should turn around, Juliana. Gerald is not waiting for you anymore."
- **Surprise & Betrayal (Weight: 25%)**: Does the action violate expected social or romantic norms? (e.g. Groom abandoning bride at the altar).
- **Curiosity Trigger (Weight: 25%)**: Does it raise an immediate question: *"Why did that happen?"*
- **Clarity to a Cold Viewer (Weight: 20%)**: Does it require understanding the family tree, or is the conflict universal?

### Score Normalization
The engine assigns an individual score from **0 to 100** and extracts the exact timestamp and screenplay line.

---

## 3. Cliffhanger Discovery Methodology

A cliffhanger is defined as **the point of maximum unresolved emotional or physical jeopardy**.

### Crucial Distinction: Resolution vs Anticipation
- **Resolved Scene (Rejected as Cliffhanger):** A couple argues, one apologizes, and they hug. High dramatic intensity, but zero anticipation to watch further.
- **Unresolved Scene (Valid Cliffhanger):** The groom declares the bride is worthless, turns his back, and the bride's tearful eyes harden into cold defiance as the music swells and the screen cuts to black.

### Criteria
- **Unanswered question or decision.**
- **Interrupted threat or physical escalation.**
- **Sudden revelation without immediate reaction.**
- **Defiant posture facing overwhelming odds.**

---

## 4. Standalone Context Methodology

A promo clip published as an ad on social media will be viewed by audiences who have never heard of the show.

The context engine classifies each candidate into one of four tiers:

| Context Tier | Definition | Action Taken |
|---|---|---|
| **Excellent** | 100% self-contained. The conflict (e.g. jilted bride, cruel sister, cold fiancé) is universally understood without backstory. | Passed to ranking |
| **Good** | Minor background details present, but the core stakes and emotional dynamic are crystal clear. | Passed with slight penalty |
| **Weak** | Requires partial knowledge of earlier episodes to understand why characters are upset. | Flagged for Human Review |
| **Poor** | Incomprehensible without series lore; heavily dependent on past plotlines. | **Hard Rejection** |

---

## 5. Candidate Construction: Continuous vs. Multi-Segment

### 5.1 Continuous Promos (Single Cut)
- An unbroken segment extracted from a single episode.
- Start timestamp matches an identified hook ($T_{start}$).
- End timestamp matches an identified cliffhanger ($T_{end}$).
- Constraint: $20.0s \le (T_{end} - T_{start}) \le 60.0s$.
- **Advantage:** Maximum narrative flow; zero artificial transition editing required.

### 5.2 Multi-Segment Promos (Montage / Cross-Cut)
- Combines $K$ discrete segments ($K \in \{2, 3\}$).
- **Segment 1:** High-impact opening hook (12–18 seconds).
- **Segment 2+:** Escalating confrontation, revelation, or reaction cut.
- **Final Segment:** Climactic unresolved cliffhanger (12–18 seconds).
- Total duration calculated strictly as the sum of selected cuts:
  $$D_{total} = \sum_{i=1}^{K} (End_i - Start_i)$$
- Unused time between separated segments is excluded from duration.
- Constraint: $20.0s \le D_{total} \le 60.0s$.

---

## 6. Scoring Formula & Weights

Every candidate receives an arithmetically deterministic score calculated in Python (not hallucinated by the LLM):

$$\text{Final Score} = 0.20 \cdot S_{hook} + 0.20 \cdot S_{cliff} + 0.20 \cdot S_{context} + 0.15 \cdot S_{coherence} + 0.10 \cdot S_{emotional} + 0.10 \cdot S_{curiosity} + 0.05 \cdot S_{duration}$$

### Duration Suitability ($S_{duration}$)
- **30.0s to 45.0s:** $100.0$ pts (Optimal short-form video performance window).
- **25.0s to 30.0s:** $85.0$ to $100.0$ pts.
- **45.0s to 52.0s:** $90.0$ to $100.0$ pts.
- **20.0s to 25.0s & 52.0s to 60.0s:** $75.0$ to $90.0$ pts.
- **$< 20.0s$ or $> 60.0s$:** $0.0$ pts (Triggers immediate hard rejection gate).

---

## 7. Deduplication & Creative Diversity

To prevent flooding human editors with 20 nearly identical variations of the same scene, the deduplication engine computes the temporal overlap ratio:

$$\text{Overlap Ratio} = \frac{\text{Intersecting Seconds}}{\min(\text{Duration}_A, \text{Duration}_B)}$$

If two candidates share identical hooks/cliffhangers or have $> 70\%$ temporal overlap, the engine automatically keeps the higher-scoring variant and routes the duplicate to the deduplication log.

"""
Centralized prompt engineering templates for Kuku Promo Intelligence.
Every prompt strictly enforces screenplay ground truth, exact timestamp preservation,
and structured JSON outputs.
"""

SYSTEM_PROMPT = """You are a senior microdrama narrative analyst and promotional discovery specialist for mobile-first video platforms (TikTok, Reels, Shorts).
Your task is to analyze screenplays and identify high-converting promotional clip opportunities (20-60s).

CORE DIRECTIVES:
1. Ground Truth Only: Use strictly screenplay-supported information. NEVER invent dialogue, timestamps, character names, or scenes.
2. Exact Timestamps: Always cite exact timestamps from the screenplay text.
3. Distinguish Fact from Inference: Explicitly label creative observations vs screenplay facts.
4. Format: Output valid JSON adhering strictly to the requested schema. Do not enclose JSON in markdown code blocks if asked for raw json, or use standard ```json ... ``` blocks.
"""

EPISODE_ANALYSIS_PROMPT = """Analyze this microdrama screenplay episode.

EPISODE ID: {episode_id}
SCREENPLAY TEXT:
\"\"\"
{screenplay_text}
\"\"\"

TASKS:
1. Identify main narrative conflict and character arcs in this episode.
2. Extract all active characters with their roles and relationships.
3. Identify dramatic turning points (betrayals, confrontations, revelations, suspense).
4. Summarize the episode's emotional arc.

Respond with valid JSON:
{{
  "episode_id": "{episode_id}",
  "main_conflict": "...",
  "characters": [
    {{"name": "...", "role": "protagonist|antagonist|supporting", "description": "...", "relationships": {{"other_char": "relationship"}}}}
  ],
  "key_events": [
    {{"event_id": "EV01", "timestamp_str": "MM:SS.SS", "description": "...", "event_type": "betrayal|conflict|revelation|climax", "intensity_score": 85}}
  ],
  "revelations_and_betrayals": ["..."],
  "emotional_arc": "...",
  "potential_promotional_themes": ["..."]
}}
"""

CHARACTER_EXTRACTION_PROMPT = """Extract the exact character profiles and relationships from this screenplay excerpt.

EPISODE ID: {episode_id}
SCREENPLAY:
\"\"\"
{screenplay_text}
\"\"\"

STRICT RULES:
- Only list characters who speak or take direct physical action.
- Extract their apparent motives, status, and dynamics with other characters.
- Never invent details not present in the dialogue or action lines.

Respond in JSON:
{{
  "characters": [
    {{
      "name": "...",
      "role": "protagonist|antagonist|supporting",
      "description": "...",
      "relationships": {{"Character B": "fiancé who betrays her", "Character C": "jealous sister"}}
    }}
  ]
}}
"""

CHARACTER_RELATIONSHIP_PROMPT = """Analyze the relational power dynamics and emotional fault lines between the characters in this episode.

EPISODE ID: {episode_id}
CHARACTERS: {characters}
SCREENPLAY:
\"\"\"
{screenplay_text}
\"\"\"

Assess:
1. Status differentials and power struggles.
2. Active betrayals or unspoken alliances.
3. How quickly a new viewer can grasp these relationships within 5 seconds.

Respond in JSON:
{{
  "episode_id": "{episode_id}",
  "relational_summary": "...",
  "clarity_to_new_viewer": "high|medium|low",
  "key_dynamic_pairs": [
    {{"char_a": "...", "char_b": "...", "dynamic": "...", "instant_recognizability": 90}}
  ]
}}
"""

EVENT_DETECTION_PROMPT = """Identify high-stakes dramatic events in this screenplay.

EPISODE ID: {episode_id}
SCREENPLAY:
\"\"\"
{screenplay_text}
\"\"\"

Criteria:
- Slaps, physical aggression, or sudden physical halts.
- Major verbal accusations, humiliating public announcements, broken oaths.
- Shocking arrivals or unexpected reveals.

For each event, record the exact timestamp from the script, description, and intensity score (0-100).

Respond in JSON:
{{
  "events": [
    {{
      "event_id": "EV...",
      "timestamp_str": "MM:SS.SS",
      "description": "...",
      "event_type": "confrontation|betrayal|shock|humiliation",
      "intensity_score": 90,
      "characters_involved": ["..."]
    }}
  ]
}}
"""

HOOK_DISCOVERY_PROMPT = """Identify potential promotional HOOKS in this episode.
A hook must grab attention in the first 3 seconds of a scroll on mobile feeds.

EPISODE ID: {episode_id}
SCREENPLAY:
\"\"\"
{screenplay_text}
\"\"\"

HOOK CRITERIA:
- Must have immediate, visceral punch (shocking revelation, brutal betrayal, slap, sudden weapon/guard, public shaming).
- Does NOT require prior knowledge to feel intense.
- Must cite EXACT timestamps from the script.

Respond in JSON:
{{
  "hooks": [
    {{
      "timestamp": "MM:SS.SS",
      "character_or_element": "...",
      "quote_or_action": "...",
      "hook_type": "shocking_statement|betrayal|confrontation|revelation",
      "scroll_stop_reason": "Explain why this stops someone scrolling within 3 seconds",
      "score": 92.0,
      "confidence": 0.95
    }}
  ]
}}
"""

CLIFFHANGER_DISCOVERY_PROMPT = """Identify potential promotional CLIFFHANGERS in this episode.
A cliffhanger must leave an urgent question or unresolved tension that compels the viewer to watch the full show.

EPISODE ID: {episode_id}
SCREENPLAY:
\"\"\"
{screenplay_text}
\"\"\"

CLIFFHANGER CRITERIA:
- Unanswered high-stakes question, interrupted violent act, sudden arrival, or dilemma.
- Must NOT be an already resolved scene or happy conclusion.
- Must cite exact timestamp from script.

Respond in JSON:
{{
  "cliffhangers": [
    {{
      "timestamp": "MM:SS.SS",
      "event_description": "...",
      "unresolved_question": "...",
      "viewer_anticipation_reason": "Why the viewer feels an irresistible itch to know what happens next",
      "score": 88.0,
      "confidence": 0.95
    }}
  ]
}}
"""

CONTEXT_EVALUATION_PROMPT = """Evaluate this candidate promotional clip from the perspective of a brand new viewer who has NEVER watched the show.

CANDIDATE PROMO DETAILS:
Title: {title}
Type: {segment_type}
Segments: {segments_json}
Dialogue Excerpts:
{dialogue_summary}

EVALUATION QUESTIONS:
1. Is it clear who the hero and antagonist are?
2. Is the core conflict instantly understood?
3. Does it feel like a complete teaser, or an incomprehensible slice of lore?
4. Would a viewer be confused about why these people are arguing?

Assign one rating: "Excellent" (100% self-explanatory), "Good" (minor unneeded details but crystal clear conflict), "Weak" (needs context), or "Poor" (baffling without previous episodes).

Respond in JSON:
{{
  "context_rating": "Excellent|Good|Weak|Poor",
  "character_clarity": "...",
  "conflict_clarity": "...",
  "prior_knowledge_needed": false,
  "explanation": "...",
  "context_score": 85.0
}}
"""

PROMO_CANDIDATE_GENERATION_PROMPT = """Generate complete promotional candidate sequences (duration strictly 20-60 seconds) from this episode or combined episodes.

EPISODE CONTEXT:
Episode ID: {episode_id}
Summary: {summary}
Available Timed Segments:
{timed_segments_list}

REQUIREMENTS:
1. The promo must start with a high-impact HOOK (first 3 seconds).
2. The promo must end on an unresolved CLIFFHANGER.
3. Total duration must be between 20 and 60 seconds (Sum of segment durations).
4. Each segment must cite real timestamps from the provided segments.
5. Provide continuous clips (single cut) and multi-segment sequences (montage/connected cuts).

Respond in JSON:
{{
  "candidates": [
    {{
      "title": "Punchy Ad Title",
      "segment_type": "continuous|multi_segment",
      "segments": [
        {{
          "segment_order": 1,
          "episode_id": "{episode_id}",
          "start_timestamp": "MM:SS.SS",
          "end_timestamp": "MM:SS.SS",
          "selected_moment": "...",
          "reason_for_inclusion": "Opening hook"
        }}
      ],
      "hook_timestamp": "MM:SS.SS",
      "hook_description": "...",
      "hook_score": 90.0,
      "cliffhanger_timestamp": "MM:SS.SS",
      "cliffhanger_description": "...",
      "cliffhanger_score": 85.0,
      "narrative_coherence_explanation": "...",
      "standalone_context_rating": "Excellent|Good|Weak|Poor",
      "coherence_score": 85.0,
      "emotional_intensity_score": 90.0,
      "curiosity_score": 88.0
    }}
  ]
}}
"""

PROMO_COHERENCE_PROMPT = """Evaluate the narrative flow and emotional escalation of this promo sequence.

PROMO TITLE: {title}
SEGMENTS:
{segments_json}

Check:
1. Does the emotional intensity build or stall?
2. Are the cuts jarring or narratively logical?
3. Does the sequence deliver a cohesive mini-story in under 60 seconds?

Respond in JSON:
{{
  "coherence_rating": "high|medium|low",
  "flow_critique": "...",
  "escalation_score": 85.0,
  "coherence_score": 88.0
}}
"""

FINAL_CANDIDATE_ASSESSMENT_PROMPT = """Conduct a final editorial review of this promotional candidate.

PROMO DETAILS:
Title: {title}
Duration: {duration_seconds}s
Hook: {hook_info}
Cliffhanger: {cliffhanger_info}
Standalone Context: {context_info}

Estimate overall viral conversion potential on mobile platforms (TikTok/Shorts/Reels).
Highlight potential marketing angles, target audience demographics, and any red flags.

Respond in JSON:
{{
  "marketing_angle": "...",
  "target_audience": "...",
  "viral_conversion_potential": "High|Medium|Low",
  "editorial_recommendation": "Recommend strongly|Recommend with edits|Reject",
  "final_editorial_notes": "..."
}}
"""

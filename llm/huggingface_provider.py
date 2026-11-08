"""
Hugging Face Inference Providers implementation using the official huggingface_hub SDK.
"""
import time
import logging
from typing import Dict, Any, List, Optional, Type, TypeVar, Tuple
from pydantic import BaseModel
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

from config.settings import settings
import config.prompts as prompts
from llm.base_provider import BaseLLMProvider
from llm.response_parser import parse_and_validate, parse_llm_json
from llm.token_utils import truncate_context
from models.episode import Episode, CharacterProfile, StoryEvent
from models.promo import HookCandidate, CliffhangerCandidate, PromoCandidate
from models.schemas import (
    LLMEpisodeAnalysis,
    LLMContextEvaluation,
    LLMPromoCandidateRaw,
)

logger = logging.getLogger("kuku.llm.huggingface")
T = TypeVar("T", bound=BaseModel)


class HuggingFaceProvider(BaseLLMProvider):
    """Production LLM provider using Hugging Face Inference Providers."""

    def __init__(
        self,
        token: Optional[str] = None,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        timeout: float = 45.0,
    ):
        self._token = token or settings.get_token()
        self._model_id = model_id or settings.HF_MODEL_ID
        self._provider = provider or settings.HF_PROVIDER
        self._timeout = timeout

        # Initialize InferenceClient
        client_kwargs = {"timeout": self._timeout}
        if self._token:
            client_kwargs["token"] = self._token
        if self._provider and self._provider != "auto":
            client_kwargs["provider"] = self._provider

        self.client = InferenceClient(**client_kwargs)

    @property
    def provider_name(self) -> str:
        return "huggingface"

    @property
    def model_id(self) -> str:
        return self._model_id

    def health_check(self) -> Tuple[bool, str]:
        """Validates API token and tests inference on the selected model."""
        if not self._token:
            return False, "Hugging Face token is missing. Please set HF_TOKEN in .env or Streamlit Secrets."

        try:
            # Small test prompt to check provider status
            res = self.client.chat.completions.create(
                model=self._model_id,
                messages=[{"role": "user", "content": "Respond strictly with the single word: READY"}],
                max_tokens=10,
                temperature=0.1,
            )
            content = res.choices[0].message.content.strip()
            return True, f"Successfully connected to Hugging Face ({self._model_id}). Response: '{content}'"
        except HfHubHTTPError as e:
            if e.response.status_code == 401:
                return False, "Authentication failed (HTTP 401): Invalid or expired Hugging Face token."
            elif e.response.status_code == 429:
                return False, "Rate limit reached (HTTP 429): Quota exhausted or request rate exceeded on Hugging Face."
            elif e.response.status_code == 404:
                return False, f"Model not found or not available for serverless inference: {self._model_id}"
            else:
                return False, f"Hugging Face HTTP error ({e.response.status_code}): {e.server_message or str(e)}"
        except Exception as e:
            err_msg = str(e)
            if "ProxyError" in err_msg or "WinError 10013" in err_msg or "Cannot connect" in err_msg:
                return False, f"Network connection blocked or unreachable: {err_msg}"
            return False, f"Inference health check failed: {err_msg}"

    def _execute_with_retry(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        """Executes chat completion with bounded retries and exponential backoff."""
        retries = 0
        backoff = settings.RETRY_BACKOFF_BASE

        while retries <= settings.MAX_RETRIES:
            try:
                response = self.client.chat.completions.create(
                    model=self._model_id,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return response.choices[0].message.content.strip()
            except HfHubHTTPError as e:
                # Retry transient 429 or 503 errors
                if e.response.status_code in (429, 503, 504) and retries < settings.MAX_RETRIES:
                    retries += 1
                    sleep_time = backoff ** retries
                    logger.warning(f"Transient HTTP {e.response.status_code}. Retrying in {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                else:
                    raise
            except Exception as e:
                if retries < settings.MAX_RETRIES and ("timeout" in str(e).lower() or "connection" in str(e).lower()):
                    retries += 1
                    sleep_time = backoff ** retries
                    logger.warning(f"Connection error: {e}. Retrying in {sleep_time:.1f}s...")
                    time.sleep(sleep_time)
                else:
                    raise

        raise RuntimeError(f"Exceeded max retries ({settings.MAX_RETRIES}) connecting to Hugging Face.")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.3,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": prompts.SYSTEM_PROMPT})
        messages.append({"role": "user", "content": prompt})

        return self._execute_with_retry(messages, max_tokens, temperature)

    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1500,
        temperature: float = 0.2,
    ) -> T:
        raw_text = self.generate_text(prompt, system_prompt, max_tokens, temperature)
        try:
            return parse_and_validate(raw_text, response_schema)
        except Exception as e:
            logger.warning(f"Initial schema parse failed: {e}. Attempting self-correction retry...")
            # 1-shot repair prompt
            repair_prompt = (
                f"The previous output failed JSON/schema validation.\n"
                f"Validation error: {e}\n"
                f"Raw response:\n{raw_text}\n\n"
                f"Please fix and output ONLY strictly valid JSON matching the schema."
            )
            repaired_text = self.generate_text(repair_prompt, system_prompt, max_tokens, temperature=0.1)
            return parse_and_validate(repaired_text, response_schema)

    def analyze_episode(self, episode: Episode) -> LLMEpisodeAnalysis:
        # Create concise screenplay excerpt for token budget
        script_text = self._build_episode_script_text(episode)
        prompt = prompts.EPISODE_ANALYSIS_PROMPT.format(
            episode_id=episode.episode_id,
            screenplay_text=truncate_context(script_text, max_tokens=2500),
        )
        return self.generate_structured(prompt, LLMEpisodeAnalysis)

    def extract_characters(self, episode: Episode) -> List[CharacterProfile]:
        script_text = self._build_episode_script_text(episode)
        prompt = prompts.CHARACTER_EXTRACTION_PROMPT.format(
            episode_id=episode.episode_id,
            screenplay_text=truncate_context(script_text, max_tokens=2500),
        )
        parsed = parse_llm_json(self.generate_text(prompt))
        chars = parsed.get("characters", [])
        return [CharacterProfile.model_validate(c) for c in chars]

    def detect_hooks(self, episode: Episode) -> List[HookCandidate]:
        script_text = self._build_episode_script_text(episode)
        prompt = prompts.HOOK_DISCOVERY_PROMPT.format(
            episode_id=episode.episode_id,
            screenplay_text=truncate_context(script_text, max_tokens=2500),
        )
        parsed = parse_llm_json(self.generate_text(prompt))
        hook_items = parsed.get("hooks", [])
        candidates = []
        for i, item in enumerate(hook_items):
            # Parse timestamp to seconds
            from core.timestamp_utils import parse_timestamp
            t_str = str(item.get("timestamp", "00:00.00"))
            sec = parse_timestamp(t_str)
            candidates.append(
                HookCandidate(
                    hook_id=f"HOOK-{episode.episode_id}-{i+1:02d}",
                    episode_id=episode.episode_id,
                    source_timestamp=t_str,
                    start_seconds=sec,
                    end_seconds=sec + 4.0,
                    relevant_content=item.get("quote_or_action", ""),
                    hook_type=item.get("hook_type", "dramatic_statement"),
                    explanation=item.get("scroll_stop_reason", ""),
                    hook_score=float(item.get("score", 80.0)),
                    confidence=float(item.get("confidence", 0.9)),
                    screenplay_reference=f"[{t_str}] {item.get('character_or_element', '')}: {item.get('quote_or_action', '')}",
                )
            )
        return candidates

    def detect_cliffhangers(self, episode: Episode) -> List[CliffhangerCandidate]:
        script_text = self._build_episode_script_text(episode)
        prompt = prompts.CLIFFHANGER_DISCOVERY_PROMPT.format(
            episode_id=episode.episode_id,
            screenplay_text=truncate_context(script_text, max_tokens=2500),
        )
        parsed = parse_llm_json(self.generate_text(prompt))
        cliff_items = parsed.get("cliffhangers", [])
        candidates = []
        for i, item in enumerate(cliff_items):
            from core.timestamp_utils import parse_timestamp
            t_str = str(item.get("timestamp", "00:00.00"))
            sec = parse_timestamp(t_str)
            candidates.append(
                CliffhangerCandidate(
                    cliffhanger_id=f"CLIFF-{episode.episode_id}-{i+1:02d}",
                    episode_id=episode.episode_id,
                    source_timestamp=t_str,
                    start_seconds=sec,
                    end_seconds=sec + 5.0,
                    event_description=item.get("event_description", ""),
                    unresolved_element=item.get("unresolved_question", ""),
                    why_viewer_continues=item.get("viewer_anticipation_reason", ""),
                    cliffhanger_score=float(item.get("score", 80.0)),
                    confidence=float(item.get("confidence", 0.9)),
                    screenplay_reference=f"[{t_str}] {item.get('event_description', '')}",
                )
            )
        return candidates

    def evaluate_context(
        self, promo_title: str, segment_type: str, segments_summary: str, dialogue_summary: str
    ) -> LLMContextEvaluation:
        prompt = prompts.CONTEXT_EVALUATION_PROMPT.format(
            title=promo_title,
            segment_type=segment_type,
            segments_json=segments_summary,
            dialogue_summary=dialogue_summary,
        )
        return self.generate_structured(prompt, LLMContextEvaluation)

    def generate_candidates(
        self, episode: Episode, show_context: Optional[str] = None
    ) -> List[LLMPromoCandidateRaw]:
        timed_segs = self._build_timed_segments_list(episode)
        prompt = prompts.PROMO_CANDIDATE_GENERATION_PROMPT.format(
            episode_id=episode.episode_id,
            summary=episode.logline or "Episode drama",
            timed_segments_list=timed_segs[:2000],
        )
        parsed = parse_llm_json(self.generate_text(prompt, max_tokens=2000))
        cands = parsed.get("candidates", [])
        return [LLMPromoCandidateRaw.model_validate(c) for c in cands]

    def evaluate_promo(self, candidate: PromoCandidate) -> Dict[str, Any]:
        prompt = prompts.FINAL_CANDIDATE_ASSESSMENT_PROMPT.format(
            title=candidate.title,
            duration_seconds=candidate.total_duration_seconds,
            hook_info=f"[{candidate.hook.source_timestamp}] {candidate.hook.relevant_content}",
            cliffhanger_info=f"[{candidate.cliffhanger.source_timestamp}] {candidate.cliffhanger.unresolved_element}",
            context_info=f"{candidate.context_rating}: {candidate.standalone_context}",
        )
        return parse_llm_json(self.generate_text(prompt))

    def _build_episode_script_text(self, episode: Episode) -> str:
        lines = [f"EPISODE: {episode.episode_id} ({episode.filename})"]
        if episode.logline:
            lines.append(f"LOGLINE: {episode.logline}")
        for sc in episode.scenes:
            lines.append(f"\nSCENE {sc.scene_number}: {sc.heading} ({sc.original_timestamp})")
            for el in sc.elements:
                speaker = f" {el.speaker}" if el.speaker else ""
                lines.append(f"[{el.start_str} - {el.end_str}] {el.element_type}{speaker}: {el.text}")
        return "\n".join(lines)

    def _build_timed_segments_list(self, episode: Episode) -> str:
        items = []
        for sc in episode.scenes:
            for el in sc.elements:
                if el.element_type in ("DIALOGUE", "ACTION"):
                    prefix = f"{el.speaker}: " if el.speaker else ""
                    items.append(f"({el.start_str}-{el.end_str}) {prefix}{el.text[:80]}")
        return "\n".join(items[:60])

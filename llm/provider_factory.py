"""
LLM Provider Factory.
"""
import logging
from typing import Optional
from llm.base_provider import BaseLLMProvider
from llm.huggingface_provider import HuggingFaceProvider
from llm.mock_provider import MockProvider
from config.settings import settings

logger = logging.getLogger("kuku.llm.factory")


def get_llm_provider(
    mode: str = "auto",
    token: Optional[str] = None,
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
) -> BaseLLMProvider:
    """
    Factory function to instantiate the configured LLM provider.

    Parameters:
    - mode: 'auto', 'huggingface', or 'mock'.
    - token: Hugging Face API token (overrides settings).
    - model_id: Target Hugging Face model repository ID.
    - provider: Specific Hugging Face inference provider ('auto', 'together', etc.).
    """
    token_val = token or settings.get_token()
    model_id_val = model_id or settings.HF_MODEL_ID
    provider_val = provider or settings.HF_PROVIDER

    if mode == "mock":
        return MockProvider(model_id="mock-heuristic-v1")

    if mode == "huggingface":
        return HuggingFaceProvider(
            token=token_val,
            model_id=model_id_val,
            provider=provider_val,
        )

    # mode == 'auto':
    if token_val and len(token_val.strip()) > 10:
        return HuggingFaceProvider(
            token=token_val,
            model_id=model_id_val,
            provider=provider_val,
        )
    else:
        logger.info("No Hugging Face token configured; using Mock / Heuristic provider.")
        return MockProvider(model_id="mock-heuristic-v1")

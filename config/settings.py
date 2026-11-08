"""
Configuration settings for Kuku Promo Intelligence.
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve secret from Streamlit Secrets or Environment Variables."""
    # First check streamlit secrets if available
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    
    # Fallback to os.environ
    return os.environ.get(key, default)


class Settings:
    """Central configuration for application runtime and AI inference."""

    # Hugging Face Settings
    HF_TOKEN: Optional[str] = get_secret("HF_TOKEN")
    HF_MODEL_ID: str = get_secret("HF_MODEL_ID", "meta-llama/Llama-3.2-3B-Instruct")
    HF_PROVIDER: str = get_secret("HF_PROVIDER", "auto")

    # Retry and timeout parameters
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_BASE: float = 1.5
    TIMEOUT_SECONDS: float = 45.0

    # Promo constraints
    MIN_PROMO_DURATION: float = 20.0
    MAX_PROMO_DURATION: float = 60.0

    # Scoring Weights (Total = 100)
    SCORING_WEIGHTS: Dict[str, float] = {
        "hook": 20.0,
        "cliffhanger": 20.0,
        "context": 20.0,
        "coherence": 15.0,
        "emotional": 10.0,
        "curiosity": 10.0,
        "duration": 5.0,
    }

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    OUTPUTS_DIR: Path = BASE_DIR / "outputs"
    DOCS_DIR: Path = BASE_DIR / "docs"

    @classmethod
    def get_token(cls) -> Optional[str]:
        """Returns the current HF token from memory or environment."""
        token = cls.HF_TOKEN or os.getenv("HF_TOKEN")
        if not token:
            # Check default huggingface home token
            home_token = Path.home() / ".cache" / "huggingface" / "token"
            if home_token.exists():
                try:
                    token = home_token.read_text().strip()
                except Exception:
                    pass
        return token

    @classmethod
    def is_token_configured(cls) -> bool:
        """Check if an API token is present."""
        t = cls.get_token()
        return bool(t and len(t) > 10)


settings = Settings()

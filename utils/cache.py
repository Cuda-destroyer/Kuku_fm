"""
Disk caching for intermediate episode analyses and prompt results.
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import settings


class PipelineCache:
    """Manages file-based JSON cache for screenplay analyses."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or (settings.BASE_DIR / ".cache" / "pipeline")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached item if present."""
        path = self.cache_dir / f"{self._hash_key(key)}.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Saves item to cache."""
        path = self.cache_dir / f"{self._hash_key(key)}.json"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(value, f, indent=2)
        except Exception:
            pass

    def clear(self) -> int:
        """Clears all cached files."""
        count = 0
        for f in self.cache_dir.glob("*.json"):
            try:
                f.unlink()
                count += 1
            except Exception:
                pass
        return count

"""Disk-backed JSON cache with TTL support."""

import json
import re
import time
from pathlib import Path
from functools import wraps
from typing import Any, Optional

_SAFE_KEY = re.compile(r'^[a-zA-Z0-9_-]+$')


def _sanitize_key(key: str) -> str:
    """Sanitize cache key to prevent path traversal."""
    if not _SAFE_KEY.match(key):
        raise ValueError(f"Invalid cache key: {key!r}")
    return key


class Cache:
    """Simple file-based cache storing JSON values with timestamps."""

    def __init__(self) -> None:
        self.dir = Path.home() / ".cache" / "ezfetch"
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    def _path(self, key: str) -> Path:
        return self.dir / f"{_sanitize_key(key)}.json"

    def get(self, key: str, ttl: int = 300) -> Optional[Any]:
        """Return cached value if it exists and hasn't expired, else None."""
        try:
            d = json.loads(self._path(key).read_text(encoding="utf-8"))
            return d["v"] if time.time() - d["t"] < ttl else None
        except Exception:
            return None

    def set(self, key: str, val: Any) -> None:
        """Write a value to the cache."""
        try:
            self._path(key).write_text(
                json.dumps({"t": time.time(), "v": val}), encoding="utf-8"
            )
        except Exception:
            pass

    def clear(self, key: Optional[str] = None) -> None:
        """Remove one or all cached entries."""
        try:
            targets = [self._path(key)] if key else list(self.dir.glob("*.json"))
        except ValueError:
            return
        for f in targets:
            try:
                f.unlink()
            except Exception:
                pass

_cache = None

def get_cache():
    global _cache
    if not _cache:
        _cache = Cache()
    return _cache

def cached(key: str, ttl: int = 300):
    """Decorator that caches a function's return value to disk.

    Skips caching if the result is falsy or 'Unknown'.
    Respects the 'performance.cache_enabled' config setting.
    """
    def dec(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                from .config import get_config
                if not get_config().get("performance", "cache_enabled", default=True):
                    return fn(*args, **kwargs)
            except Exception:
                pass
            c = get_cache()
            v = c.get(key, ttl)
            if v is not None:
                return v
            result = fn(*args, **kwargs)
            if result and result != "Unknown":
                c.set(key, result)
            return result
        return wrapper
    return dec

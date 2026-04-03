"""Configuration management with JSON file support and defaults."""

import copy
import json
from pathlib import Path
from typing import Any, Optional

DEFAULTS = {
    "display": {"show_logo": True, "show_colors": True, "truncate_length": 50, "show_color_blocks": True},
    "theme": {"name": "default"},
    "fields": {
        "enabled": ["User","Host","OS","Kernel","Uptime","Packages","Shell","Resolution",
                     "DE","WM","Terminal","CPU","GPU","Memory","Swap","Disk","Local IP","Battery","Locale"],
        "hide_unavailable": True, "hide_unknown": False,
    },
    "performance": {"cache_enabled": True, "cache_duration": 300},
}

def _merge(base: dict, over: dict) -> None:
    """Recursively merge *over* into *base*, mutating base in-place."""
    for k, v in over.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _merge(base[k], v)
        else:
            base[k] = v


class Config:
    """Application configuration backed by a JSON file."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.file = Path(path) if path else Path.home() / ".config" / "ezfetch" / "config.json"
        file_existed = self.file.exists()
        self.data: dict = self._load()
        if not file_existed:
            self.save()

    def _load(self) -> dict:
        cfg = copy.deepcopy(DEFAULTS)
        if self.file.exists():
            try:
                _merge(cfg, json.loads(self.file.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                pass
        return cfg

    def get(self, *keys: str, default: Any = None) -> Any:
        """Traverse nested config keys, returning *default* if any key is missing."""
        v = self.data
        for k in keys:
            if isinstance(v, dict) and k in v:
                v = v[k]
            else:
                return default
        return v

    def save(self) -> None:
        """Persist current configuration to disk."""
        try:
            self.file.parent.mkdir(parents=True, exist_ok=True)
            self.file.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        except OSError:
            pass

_cfg = None

def get_config(path: Optional[str] = None) -> Config:
    """Return the singleton Config, optionally (re)loading from *path*."""
    global _cfg
    if not _cfg or path:
        _cfg = Config(path)
    return _cfg

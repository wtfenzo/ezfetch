import re
import unicodedata


def _to_int(value: object, default: int) -> int:
    """Safely coerce values to int with a fallback default."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_text(value: object, default: str = "") -> str:
    """Safely coerce values to str with a fallback default."""
    if value is None:
        return default
    if isinstance(value, str):
        return value
    try:
        return str(value)
    except Exception:
        return default


def truncate(text: str, max_len: int = 50, suffix: str = "...") -> str:
    """Truncate text to max_len characters, appending suffix if truncated."""
    text = _to_text(text, "")
    max_len = _to_int(max_len, 50)
    suffix = _to_text(suffix, "")
    if not text:
        return ""
    if max_len <= 0:
        return ""
    if len(text) <= max_len:
        return text
    if max_len <= len(suffix):
        return text[:max_len]
    return text[:max_len - len(suffix)] + suffix


def display_width(text: str) -> int:
    """Calculate display width, accounting for ANSI escapes and wide Unicode."""
    text = _to_text(text, "")
    if not text:
        return 0
    text = re.sub(r'\033\[[0-9;]*m', '', text)
    width = 0
    for ch in text:
        eaw = unicodedata.east_asian_width(ch)
        if eaw in ('F', 'W'):
            width += 2
        elif unicodedata.category(ch) in ('Mn', 'Me', 'Cf'):
            pass
        else:
            width += 1
    return width


def pad_to_width(text: str, target_width: int) -> str:
    """Pad text with spaces to reach the target display width."""
    text = _to_text(text, "")
    target_width = max(0, _to_int(target_width, display_width(text)))
    current = display_width(text)
    if current >= target_width:
        return text
    return text + " " * (target_width - current)

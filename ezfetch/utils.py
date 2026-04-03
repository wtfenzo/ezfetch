
import re
import unicodedata
from typing import Optional


def truncate(text: str, max_len: int = 50, suffix: str = "...") -> str:
    """Truncate text to max_len characters, appending suffix if truncated."""
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
    """Calculate the display width of a string, accounting for wide Unicode and ANSI codes."""
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
    """Pad text with spaces to reach target display width."""
    current = display_width(text)
    if current >= target_width:
        return text
    return text + " " * (target_width - current)

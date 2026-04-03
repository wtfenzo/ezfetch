"""ANSI color utilities and theme definitions."""

import re
from typing import Optional, Dict, List

_C = lambda n: f"\033[{n}m"
RST = _C(0)

_COLORS: Dict[str, int] = {
    "black": 30, "red": 31, "green": 32, "yellow": 33,
    "blue": 34, "magenta": 35, "cyan": 36, "white": 37,
    "bright_black": 90, "bright_red": 91, "bright_green": 92, "bright_yellow": 93,
    "bright_blue": 94, "bright_magenta": 95, "bright_cyan": 96, "bright_white": 97,
}


def rgb(r: int, g: int, b: int, bg: bool = False) -> str:
    """Return an ANSI 24-bit (truecolor) escape sequence."""
    return f"\033[{48 if bg else 38};2;{r};{g};{b}m"


def from_hex(h: str, bg: bool = False) -> str:
    """Convert a hex color string (e.g. '#FF5500' or '#F50') to an ANSI escape sequence."""
    h = h.lstrip('#')
    # Expand 3-char shorthand (#F50 → #FF5500)
    if len(h) == 3 and all(c in '0123456789abcdefABCDEF' for c in h):
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    if len(h) != 6 or not all(c in '0123456789abcdefABCDEF' for c in h):
        return ""
    return rgb(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), bg=bg)

def color(name: str) -> str:
    """Return the ANSI escape sequence for a named color."""
    code = _COLORS.get(name.lower().replace(" ", "_"))
    return _C(code) if code else ""


def colorize(text: str, c: Optional[str], reset: bool = True) -> str:
    """Wrap text in an ANSI color sequence."""
    if not c:
        return text
    if not c.startswith('\033'):
        c = color(c)
    if not c:
        return text
    return f"{c}{text}{RST}" if reset else f"{c}{text}"

def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from a string."""
    return re.sub(r'\033\[[0-9;]*m', '', text)

THEMES = {
    "default": {"label": _C(92), "value": _C(96), "logo": _C(36), "separator": _C(37)},
    "nord":    {"label": from_hex("#88C0D0"), "value": from_hex("#ECEFF4"), "logo": from_hex("#5E81AC"), "separator": from_hex("#D8DEE9")},
    "dracula": {"label": from_hex("#FF79C6"), "value": from_hex("#F8F8F2"), "logo": from_hex("#BD93F9"), "separator": from_hex("#6272A4")},
    "gruvbox": {"label": from_hex("#B8BB26"), "value": from_hex("#EBDBB2"), "logo": from_hex("#83A598"), "separator": from_hex("#A89984")},
    "monokai": {"label": from_hex("#A6E22E"), "value": from_hex("#F8F8F2"), "logo": from_hex("#66D9EF"), "separator": from_hex("#75715E")},
    "solarized": {"label": from_hex("#859900"), "value": from_hex("#93A1A1"), "logo": from_hex("#268BD2"), "separator": from_hex("#586E75")},
}

class Theme:
    """Color theme for ezfetch display."""

    def __init__(self, name: str = "default") -> None:
        if not isinstance(name, str):
            name = "default"
        else:
            name = name.strip() or "default"
        self.colors = THEMES.get(name, THEMES["default"])

    def get(self, key: str) -> str:
        """Return the ANSI escape sequence for the given theme component."""
        return self.colors.get(key, "")

    @staticmethod
    def list_themes() -> List[str]:
        """Return sorted list of available theme names."""
        return sorted(THEMES.keys())

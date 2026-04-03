"""CLI entry point and display logic for ezfetch."""

import argparse
import json
import signal
import sys
from typing import Any, Dict, List, Optional

from . import __version__
from .logo import get_logo, list_logos
from .info import (
    get_battery,
    get_color_blocks,
    get_cpu,
    get_desktop_env,
    get_disk,
    get_gpu,
    get_host,
    get_ip,
    get_kernel,
    get_locale,
    get_memory,
    get_os,
    get_packages,
    get_resolution,
    get_shell,
    get_swap,
    get_terminal,
    get_uptime,
    get_user_host,
    get_window_manager,
)
from .colors import Theme, colorize, strip_ansi
from .config import get_config
from .cache import get_cache
from .utils import truncate, display_width, pad_to_width

# Prevent BrokenPipeError when piped to head/etc. on POSIX systems
if hasattr(signal, 'SIGPIPE'):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(
        description="ezfetch - fast, cross-platform system info",
        epilog="Documentation: https://github.com/wtfenzo/ezfetch",
    )
    p.add_argument("-v", "--version", action="version", version=f"ezfetch {__version__}")
    p.add_argument("-l", "--logo", type=str, metavar="NAME", help="use a specific distro logo")
    p.add_argument("--list-logos", action="store_true", help="list available logos and exit")
    p.add_argument("--no-logo", action="store_true", help="hide the ASCII logo")
    p.add_argument("--custom-logo", type=str, metavar="PATH", help="path to a custom ASCII art file")
    p.add_argument("-t", "--theme", type=str, default=None, help="color theme name")
    p.add_argument("--list-themes", action="store_true", help="list available themes and exit")
    p.add_argument("-c", "--config", type=str, metavar="PATH", help="path to config JSON file")
    p.add_argument("--json", action="store_true", help="output system info as JSON")
    p.add_argument("--no-color", action="store_true", help="disable all colors")
    p.add_argument("--no-color-blocks", action="store_true", help="hide terminal color palette")
    p.add_argument("--no-cache", action="store_true", help="bypass disk cache for this run")
    p.add_argument("--clear-cache", action="store_true", help="clear the disk cache and exit")
    p.add_argument("-f", "--field", action="append", metavar="NAME",
                   help="show only specific fields (can be repeated)")
    return p.parse_args()


FIELDS = [
    ("User", get_user_host), ("Host", get_host), ("OS", get_os), ("Kernel", get_kernel),
    ("Uptime", get_uptime), ("Packages", get_packages), ("Shell", get_shell),
    ("Resolution", get_resolution), ("DE", get_desktop_env), ("WM", get_window_manager),
    ("Terminal", get_terminal), ("CPU", get_cpu), ("GPU", get_gpu), ("Memory", get_memory),
    ("Swap", get_swap), ("Disk", get_disk), ("Local IP", get_ip), ("Battery", get_battery),
    ("Locale", get_locale),
]


def _as_bool(value: Any, default: bool) -> bool:
    """Convert common config value forms to bool with a safe default."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"1", "true", "yes", "on"}:
            return True
        if v in {"0", "false", "no", "off"}:
            return False
    return default


def _as_int(value: Any, default: int, minimum: int = 0) -> int:
    """Convert config values to int with fallback and lower bound."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, parsed)


def _normalize_fields(value: Optional[Any]) -> Optional[List[str]]:
    """Normalize field config/CLI input into a clean list of field names."""
    if value is None:
        return None
    from_sequence = isinstance(value, (list, tuple, set))
    if isinstance(value, str):
        items = [value]
    elif from_sequence:
        items = list(value)
    else:
        return None

    cleaned: List[str] = []
    for item in items:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            cleaned.append(text)
    # Preserve explicit empty lists from config/CLI (means "show no fields").
    if from_sequence:
        return cleaned
    return cleaned or None


def _normalize_theme_name(value: Any, default: str = "default") -> str:
    if isinstance(value, str):
        theme = value.strip()
        return theme or default
    return default


def collect(enabled: Optional[List[str]] = None) -> Dict[str, str]:
    """Collect system information for all (or selected) fields."""
    allowed = {e.lower() for e in enabled} if enabled is not None else None
    result = {}
    for k, fn in FIELDS:
        if allowed is not None and k.lower() not in allowed:
            continue
        try:
            result[k] = fn()
        except Exception:
            result[k] = "Unknown"
    return result


def _build_info_lines(filtered: Dict[str, str], colors: bool, th: Optional[Theme], ml: int) -> List[str]:
    """Format system info key-value pairs into display lines."""
    lines = []
    first = True
    for k, v in filtered.items():
        if first and k == "User":
            if colors and th:
                lines.append(colorize(v, th.get('label')))
                lines.append(colorize("-" * display_width(v), th.get('separator')))
            else:
                lines.append(v)
                lines.append("-" * display_width(v))
            first = False
            continue
        first = False
        if colors and th:
            label = colorize(k, th.get('label'))
            ansi_extra = len(label) - len(strip_ansi(label))
            sep = colorize(':', th.get('separator'))
            val = colorize(v, th.get('value'))
            lines.append(f"{label:<{ml + ansi_extra}} {sep} {val}")
        else:
            lines.append(f"{k:<{ml}} : {v}")
    return lines


def display(
    logo_name: Optional[str] = None,
    custom_logo: Optional[str] = None,
    show_logo: bool = True,
    theme: str = "default",
    colors: bool = True,
    fields: Optional[List[str]] = None,
    trunc: int = 50,
    show_color_blocks: bool = True,
) -> None:
    """Render system info with optional ASCII logo and color theme."""
    cfg = get_config()
    th = Theme(_normalize_theme_name(theme)) if colors else None
    enabled = fields if fields is not None else cfg.get("fields", "enabled")
    info = collect(_normalize_fields(enabled))
    hide_na = _as_bool(cfg.get("fields", "hide_unavailable", default=True), True)
    hide_unk = _as_bool(cfg.get("fields", "hide_unknown", default=False), False)
    trunc_len = _as_int(trunc, 50, minimum=0)

    # Filter out unavailable/unknown fields as configured
    filtered = {}
    for k, v in info.items():
        if hide_na and v in ("Unavailable", "N/A"):
            continue
        if hide_unk and v == "Unknown":
            continue
        filtered[k] = truncate(str(v) if v else "Unknown", trunc_len)

    if not filtered:
        print("ezfetch: no info available to display", file=sys.stderr)
        return

    # Build logo lines
    raw_logo = get_logo(logo_name, custom_logo).splitlines() if show_logo else []
    logo_width = max((display_width(l) for l in raw_logo), default=0) + 2 if raw_logo else 0
    padded_logo = [pad_to_width(l, logo_width) for l in raw_logo] if raw_logo else []
    if padded_logo and colors and th:
        lc = th.get('logo')
        logo_lines = [colorize(l, lc, reset=True) for l in padded_logo] if lc else padded_logo
    else:
        logo_lines = padded_logo
    blank_pad = " " * logo_width

    # Build info lines
    ml = max((len(k) for k in filtered), default=0)
    flines = _build_info_lines(filtered, colors, th, ml)

    # Append color blocks
    show_blocks = bool(show_color_blocks) and _as_bool(
        cfg.get("display", "show_color_blocks", default=True), True
    )
    if colors and show_blocks:
        flines.append("")
        flines.extend(get_color_blocks())

    # Render side-by-side
    total = max(len(logo_lines), len(flines))
    output = []
    for i in range(total):
        ll = logo_lines[i] if i < len(logo_lines) else blank_pad
        fl = flines[i] if i < len(flines) else ""
        output.append(f"{ll}{fl}" if show_logo else fl)
    print("\n".join(output))


def main() -> None:
    """CLI entry point."""
    try:
        a = parse_args()
        if a.list_logos:
            print("\n".join(list_logos()))
            return
        if a.list_themes:
            print("\n".join(Theme.list_themes()))
            return
        if a.clear_cache:
            get_cache().clear()
            print("Cache cleared.")
            return

        cfg = get_config(a.config)
        cli_fields = _normalize_fields(a.field)

        # Temporarily disable caching if --no-cache is set
        if a.no_cache:
            perf = cfg.data.get("performance") if isinstance(cfg.data, dict) else None
            if not isinstance(perf, dict):
                perf = {}
                if isinstance(cfg.data, dict):
                    cfg.data["performance"] = perf
            perf["cache_enabled"] = False

        if a.json:
            print(json.dumps(collect(cli_fields), indent=2))
            return

        display(
            logo_name=a.logo,
            custom_logo=a.custom_logo,
            show_logo=not a.no_logo and _as_bool(cfg.get("display", "show_logo", default=True), True),
            theme=_normalize_theme_name(
                a.theme if a.theme is not None else cfg.get("theme", "name", default="default")
            ),
            colors=not a.no_color and _as_bool(cfg.get("display", "show_colors", default=True), True),
            fields=cli_fields,
            trunc=_as_int(cfg.get("display", "truncate_length", default=50), 50, minimum=0),
            show_color_blocks=not a.no_color_blocks,
        )
    except KeyboardInterrupt:
        sys.exit(130)
    except BrokenPipeError:
        # Silently exit when piped to head/etc.
        sys.exit(0)
    except Exception as e:
        print(f"ezfetch: error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

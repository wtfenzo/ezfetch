"""System information gathering functions for all supported platforms."""

import os
import platform
import re
import socket
import subprocess
import time
import glob
import locale
import shutil
import json
from pathlib import Path
from typing import List, Optional

import psutil
from .cache import cached
from .utils import truncate

__all__ = [
    "get_user_host", "get_host", "get_os", "get_kernel", "get_uptime",
    "get_packages", "get_shell", "get_resolution", "get_desktop_env",
    "get_window_manager", "get_terminal", "get_cpu", "get_gpu",
    "get_memory", "get_swap", "get_disk", "get_ip", "get_battery", "get_locale",
    "get_color_blocks",
]

S = platform.system()
_env = os.environ.get
_has = lambda c: shutil.which(c) is not None
_gib = lambda b: round(b / (1 << 30), 2)
_DMI_GARBAGE = {"to be filled by o.e.m.", "default string", "not specified", "system product name", "none", ""}


def _env_text(key: str, default: str = "") -> str:
    val = _env(key, default)
    if val is None:
        return default
    if isinstance(val, str):
        return val.strip()
    return str(val).strip()

def _cmd(c: str, timeout: int = 5) -> Optional[str]:
    """Run a shell command and return stripped stdout, or None on failure."""
    try:
        return subprocess.check_output(
            c, shell=True, text=True, stderr=subprocess.DEVNULL, timeout=timeout
        ).strip()
    except (subprocess.SubprocessError, OSError):
        return None


def _try(fn, fallback="Unknown"):
    """Call *fn*; return its result if truthy, otherwise *fallback*."""
    try:
        r = fn()
        return r if r else fallback
    except Exception:
        return fallback


def _fread(*parts) -> Optional[str]:
    """Read and strip a file, returning None on any error."""
    try:
        return Path(*parts).read_text(encoding="utf-8").strip()
    except Exception:
        return None


def _format_hz(value: object) -> Optional[str]:
    try:
        hz = float(value)
    except (TypeError, ValueError):
        return None
    if hz <= 0:
        return None
    rounded = round(hz, 2)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")


def get_user_host() -> str:
    """Return 'user@hostname' string."""
    user = _env_text("USER") or _env_text("USERNAME", "?")
    return f"{user}@{socket.gethostname()}"

@cached("host", ttl=3600)
def get_host() -> str:
    """Detect the hardware model / product name."""
    def _do():
        if S == "Linux":
            p = _fread("/sys/class/dmi/id/product_name")
            v = _fread("/sys/class/dmi/id/product_version")
            if not p or p.lower() in _DMI_GARBAGE:
                return None
            if v and v.lower() not in _DMI_GARBAGE:
                return f"{p} ({v})"
            return p
        elif S == "Darwin":
            return _cmd("sysctl -n hw.model")
        elif S == "Windows":
            o = _cmd("wmic computersystem get model")
            if o:
                lines = [l.strip() for l in o.split("\n")[1:] if l.strip()]
                if lines:
                    return lines[0]
        return None
    return _try(_do)

@cached("os", ttl=3600)
def get_os():
    """Detect the operating system name and version."""
    if S == "Linux":
        try:
            with open("/etc/os-release", encoding="utf-8") as f:
                for l in f:
                    if l.startswith("PRETTY_NAME="):
                        return l.split("=", 1)[1].strip().strip('"')
        except Exception:
            pass
    elif S == "Darwin":
        ver = platform.mac_ver()[0]
        if ver:
            return f"macOS {ver}"
    elif S == "Windows":
        rel = platform.release()
        edition = platform.win32_edition() if hasattr(platform, 'win32_edition') else ""
        ver = platform.version()
        parts = ["Windows", rel]
        if edition:
            parts.append(edition)
        return f"{' '.join(parts)} ({ver})"
    return f"{S} {platform.release()}"

@cached("kernel", ttl=3600)
def get_kernel():
    """Return the kernel version string."""
    if S == "Windows":
        return platform.version()
    return platform.release()

def get_uptime():
    def _do():
        s = int(time.time() - psutil.boot_time())
        d, s = divmod(s, 86400)
        h, s = divmod(s, 3600)
        m, _ = divmod(s, 60)
        parts = []
        if d: parts.append(f"{d} day{'s' if d > 1 else ''}")
        if h: parts.append(f"{h} hour{'s' if h > 1 else ''}")
        parts.append(f"{m} min{'s' if m != 1 else ''}")
        return ", ".join(parts)
    return _try(_do)

@cached("packages", ttl=600)
def get_packages():
    """Count installed packages from all detected package managers."""
    # Order matters: prefer higher-level PMs (dnf/zypper) over rpm
    managers = [
        ("pacman", "pacman -Q 2>/dev/null | wc -l"),
        ("dpkg", "dpkg-query -f '.\n' -W 2>/dev/null | wc -l"),
        ("dnf", "dnf list installed 2>/dev/null | tail -n +2 | wc -l"),
        ("zypper", "zypper se --installed-only 2>/dev/null | tail -n +5 | wc -l"),
        ("rpm", "rpm -qa 2>/dev/null | wc -l"),
        ("apk", "apk info 2>/dev/null | wc -l"),
        ("brew", "brew list 2>/dev/null | wc -l"),
        ("xbps-query", "xbps-query -l 2>/dev/null | wc -l"),
        ("emerge", "find /var/db/pkg -mindepth 2 -maxdepth 2 -type d 2>/dev/null | wc -l"),
        ("nix-env", "nix-env -q 2>/dev/null | wc -l"),
        ("flatpak", "flatpak list 2>/dev/null | wc -l"),
        ("snap", "snap list 2>/dev/null | tail -n +2 | wc -l"),
    ]
    results, seen = [], set()
    # When a higher-level PM is found, skip its lower-level backend
    skip_aliases = {"dnf": {"rpm"}, "zypper": {"rpm"}, "rpm": {"dnf", "zypper"}}
    for name, command in managers:
        if name in seen or not _has(name):
            continue
        seen.add(name)
        try:
            out = _cmd(command, timeout=10)
            if not out:
                continue
            n = int(out.strip())
            if n > 0:
                results.append(f"{n} ({name})")
                seen |= skip_aliases.get(name, set())
        except (ValueError, OSError):
            continue
    return ", ".join(results) if results else "Unknown"

@cached("shell", ttl=3600)
def get_shell():
    """Detect the current shell name and version."""
    path = _env_text("SHELL") or _env_text("ComSpec")
    if not path:
        return "Unknown"
    name = os.path.basename(path)
    if S == "Windows":
        if name.lower().endswith(".exe"):
            name = name[:-4]
    ver_cmds = {
        "zsh": "zsh --version",
        "bash": "bash --version",
        "fish": "fish --version",
        "nu": "nu --version",
        "elvish": "elvish -version",
    }
    if name in ver_cmds:
        out = _cmd(ver_cmds[name])
        if out:
            m = re.search(r'(\d+\.\d+(?:\.\d+)?)', out)
            if m:
                return f"{name} {m.group(1)}"
    return name

@cached("resolution", ttl=600)
def get_resolution():
    """Detect the screen resolution."""
    def _do():
        if S == "Linux":
            st = _env_text("XDG_SESSION_TYPE").lower()
            if st == "wayland":
                if _has("hyprctl"):
                    out = _cmd("hyprctl monitors -j")
                    if out:
                        try:
                            monitors = json.loads(out)
                            if monitors:
                                m = monitors[0]
                                hz = _format_hz(m.get("refreshRate"))
                                if hz:
                                    return f"{m['width']}x{m['height']} @ {hz} Hz"
                                return f"{m['width']}x{m['height']}"
                        except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                            pass
                if _has("swaymsg"):
                    out = _cmd("swaymsg -t get_outputs")
                    if out:
                        try:
                            for o in json.loads(out):
                                if o.get("active"):
                                    m = o.get("current_mode", {})
                                    w, h = m.get("width"), m.get("height")
                                    if w and h:
                                        ref = m.get("refresh", 0)
                                        hz = _format_hz(ref / 1000 if ref > 1000 else ref)
                                        return f"{w}x{h} @ {hz} Hz" if hz else f"{w}x{h}"
                        except (json.JSONDecodeError, KeyError, TypeError):
                            pass
                if _has("wlr-randr"):
                    out = _cmd("wlr-randr")
                    if out:
                        for l in out.splitlines():
                            l = l.strip()
                            if "current" in l.lower() and "x" in l:
                                return l.split()[0]
            if _has("xrandr"):
                out = _cmd("xrandr | grep '*' | awk '{print $1}'")
                if out:
                    return out.split("\n")[0]
            for fb in glob.glob("/sys/class/graphics/fb*/modes"):
                m = _fread(fb)
                if m:
                    match = re.search(r'(\d+)x(\d+)', m)
                    if match:
                        return f"{match.group(1)}x{match.group(2)}"
        elif S == "Darwin":
            out = _cmd("system_profiler SPDisplaysDataType | grep Resolution")
            if out: return out.split(":")[-1].strip()
        elif S == "Windows":
            import ctypes
            u = ctypes.windll.user32
            return f"{u.GetSystemMetrics(0)}x{u.GetSystemMetrics(1)}"
    return _try(_do)

@cached("de", ttl=3600)
def get_desktop_env():
    """Detect the desktop environment."""
    def _do():
        if S == "Darwin":
            return "Aqua"
        if S == "Windows":
            return "Windows Shell"
        env = _env_text("XDG_CURRENT_DESKTOP") or _env_text("DESKTOP_SESSION")
        if not env:
            return None
        el = env.lower()
        if "kde" in el or "plasma" in el:
            out = _cmd("plasmashell --version")
            return f"KDE Plasma {out.split()[-1]}" if out else "KDE Plasma"
        if "gnome" in el:
            return _cmd("gnome-shell --version") or "GNOME"
        for name in ["xfce", "cinnamon", "mate", "lxqt", "budgie", "deepin", "lxde", "hyprland", "sway"]:
            if name in el:
                return name.upper() if len(name) <= 4 else name.capitalize()
        return env
    return _try(_do)

@cached("wm", ttl=3600)
def get_window_manager():
    """Detect the window manager."""
    def _do():
        if S == "Darwin":
            return "Quartz WM"
        if S == "Windows":
            return "DWM"
        st = _env_text("XDG_SESSION_TYPE").lower()
        if st == "wayland":
            desk = _env_text("XDG_CURRENT_DESKTOP").lower()
            if "hyprland" in desk:
                out = _cmd("hyprctl version -j")
                if out:
                    try:
                        return f"Hyprland {json.loads(out).get('tag', '')}".strip()
                    except (json.JSONDecodeError, KeyError):
                        pass
                return "Hyprland"
            if "sway" in desk:
                return "Sway"
            if "kde" in desk:
                return "KWin (Wayland)"
            if "gnome" in desk:
                return "Mutter (Wayland)"
            d = _env_text("XDG_CURRENT_DESKTOP")
            return f"Wayland ({d})" if d else "Wayland"
        if _has("wmctrl"):
            out = _cmd("wmctrl -m")
            if out:
                for l in out.splitlines():
                    if l.startswith("Name:"):
                        return l.split(":", 1)[1].strip()
        if _has("xprop"):
            out = _cmd("xprop -root _NET_WM_NAME")
            if out and "=" in out:
                return out.split("=")[-1].replace('"', '').strip()
    return _try(_do)

_SHELLS = frozenset({"python", "python3", "bash", "sh", "zsh", "fish", "dash", "node",
                     "login", "sudo", "su", "sshd", "init", "systemd", "csh", "tcsh",
                     "ksh", "nu", "elvish", "ion", "xonsh", "pwsh", "powershell"})

_WRAPPER_PROCS = frozenset({"env", "timeout", "stdbuf", "script", "sh", "bash", "zsh"})

# Map binary names to friendlier display names
_TERMINAL_NAMES = {
    "alacritty": "Alacritty",
    "kitty": "Kitty",
    "wezterm-gui": "WezTerm",
    "wezterm": "WezTerm",
    "gnome-terminal-server": "GNOME Terminal",
    "gnome-terminal": "GNOME Terminal",
    "konsole": "Konsole",
    "xfce4-terminal": "Xfce Terminal",
    "mate-terminal": "MATE Terminal",
    "tilix": "Tilix",
    "terminator": "Terminator",
    "foot": "Foot",
    "footclient": "Foot",
    "st": "st",
    "urxvt": "URxvt",
    "rxvt": "rxvt",
    "xterm": "xterm",
    "lxterminal": "LXTerminal",
    "sakura": "Sakura",
    "tmux": "tmux",
    "screen": "screen",
    "vscode": "VS Code",
    "code": "VS Code",
}

def get_terminal() -> str:
    """Detect the terminal emulator by walking the process tree."""
    for v in ("TERM_PROGRAM", "TERMINAL_EMULATOR"):
        t = _env_text(v)
        if t:
            return _TERMINAL_NAMES.get(t.lower().replace(" ", "-"), t)
    if S == "Windows":
        if _env_text("WT_SESSION"):
            return "Windows Terminal"
        if _env_text("ConEmuPID"):
            return "ConEmu"

    def _is_shell_or_wrapper(name: str) -> bool:
        n = name.lower()
        if n in _SHELLS or n in _WRAPPER_PROCS:
            return True
        # Skip versioned interpreter names like python3.12.
        return n.startswith("python")

    try:
        pid = os.getppid()
        visited = set()
        while pid > 1 and pid not in visited:
            visited.add(pid)
            try:
                proc = psutil.Process(pid)
                name = (proc.name() or "").strip()
            except (OSError, PermissionError):
                break
            if name and not _is_shell_or_wrapper(name):
                key = name.lower().replace(" ", "-")
                return _TERMINAL_NAMES.get(key, name)
            try:
                parent = proc.parent()
                pid = parent.pid if parent else 0
            except (psutil.Error, OSError, ValueError):
                break
    except Exception:
        pass
    term = _env_text("TERM", "Unknown")
    return term or "Unknown"

@cached("cpu", ttl=600)
def get_cpu():
    """Detect CPU model, core count, and frequency."""
    def _do():
        name = "Unknown CPU"
        if S == "Linux":
            try:
                with open("/proc/cpuinfo", encoding="utf-8") as f:
                    for l in f:
                        if l.startswith("model name"):
                            name = l.split(":", 1)[1].strip()
                            break
            except OSError:
                pass
            if name == "Unknown CPU":
                out = _cmd("lscpu 2>/dev/null | grep -i 'model name'")
                if out:
                    name = out.split(":", 1)[1].strip() if ":" in out else out.strip()
        elif S == "Darwin":
            name = _cmd("sysctl -n machdep.cpu.brand_string") or platform.processor() or name
        elif S == "Windows":
            out = _cmd("wmic cpu get name")
            if out:
                lines = [l.strip() for l in out.split("\n")[1:] if l.strip()]
                if lines: name = lines[0]
            if name == "Unknown CPU":
                name = platform.processor() or name
        else:
            name = platform.processor() or name
        freq = psutil.cpu_freq()
        cores = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count()
        if cores and threads:
            core_info = f"{cores}C/{threads}T" if cores != threads else str(threads)
        else:
            core_info = str(threads or cores or "?")
        if freq and freq.current:
            ghz = freq.current / 1000
            return f"{name} ({core_info}) @ {ghz:.2f} GHz"
        return f"{name} ({core_info})"
    return _try(_do)

@cached("gpu", ttl=3600)
def get_gpu():
    """Detect the primary GPU."""
    def _do():
        if S == "Windows":
            out = _cmd("wmic path win32_VideoController get name", timeout=10)
            if out:
                lines = [l.strip() for l in out.split("\n")[1:] if l.strip()]
                if lines:
                    return lines[0]
        elif S == "Linux":
            out = _cmd("lspci 2>/dev/null | grep -iE 'vga|3d|display'", timeout=10)
            if out:
                line = out.split("\n")[0]
                info = line.split(": ", 1)[1].strip() if ": " in line else line.strip()
                info = re.sub(r'\s*\(rev [0-9a-fA-F]+\)\s*$', '', info)
                # Clean up common vendor prefixes for brevity
                info = re.sub(r'^(Advanced Micro Devices,? Inc\.?\s*\[AMD(/ATI)?\]\s*)', 'AMD ', info)
                info = re.sub(r'^(NVIDIA Corporation\s*)', 'NVIDIA ', info)
                info = re.sub(r'^(Intel Corporation\s*)', 'Intel ', info)
                return truncate(info, 60)
        elif S == "Darwin":
            out = _cmd("system_profiler SPDisplaysDataType | grep -E 'Chipset|Chip'", timeout=10)
            if out:
                return out.split(":")[-1].strip()
    return _try(_do)

def get_memory():
    """Return used/total RAM with percentage."""
    try:
        m = psutil.virtual_memory()
        return f"{_gib(m.used)} GiB / {_gib(m.total)} GiB ({round(m.percent)}%)"
    except Exception:
        return "Unknown"

def get_swap():
    """Return used/total swap with percentage."""
    try:
        s = psutil.swap_memory()
        if s.total == 0:
            return "N/A"
        pct = round(s.percent) if hasattr(s, 'percent') else int(s.used / s.total * 100)
        return f"{_gib(s.used)} GiB / {_gib(s.total)} GiB ({pct}%)"
    except Exception:
        return "Unknown"

def get_disk():
    """Return used/total disk space with filesystem type on Linux."""
    try:
        d = psutil.disk_usage("/")
        base = f"{_gib(d.used)} GiB / {_gib(d.total)} GiB ({round(d.percent)}%)"
        if S == "Linux":
            fs = _cmd("df -T / | tail -1 | awk '{print $2}'")
            if fs:
                return f"{base} - {fs}"
        return base
    except Exception:
        return "Unknown"

def get_ip() -> str:
    """Return the local IP address with interface name on Linux."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        if S == "Linux":
            out = _cmd(f"ip -o addr show | grep -wF '{ip}'")
            if out:
                parts = out.splitlines()[0].split()
                iface = parts[1] if len(parts) > 1 else None
                cidr = parts[3] if len(parts) > 3 else ip
                return f"{cidr} ({iface})" if iface else cidr
        return ip
    except Exception:
        return "Unavailable"
    finally:
        if sock:
            try:
                sock.close()
            except Exception:
                pass

def get_battery():
    """Detect battery charge level and charging status."""
    def _do():
        if S == "Linux":
            bp = next(iter(sorted(Path("/sys/class/power_supply").glob("BAT*"))), None)
            if not bp:
                return "N/A"
            cap = (bp / "capacity").read_text(encoding="utf-8").strip()
            st = (bp / "status").read_text(encoding="utf-8").strip().lower()
            label = "Charging" if st == "charging" else "Full" if st == "full" else "Discharging"
            return f"{cap}% [{label}]"
        b = psutil.sensors_battery()
        if not b:
            return "N/A"
        if b.power_plugged:
            label = "Full" if b.percent >= 100 else "Charging"
        else:
            label = "Discharging"
        return f"{round(b.percent)}% [{label}]"
    return _try(_do, "N/A")

def get_locale():
    """Return the system locale."""
    try:
        return locale.getlocale()[0] or _env_text("LANG", "Unknown").split(".")[0]
    except Exception:
        return "Unknown"

def get_color_blocks():
    """Generate terminal color palette blocks (neofetch-style)."""
    normal = ''.join(f'\033[4{i}m   ' for i in range(8)) + '\033[0m'
    bright = ''.join(f'\033[10{i}m   ' for i in range(8)) + '\033[0m'
    return [normal, bright]

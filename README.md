# ezfetch

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)](https://github.com/wtfenzo/ezfetch)

> A blazing-fast, highly customizable, cross-platform system information tool written in Python.

Inspired by neofetch but with modern features, extensive customization, better performance, and rich CLI options.

---

## ✨ Features

**See also:**
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Configuration Guide](docs/configuration.md)


- **⚡ Fast & Lightweight** — Pure Python with minimal dependencies (only psutil)
- **🌍 Cross-platform** — Linux (X11/Wayland), macOS, Windows, and Termux
- **🎨 Beautiful Output** — ASCII art logos with customizable color themes
- **📊 Comprehensive Info** — OS, CPU, GPU, RAM, resolution, shell, uptime, DE/WM, and more
- **🎭 Multiple Themes** — 6 built-in themes (default, nord, dracula, gruvbox, monokai, solarized)
- **🐧 16+ Logos** — Arch, Ubuntu, Debian, Fedora, Manjaro, Pop!_OS, Alpine, Gentoo, Kali, and more
- **⚙️ Highly Configurable** — JSON config file with extensive options ([see Configuration Guide](docs/configuration.md))
- **🎯 Smart Detection** — Auto-identifies desktop environments and window managers
- **📦 Smart Caching** — Cache expensive operations (3x faster on cached runs)
- **🔧 Rich CLI** — 11+ command-line options for quick customization
- **📄 JSON Export** — Machine-readable output for scripting and automation

---

## 📥 Installation

**Having issues?** See the [Troubleshooting Guide](docs/troubleshooting.md).

### Quick Start (Recommended - Works Instantly!)

```bash
# Shallow clone for faster download (~2MB vs 25MB)
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch
python3 -m ezfetch
```

**That's it!** No pip, no dependencies installation needed. Just clone and run! 🚀

### Install System-wide

#### On Arch Linux / Manjaro:
```bash
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch

# Option 1: Run directly (Recommended - No installation needed)
python3 -m ezfetch

# Option 2: Install with pipx (Arch Linux best practice)
sudo pacman -S python-pipx
pipx install .

# Option 3: System-wide with --break-system-packages (Not recommended)
pip install --user --break-system-packages -e .
```

#### On Ubuntu / Debian:
```bash
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch
# Recommended: virtual environment (works with PEP 668)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 -m ezfetch
```

#### On macOS:
```bash
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python3 -m ezfetch
```

#### Generic (Works Everywhere):
```bash
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch
# Run directly without installation
python3 -m ezfetch
```

#### Windows (PowerShell):
```powershell
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch
./scripts/install.ps1
```

---

## 🚀 Usage

**Configuration tips and more examples:** See [Configuration Guide](docs/configuration.md).

### Basic Usage

```bash
# If installed system-wide
ezfetch
```

### Command-Line Options

```bash
# Show version
ezfetch --version

# Use a specific logo
ezfetch --logo arch
ezfetch --logo ubuntu

# List all available logos
ezfetch --list-logos

# Use a color theme
ezfetch --theme nord
ezfetch --theme dracula

# List all available themes
ezfetch --list-themes

# Hide the logo
ezfetch --no-logo

# Disable colors
ezfetch --no-color

# Use custom logo
ezfetch --custom-logo /path/to/ascii-art.txt

# Export as JSON
ezfetch --json

# Show specific fields only
ezfetch --field OS --field CPU --field Memory

# Use custom config file
ezfetch --config /path/to/config.json
```

---

## ⚙️ Configuration ([Full Guide](docs/configuration.md))

ezfetch creates a config file at `~/.config/ezfetch/config.json` which you can customize. For advanced configuration, see [docs/configuration.md](docs/configuration.md).

### Example Configuration

```json
{
  "display": {
    "show_logo": true,
    "show_colors": true,
    "truncate_length": 50,
    "show_color_blocks": true
  },
  "theme": {
    "name": "default"
  },
  "fields": {
    "enabled": [
      "User",
      "Host",
      "OS",
      "Kernel",
      "Uptime",
      "Packages",
      "Shell",
      "Resolution",
      "DE",
      "WM",
      "Terminal",
      "CPU",
      "GPU",
      "Memory",
      "Swap",
      "Disk",
      "Local IP",
      "Battery",
      "Locale"
    ],
    "hide_unavailable": true,
    "hide_unknown": false
  },
  "performance": {
    "cache_enabled": true,
    "cache_duration": 300
  }
}
```

---

## 🎨 Available Themes

- **default** — Classic green and cyan
- **nord** — Cool northern palette
- **dracula** — Dark purple theme
- **gruvbox** — Retro warm colors
- **monokai** — Sublime Text inspired
- **solarized** — Precision colors

---

## 🐧 Supported Logos

- Arch Linux
- Ubuntu
- Debian
- Linux Mint
- Fedora
- Red Hat
- Manjaro
- Pop!_OS
- Alpine Linux
- Gentoo
- Kali Linux
- macOS
- Windows

*Custom logos supported via `--custom-logo` flag!*

---

## 📦 System Information Displayed

- **User & Host** — Current user and hostname
- **OS** — Operating system name and version
- **Kernel** — Kernel version
- **Uptime** — System uptime
- **Packages** — Number of installed packages (supports dpkg, rpm, pacman, apt, dnf, brew, etc.)
- **Shell** — Current shell with version
- **Resolution** — Screen resolution (X11/Wayland)
- **Desktop Environment** — DE with version (GNOME, KDE, XFCE, etc.)
- **Window Manager** — WM detection (Mutter, KWin, i3, Hyprland, etc.)
- **Terminal** — Terminal emulator
- **CPU** — Processor model, cores, and frequency
- **GPU** — Graphics card information
- **Memory** — RAM usage (used/total)
- **Swap** — Swap memory usage
- **Disk** — Disk usage with filesystem type
- **Local IP** — Network interface and IP address
- **Battery** — Battery status and percentage (laptops)
- **Locale** — System locale

---

## 🔧 Advanced Features

### Fast Installation

For the **fastest download**, use shallow clone:
```bash
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
```

**Benefits:**
- **90% smaller download** (~2MB vs 20MB full clone)
- **10x faster** clone time
- Only downloads latest version (recommended for most users)
- Full functionality preserved

### Caching

ezfetch intelligently caches slow operations (like package counting) in `~/.cache/ezfetch/` to improve performance. Cache duration is configurable.

### Custom Colors

You can use RGB/hex colors in themes:

```python
from ezfetch.colors import rgb, from_hex

# Use RGB
custom_color = rgb(255, 87, 51)

# Use hex
custom_color = from_hex("#FF5733")
```

### JSON Output

Perfect for scripting and automation:

```bash
ezfetch --json | jq '.CPU'
```

---

### Custom Configuration

Create `~/.config/ezfetch/config.json`:
```json
{
  "fields": {
    "enabled": ["User", "OS", "Shell", "CPU", "Memory"]
  },
  "theme": {
    "name": "dracula"
  }
}
```

### Integration Examples

```bash
# Minimal output
python3 -m ezfetch --no-logo --field OS --field CPU --field Memory

# Specific theme and logo
python3 -m ezfetch --logo arch --theme nord

# JSON with jq filtering
python3 -m ezfetch --json | jq '.CPU'

# Save system info
python3 -m ezfetch --json > system-info.json
```

---

## 🔧 Troubleshooting ([Full Guide](docs/troubleshooting.md))


For more troubleshooting tips and platform-specific help, see [docs/troubleshooting.md](docs/troubleshooting.md).

### "externally-managed-environment" error (Arch Linux)

Modern Arch Linux uses PEP 668 to prevent pip conflicts. Solutions:

**Best option - Run directly (no installation):**
```bash
python3 -m ezfetch
```

**Or use pipx (recommended for system-wide install):**
```bash
sudo pacman -S python-pipx
pipx install .
ezfetch
```

**Or use virtual environment:**
```bash
python3 -m venv ~/ezfetch-env
source ~/ezfetch-env/bin/activate
pip install -e .
ezfetch
```

### "pip: command not found"

**Arch Linux / Manjaro:**
```bash
sudo pacman -S python-pip
# Or use pipx instead: sudo pacman -S python-pipx
```

**Ubuntu / Debian:**
```bash
sudo apt install python3-pip
```

**Fedora:**
```bash
sudo dnf install python3-pip
```

### "python3: command not found"

**Install Python 3:**
```bash
# Arch Linux
sudo pacman -S python

# Ubuntu/Debian
sudo apt install python3

# Fedora
sudo dnf install python3
```

### "ModuleNotFoundError: No module named 'psutil'"

```bash
# With pip
pip3 install --user psutil

# Arch Linux
sudo pacman -S python-psutil

# Ubuntu/Debian
sudo apt install python3-psutil
```

### Clone is too slow / too large

Use shallow clone for faster download:
```bash
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
```
This downloads only ~2MB instead of 25MB!

---

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Issues:** [Report bugs or request features](https://github.com/wtfenzo/ezfetch/issues)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits

- **Inspired by:** [neofetch](https://github.com/dylanaraps/neofetch)
- **Created by:** yokaimsi & himonshuuu
- **ASCII Logos:** Various open-source projects

---

## 🔗 Links

- **Repository:** [github.com/wtfenzo/ezfetch](https://github.com/wtfenzo/ezfetch)
- **Issues:** [Bug Reports & Feature Requests](https://github.com/wtfenzo/ezfetch/issues)
<<<<<<< HEAD
- **Version:** 1.1.0
=======
- **Version:** 1.3.0
>>>>>>> 5b477de (feat: mproved distro detection)

---

**Made with ❤️ by the ezfetch team**

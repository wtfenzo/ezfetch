# ezfetch

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Fast, cross-platform system info for the terminal.

ezfetch is inspired by neofetch, with a clean Python codebase, JSON output, and practical customization.

## Why ezfetch

- Fast startup with optional disk caching
- Linux, macOS, and Windows support
- Themed output with built-in logos
- JSON mode for scripts and automation
- Config file for persistent customization

## Quick Start

Run directly from source (no install required):

```bash
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch
python3 -m ezfetch
```

Optional install in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
ezfetch
```

Global install (recommended for running `ezfetch` from any directory):

```bash
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch
make install-global
ezfetch
```

Manual global install options:

```bash
# Best on modern Linux systems (PEP 668-safe)
pipx install .

# Alternative fallback (isolated local venv + symlink)
bash scripts/install.sh
```

Windows PowerShell:

```powershell
git clone --depth 1 https://github.com/wtfenzo/ezfetch.git
cd ezfetch
./scripts/install.ps1
```

If `ezfetch` is not found after installation, add `~/.local/bin` to PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Usage

```bash
# Standard output
ezfetch

# JSON output
ezfetch --json

# Choose logo/theme
ezfetch --logo arch --theme nord

# Show only selected fields
ezfetch --field OS --field CPU --field Memory

# Disable logo/colors
ezfetch --no-logo --no-color
```

## Configuration

Default config path:

```text
~/.config/ezfetch/config.json
```

Minimal example:

```json
{
  "theme": { "name": "dracula" },
  "fields": { "enabled": ["User", "OS", "CPU", "Memory"] },
  "performance": { "cache_enabled": true, "cache_duration": 300 }
}
```

## Docs

- Full configuration: [docs/configuration.md](docs/configuration.md)
- Troubleshooting: [docs/troubleshooting.md](docs/troubleshooting.md)
- Additional docs index: [docs/README.md](docs/README.md)

## License

MIT

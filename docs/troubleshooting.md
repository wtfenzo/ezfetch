# ezfetch Troubleshooting

This guide provides solutions to common issues and errors you may encounter when installing or running ezfetch.

---

## Table of Contents
- [Common Issues](#common-issues)
- [Dependency Problems](#dependency-problems)
- [Configuration Issues](#configuration-issues)
- [Platform-specific Notes](#platform-specific-notes)
- [Reporting Bugs](#reporting-bugs)

---

## Common Issues

### 1. Command Not Found
- Install globally with one of these options:
  - `make install-global`
  - `pipx install .`
  - `bash scripts/install.sh`
- Verify installation and PATH:
  ```bash
  command -v ezfetch
  ezfetch --version
  ```
- If it is still not found, add `~/.local/bin` to PATH:
  ```bash
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  source ~/.bashrc
  ```

### 2. ImportError: No module named 'psutil'
- Run `pip install -r requirements.txt` in the project directory to install dependencies.

### 3. Permission Denied
- If installing system-wide, use `sudo` where appropriate.
- For user installs, ensure your user has write access to the install location.

---

## Dependency Problems
- ezfetch requires Python 3.8+ and the `psutil` package.
- If your distro enforces PEP 668 (externally managed Python), use the built-in Make targets. They create and use a local `.venv` automatically.
- Example:
  ```bash
  make test
  make build
  ```
- For global command installation on PEP 668 systems, prefer `pipx`:
  ```bash
  pipx install .
  ```
- If you see this error:
  `externally-managed-environment`
  it means direct `pip install --user .` is blocked by your distro policy. Use `pipx` or `bash scripts/install.sh`.
- If you see errors about missing modules, run:
  ```bash
  pip install -r requirements.txt
  ```

## Installation Validation

Run these checks after installing globally:

```bash
make doctor
```

or manually:

```bash
ezfetch --json --no-cache
(cd /tmp && ezfetch --version)
```

---

## Configuration Issues
- If ezfetch fails to load or save configuration, check permissions for `~/.config/ezfetch/`.
- Delete or fix a corrupted config file at `~/.config/ezfetch/config.json`.

---

## Platform-specific Notes
- **Windows:** Use PowerShell and ensure Python is in your PATH.
- **Linux:** Works on most distros. For Wayland/X11 info, ensure `xrandr` or `wlr-randr` is available.
- **macOS:** Some info fields may be limited due to OS restrictions.

---

## Reporting Bugs
- Please open an issue at https://github.com/wtfenzo/ezfetch/issues with details and error messages.

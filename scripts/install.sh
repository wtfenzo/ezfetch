#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BIN_DIR="${EZFETCH_BIN_DIR:-${HOME}/.local/bin}"
FALLBACK_VENV="${EZFETCH_VENV_DIR:-${HOME}/.local/share/ezfetch/venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PATH_HINT_SHOWN=0

log() {
    printf '[ezfetch-install] %s\n' "$*"
}

fail() {
    printf '[ezfetch-install] ERROR: %s\n' "$*" >&2
    exit 1
}

path_hint() {
    local target_dir="${1:-${BIN_DIR}}"
    if [[ "${PATH_HINT_SHOWN}" -eq 1 ]]; then
        return
    fi
    if [[ ":${PATH}:" != *":${target_dir}:"* ]]; then
        log "${target_dir} is not currently in PATH."
        log "Add this line to your shell rc file (for example ~/.bashrc or ~/.zshrc):"
        printf 'export PATH="%s:$PATH"\n' "${target_dir}"
        PATH_HINT_SHOWN=1
    fi
}

install_with_pipx() {
    log "pipx detected. Installing ezfetch globally with an isolated environment..."
    pipx install "${REPO_DIR}" --force
    pipx ensurepath >/dev/null 2>&1 || true
}

install_with_local_venv() {
    command -v "${PYTHON_BIN}" >/dev/null 2>&1 || fail "python3 is required but was not found in PATH"
    log "pipx is not available. Using isolated user venv fallback at ${FALLBACK_VENV}"
    "${PYTHON_BIN}" -m venv "${FALLBACK_VENV}"
    "${FALLBACK_VENV}/bin/python" -m pip install --upgrade pip
    "${FALLBACK_VENV}/bin/python" -m pip install --upgrade "${REPO_DIR}"

    mkdir -p "${BIN_DIR}"
    ln -sf "${FALLBACK_VENV}/bin/ezfetch" "${BIN_DIR}/ezfetch"
}

verify_install() {
    if command -v ezfetch >/dev/null 2>&1; then
        path_hint "$(dirname "$(command -v ezfetch)")"
        log "Installation complete. Run: ezfetch"
        return
    fi

    if [[ -x "${BIN_DIR}/ezfetch" ]]; then
        log "Installation complete. '${BIN_DIR}/ezfetch' is ready."
        path_hint
        return
    fi

    fail "Installation finished but ezfetch could not be found. Check output above for details."
}

if command -v pipx >/dev/null 2>&1; then
    install_with_pipx
else
    install_with_local_venv
fi

verify_install
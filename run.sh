#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
REQUIREMENTS_HASH_FILE="$VENV_DIR/.requirements.sha256"

pick_python() {
  if command -v python3.11 >/dev/null 2>&1; then
    command -v python3.11
    return
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return
  fi

  echo "Error: python3.11/python3 not found." >&2
  exit 1
}

ensure_python_version() {
  local py_bin="$1"
  local ver
  ver="$("$py_bin" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
  local major="${ver%%.*}"
  local minor="${ver##*.}"
  if [[ "$major" -lt 3 || ( "$major" -eq 3 && "$minor" -lt 10 ) ]]; then
    echo "Error: Python >= 3.10 is required, found $ver at $py_bin" >&2
    exit 1
  fi
}

venv_activate_path() {
  local activate_file="$1"
  if [[ ! -f "$activate_file" ]]; then
    return
  fi
  sed -n \
    -e 's/^VIRTUAL_ENV="\([^"]*\)"/\1/p' \
    -e 's/^VIRTUAL_ENV=\(.*\)/\1/p' \
    "$activate_file" | head -n 1
}

recreate_venv_if_needed() {
  local py_bin="$1"
  local recreate=0

  if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    recreate=1
  fi

  local configured_venv
  configured_venv="$(venv_activate_path "$VENV_DIR/bin/activate" || true)"
  if [[ -n "${configured_venv:-}" && "$configured_venv" != "$VENV_DIR" ]]; then
    recreate=1
  fi

  if [[ "$recreate" -eq 1 ]]; then
    rm -rf "$VENV_DIR"
    "$py_bin" -m venv "$VENV_DIR"
  fi
}

install_deps_if_needed() {
  if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
    echo "Error: requirements.txt not found at $REQUIREMENTS_FILE" >&2
    exit 1
  fi

  local current_hash
  current_hash="$(shasum -a 256 "$REQUIREMENTS_FILE" | awk '{print $1}')"
  local installed_hash=""
  if [[ -f "$REQUIREMENTS_HASH_FILE" ]]; then
    installed_hash="$(cat "$REQUIREMENTS_HASH_FILE")"
  fi

  if [[ "$current_hash" != "$installed_hash" ]]; then
    pip install -r "$REQUIREMENTS_FILE"
    printf "%s\n" "$current_hash" > "$REQUIREMENTS_HASH_FILE"
  fi
}

main() {
  local py_bin
  py_bin="$(pick_python)"
  ensure_python_version "$py_bin"
  recreate_venv_if_needed "$py_bin"

  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
  install_deps_if_needed

  exec streamlit run "$PROJECT_DIR/app.py" "$@"
}

main "$@"

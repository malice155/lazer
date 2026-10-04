#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
if ! python3 -c "import venv, ensurepip" 2>/dev/null; then
  echo "Need python3-venv (Debian/Ubuntu: sudo apt install python3.12-venv)" >&2
  exit 1
fi
python3 -m venv "${ROOT}/.venv"
"${ROOT}/.venv/bin/python" -m pip install -U pip
"${ROOT}/.venv/bin/python" -m pip install -r "${ROOT}/requirements.txt"
"${ROOT}/.venv/bin/python" -c "import cadquery as cq; print('cadquery', cq.__version__)"
echo "OK. Run: ${ROOT}/.venv/bin/python ${ROOT}/build.py"

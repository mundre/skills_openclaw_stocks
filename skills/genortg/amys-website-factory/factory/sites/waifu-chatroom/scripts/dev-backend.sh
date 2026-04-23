#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -d backend/.venv ]]; then
  echo "Create venv first: cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

source backend/.venv/bin/activate
uvicorn app.main:app --reload --port 8000 --app-dir backend

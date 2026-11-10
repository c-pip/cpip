#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "🤖 Starting SwarmDroid Multi-Agent AI Backend..."

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r backend/requirements.txt
fi

export PYTHONPATH="$DIR"
.venv/bin/uvicorn backend.main:app --host "${SWARMDROID_HOST:-0.0.0.0}" --port "${SWARMDROID_PORT:-8000}" --reload

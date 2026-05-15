#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

export USE_MOCK_TRANSLATION="${USE_MOCK_TRANSLATION:-true}"

echo "Starting API on http://localhost:8000"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Ensure frontend static export is built if missing
if [[ ! -f "frontend/out/index.html" ]]; then
  echo "Building frontend static export (next build)..."
  (cd frontend && npm run build)
fi

# Prefer backend virtualenv python if available
PYTHON="python3"
if [[ -f "backend/.venv/bin/python3" ]]; then
  PYTHON="backend/.venv/bin/python3"
elif [[ -n "${VIRTUAL_ENV:-}" && -f "${VIRTUAL_ENV}/bin/python3" ]]; then
  PYTHON="${VIRTUAL_ENV}/bin/python3"
fi

exec "$PYTHON" -m uvicorn backend.app.main:app \
  --host "${BACKEND_HOST:-127.0.0.1}" \
  --port "${BACKEND_PORT:-8010}"
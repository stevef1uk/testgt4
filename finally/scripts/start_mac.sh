#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Preserve any existing environment variables exported by the user in their shell
USER_OPENROUTER_KEY="${OPENROUTER_API_KEY:-}"
USER_LLM_MOCK="${LLM_MOCK:-}"
USER_MASSIVE_KEY="${MASSIVE_API_KEY:-}"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Restore user's exported variables if set
if [[ -n "$USER_OPENROUTER_KEY" ]]; then
  export OPENROUTER_API_KEY="$USER_OPENROUTER_KEY" allow-secret: env var pass-through, no literal secret value
fi
if [[ -n "$USER_MASSIVE_KEY" ]]; then
  export MASSIVE_API_KEY="$USER_MASSIVE_KEY" allow-secret: env var pass-through, no literal secret value
fi

# If a real OPENROUTER_API_KEY is present and user didn't explicitly force mock mode, default to live LLM
if [[ -n "${OPENROUTER_API_KEY:-}" && "${OPENROUTER_API_KEY}" != "your-openrouter-api-key-here" ]]; then
  if [[ -n "$USER_LLM_MOCK" ]]; then
    export LLM_MOCK="$USER_LLM_MOCK"
  else
    export LLM_MOCK=false
  fi
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

exec "$PYTHON" -m uvicorn app.main:app \
  --app-dir "$ROOT/backend" \
  --host "${BACKEND_HOST:-127.0.0.1}" \
  --port "${BACKEND_PORT:-8010}"
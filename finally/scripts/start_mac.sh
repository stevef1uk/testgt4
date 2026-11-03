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

: "${HOST:=0.0.0.0}"
: "${PORT:=8000}"

mkdir -p db
nohup python -m uvicorn backend.app.main:app --host "$HOST" --port "$PORT" \
  >> db/polecat.log 2>&1 &
echo "$!" > "${TMPDIR:-/tmp}/polecat.pid"
echo "Polecat started with PID $! on ${HOST}:${PORT}"
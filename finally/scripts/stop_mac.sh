#!/usr/bin/env bash
set -euo pipefail

PID_FILE="${TMPDIR:-/tmp}/polecat.pid"

if [[ -f "$PID_FILE" ]]; then
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
    for _ in {1..20}; do
      kill -0 "$pid" 2>/dev/null || break
      sleep 0.25
    done
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid"
    fi
  fi
  rm -f "$PID_FILE"
fi
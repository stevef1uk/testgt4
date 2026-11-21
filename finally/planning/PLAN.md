# Project Foundation Support Plan

## Scope

Deliver the support artifacts required for local development, database
initialization, cross-platform lifecycle commands, and CI validation.

## Acceptance

- The checked-in `.env` contains only non-secret development defaults.
- The SQLite schema initializes idempotently with the SPEC-defined default
  account and ten-ticker watchlist.
- The database directory is retained with `.gitkeep`.
- macOS and Windows scripts use the configured backend host and port.
- `.gitignore` excludes generated local state without hiding required source
  artifacts.
- CI validates the support files and schema module.

## Verification

test -f finally/planning/PLAN.md
test -f finally/scripts/start_mac.sh
test -f finally/scripts/stop_mac.sh
test -f finally/scripts/start_windows.ps1
test -f finally/scripts/stop_windows.ps1
test -f finally/.env
test -f finally/.gitignore
test -f finally/.github/workflows/ci.yml
test -f finally/db/.gitkeep
test -f finally/backend/db/schema.py
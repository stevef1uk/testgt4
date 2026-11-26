# Test Review — project-foundation-support

## Summary
Phase verify FAILED (exit 1). The verify ran as `docker build -f Dockerfile` from the rig root, and pytest targeted `finally/tests/test_schema.py`. Both paths are wrong for this layout. The configured command uses `(cd finally && docker build ...)` and `(cd finally/backend && uv run pytest tests/test_schema.py -q)`. No green run of the configured command has been observed.

## Per-requirement results
### te-44z (project-foundation-support: schema and seed) — FAIL (verify not green)
- Test file: finally/backend/tests/test_schema.py
- Verify result: exit 1, `failed to read dockerfile: open Dockerfile: no such file or directory`
- Notes: The test file has real assertions. Coverage for the finding:
  - Schema file present and creates tables: lines 42, 47
  - UNIQUE (user_id, ticker) on watchlist: lines 73-76
  - UNIQUE on positions: lines 86-90
  - Seed cash of 10000.0 and exact ten tickers: lines 101, 109
  - Idempotent seed count: line 118
  Coverage is adequate in the test file. The phase verify has not passed, so the requirement is not satisfied.

## Evidence
- Evidence: {"file":"finally/backend/tests/test_schema.py","line":42,"excerpt":"    assert SCHEMA_PATH.is_file()"}
- Evidence: {"file":"finally/backend/tests/test_schema.py","line":101,"excerpt":"    assert profile[\"cash_balance\"] == pytest.approx(10000.0)"}
- Evidence: {"file":"finally/backend/tests/test_schema.py","line":109,"excerpt":"    assert tickers == set(seed.DEFAULT_WATCHLIST)"}
- Evidence: {"file":"finally/backend/tests/test_schema.py","line":118,"excerpt":"    assert count == len(seed.DEFAULT_WATCHLIST)"}

## Overall assessment
FAIL. The phase verify did not exit green. The stale command still runs from the rig root. Polecat must confirm the verify runs from the correct directories. Owning bead to reopen: te-44z. Future-phase rows are deferred.

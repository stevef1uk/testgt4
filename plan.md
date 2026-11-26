# Implementation plan: testing-release

## Scope

Phase `testing-release` (canonical ID per SPEC Section 14.2; Phase 8 in SPEC). Six implement beads, one per `required_files` entry in architecture.md. Every path keeps the `finally/` layout-root prefix and its nested directories exactly as listed. No other phase's files are in scope.

Sources: SPEC.md Section 12 (Testing Strategy), Section 13 (Playwright E2E Specification), Section 14 (design contract); architecture.md "Delivery phases" (testing-release entry), "Unit tests", "E2E / integration testing", "Docker & Deployment".

Integration contract: not required for this phase. The phase's required_files contain no server entrypoint file; the server entrypoint `finally/backend/app/main.py` is owned by project-foundation and is consumed here only over HTTP.

## Bead map

### te-2iz: finally/backend/tests/test_api.py
- Scope: full API contract test module exercising the FastAPI app built by `create_app(...) -> FastAPI` in `finally/backend/app/main.py`.
- Architecture: "Unit tests" entry for test_api.py; "HTTP + entrypoint integration" route list (SPEC Section 8 verbatim).
- Interfaces: HTTP-only; imports `create_app` from `app.main`; no direct DB writes.
- Depends on: finally/backend/app/main.py, finally/backend/app/api/routes_portfolio.py, finally/backend/app/api/routes_watchlist.py, finally/backend/app/api/routes_chat.py, finally/backend/app/market/stream.py (owned by earlier phases).
- Consumed by: <none>
- Acceptance:
  - GET / returns the real dashboard HTML: heading "FinAlly", the ten tickers (AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX), and the "$10,000" cash figure. A placeholder page fails the test.
  - GET /api/health returns success.
  - Every route in SPEC Section 8 is exercised for method, path, and response shape: /api/stream/prices (and alias /api/stream), /api/portfolio, /api/portfolio/trade, /api/portfolio/history, /api/watchlist (GET, POST, DELETE /{ticker}), /api/chat.
  - Missing export directory returns 503 with a diagnostic body, not a fallback page.
  - Assertions check returned values and state, not status codes alone.
- Verify: `cd finally/backend && uv run pytest tests/test_api.py -q`

### te-rak: finally/test/package.json
- Scope: npm manifest for the E2E harness in `finally/test/`. Declares `@playwright/test` and test utilities.
- Architecture: "E2E harness" file list; SPEC Section 13 "Directory layout".
- Interfaces: package name and devDependencies consumed by `npm install` in the Playwright container.
- Depends on: <none>
- Consumed by: finally/test/playwright.config.ts, finally/test/docker-compose.test.yml, finally/test/e2e.spec.ts.
- Acceptance:
  - `@playwright/test` is a declared devDependency.
  - Manifest installs cleanly with `npm install --ignore-scripts`.
- Verify: `cd finally/test && npm install --ignore-scripts`

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration for the chromium-only E2E run.
- Architecture: SPEC Section 13 "Playwright configuration".
- Interfaces: exports the default Playwright config object.
- Depends on: finally/test/package.json.
- Consumed by: finally/test/e2e.spec.ts; finally/test/docker-compose.test.yml runs it.
- Acceptance:
  - `baseURL` is `process.env.BASE_URL || 'http://localhost:8010'`.
  - `timeout` 30s per test; expect timeout 60s per assertion.
  - `retries: 1`.
  - Single project `chromium` using `devices['Desktop Chrome']`.
  - Reporter `[['html', { open: 'never' }], ['list']]`.
  - No `webServer` block (Docker Compose manages the app).
- Verify: `cd finally/test && npx playwright test --list`

### te-9o3: finally/test/docker-compose.test.yml
- Scope: compose harness with an `app` service and a `playwright` service.
- Architecture: "Harness contract" in SPEC Section 12; architecture.md "E2E / integration testing".
- Interfaces: `app` service builds from context `..` (project root) so the real `finally/Dockerfile` is used; `playwright` service mounts `..:/app`.
- Depends on: finally/Dockerfile (owned by project-foundation-support), finally/test/playwright.config.ts, finally/test/package.json.
- Consumed by: test runners only.
- Acceptance:
  - `app.build.context` is `..`.
  - `app` sets `LLM_MOCK=true`; healthcheck is `curl -f http://localhost:8010/api/health`.
  - `playwright` sets `BASE_URL=http://app:8010` and runs `cd /app/test && npm install && npx playwright test --project=chromium`.
  - Compose paths resolve relative to `finally/test/`.
- Verify: `cd finally/test && docker compose -f docker-compose.test.yml config -q`

### te-7by: finally/test/e2e.spec.ts
- Scope: Playwright scenarios from SPEC Section 13 (dashboard, watchlist, trading, portfolio, chat, SSE, navigation, full happy path). Selectors use `getByRole`, `getByText`, or `getByTestId` only.
- Architecture: SPEC Section 13 mandatory coverage tables; architecture.md "E2E / integration testing".
- Interfaces: drives the DOM contracts from SPEC Section 10 (`data-testid="connection-status"`, `cash-balance`, `portfolio-summary`, `positions-table`, `trading-panel`; `aria-label="Chat assistant"`, `aria-label="Chat message"`).
- Depends on: finally/test/playwright.config.ts, finally/test/package.json, finally/test/docker-compose.test.yml.
- Consumed by: <none>
- Acceptance:
  - Fresh load asserts "FinAlly" heading, all ten ticker symbols, "$10,000".
  - At least one browser interaction with state-change assertion: Buy 10 AAPL reduces cash and adds a position row; Send in chat shows an assistant reply.
  - Insufficient-cash and oversell cases assert error text and unchanged state.
  - Chat assertions require non-empty text and reject raw JSON braces.
  - No test asserts placeholder text such as "Coming soon".
- Verify: `cd finally/test && npx playwright test --list`

### te-5n9: finally/planning/PLAN.md
- Scope: project-wide planning document for agents, written under `finally/planning/`. Summarises the delivery phases, the bead-to-file mapping, and the release checklist (Docker validation, README, environment examples).
- Architecture: "Layout" entry for `finally/planning/PLAN.md`; SPEC Section 4 (`planning/`) and Section 12 Release.
- Interfaces: documentation only; no code exports.
- Depends on: <none>
- Consumed by: <none>
- Acceptance:
  - File exists at `finally/planning/PLAN.md` with the phase list from architecture.md.
  - Contains exit criteria for testing-release from SPEC Section 14.3.
  - No placeholder text.
- Verify: `test -f finally/planning/PLAN.md && wc -c finally/planning/PLAN.md`

## Dependency order

1. te-rak (finally/test/package.json)
2. te-eku (finally/test/playwright.config.ts)
3. te-9o3 (finally/test/docker-compose.test.yml)
4. te-7by (finally/test/e2e.spec.ts)
5. te-2iz (finally/backend/tests/test_api.py)
6. te-5n9 (finally/planning/PLAN.md)

## Future considerations

- Additional E2E scenarios beyond SPEC Section 13 are out of scope for this phase.

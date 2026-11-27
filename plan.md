# Implementation plan — testing-release

Active phase: `testing-release` (Phase 8, Testing & Release). Depends on `application-polish`. Scope is limited to the six `required_files` for this phase. Earlier-phase files are not in scope here.

Phase verification (architecture `qa_verify_command`): `(cd finally/backend && uv run pytest tests/test_api.py -q) && (cd finally/test && npm install --ignore-scripts && npx playwright test --list)`. The polecat must also execute the browser suite with `npx playwright test --project=chromium` to completion (SPEC Section 13 forbids enumeration-only as proof).

File dependency order (acyclic, earliest first):
1. `finally/test/package.json` (root; no file dependencies)
2. `finally/test/playwright.config.ts` (depends on package.json)
3. `finally/test/docker-compose.test.yml` (depends on package.json, playwright.config.ts, and project Dockerfile)
4. `finally/test/e2e.spec.ts` (depends on playwright.config.ts and the API contract in test_api.py)
5. `finally/backend/tests/test_api.py` (depends on the backend app and schemas)
6. `finally/planning/PLAN.md` (documentation; depends on nothing in code)

## Bead map

### te-rak: finally/test/package.json
- Scope: E2E harness manifest declaring `@playwright/test` and a `test` script. This file has no file dependencies and is the root of the phase.
- Architecture: E2E harness file list; SPEC Section 13 directory layout.
- Interfaces: `npm run test` invokes `npx playwright test --project=chromium`.
- Depends on: `<none>`
- Consumed by: `finally/test/playwright.config.ts`, `finally/test/docker-compose.test.yml`, `finally/test/e2e.spec.ts`.
- Acceptance:
  - Declares `@playwright/test` as a devDependency.
  - Scripts include a chromium test runner entry.
  - `npm install --ignore-scripts` succeeds without a lockfile assumption.
- Verify: `cd finally/test && npm install --ignore-scripts && npx playwright test --list`

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration per SPEC Section 13.
- Architecture: E2E harness; SPEC Section 13 configuration block.
- Interfaces: exports a default `PlaywrightTestConfig`.
- Depends on: `finally/test/package.json`
- Consumed by: `finally/test/e2e.spec.ts`, `finally/test/docker-compose.test.yml`.
- Acceptance:
  - `baseURL` is `process.env.BASE_URL || 'http://localhost:8010'`.
  - `timeout` is 30s per test; `expect` timeout is 60s; `retries` is 1.
  - One project named `chromium` using `devices['Desktop Chrome']`.
  - Reporter is `[['html', { open: 'never' }], ['list']]`.
  - `webServer` starts `cd ../backend && uv run uvicorn app.main:app --port 8010` with url `http://127.0.0.1:8010/api/health` and `reuseExistingServer: !process.env.CI`.
- Verify: `cd finally/test && npx playwright test --list`

### te-9o3: finally/test/docker-compose.test.yml
- Scope: harness compose file with app and playwright services.
- Architecture: Docker & Deployment; E2E / integration testing; SPEC Section 12 harness contract.
- Interfaces: app service on port 8010; playwright service with `BASE_URL=http://app:8010`.
- Depends on: `finally/test/package.json`, `finally/test/playwright.config.ts`, `finally/Dockerfile` (owned by project-foundation-support, not this phase).
- Consumed by: CI and the operator's Docker test run.
- Acceptance:
  - `app.build.context` is `..` so the real project Dockerfile is used.
  - app sets `LLM_MOCK=true` and healthcheck `curl -f http://localhost:8010/api/health`.
  - playwright mounts `..:/app` and runs `cd /app/test && npm install && npx playwright test --project=chromium`.
- Verify: `cd finally && docker compose -f test/docker-compose.test.yml config`

### te-7by: finally/test/e2e.spec.ts
- Scope: Playwright E2E scenarios per SPEC Section 13, using semantic locators (`getByRole`, `getByText`, `getByTestId`).
- Architecture: E2E / integration testing; Playwright E2E per SPEC Section 13.
- Interfaces: test cases only; uses defaults from `finally/test/playwright.config.ts`.
- Depends on: `finally/test/playwright.config.ts`
- Consumed by: testing gate (`npx playwright test --project=chromium`).
- Acceptance:
  - Fresh load: `getByRole('heading', { level: 1, name: 'FinAlly' })`, `getByText('$10,000')`, and all ten ticker symbols visible.
  - Price stream: at least one ticker price text changes within 5s, matching `$[\d,.]+`.
  - Connection status: `getByTestId('connection-status')` visible.
  - Interaction: Buy 5 AAPL via `getByTestId('trading-panel')` reduces cash and adds an AAPL row to `getByTestId('positions-table')`.
  - Sell: selling shares increases cash and reduces the position.
  - Watchlist: add PYPL and remove NFLX; DOM reflects both changes.
  - Chat: send a message in `getByLabel('Chat message')`; a non-empty assistant bubble appears with no raw `{...}` JSON. A trade via chat shows `✓ Trade Fill: BUY 5 AAPL`.
  - Portfolio: `getByTestId('portfolio-heatmap')` and `getByTestId('pnl-chart')` render.
  - SSE: reconnection returns the connection status to green after a restart.
  - Each test asserts real content, never status codes alone.
- Verify: `cd finally/test && npm install --ignore-scripts && npx playwright test --project=chromium`

### te-2iz: finally/backend/tests/test_api.py
- Scope: full API contract tests across all canonical routes and GET / real dashboard content.
- Architecture: Unit tests list (`test_api.py`); HTTP + entrypoint integration section (SPEC Section 8 routes verbatim).
- Interfaces: uses `create_app(...)` from `finally/backend/app/main.py`; asserts response shapes from `finally/backend/app/api/schemas.py`.
- Depends on: `finally/backend/app/main.py`, `finally/backend/app/api/schemas.py`, `finally/frontend/out/index.html` (built export).
- Consumed by: `finally/test/e2e.spec.ts` (shared contract).
- Acceptance:
  - GET /api/health returns success and identifies the service as up.
  - GET / returns the real dashboard HTML with the `FinAlly` heading, all ten tickers (AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX), and the `$10,000` cash figure. A placeholder or 503 fails the test.
  - GET /api/watchlist returns the ten default tickers with latest prices.
  - POST /api/watchlist with `{ticker}` adds a ticker; a duplicate is rejected; DELETE /api/watchlist/{ticker} removes it.
  - GET /api/portfolio returns cash, positions, total value, and unrealized P&L with the seeded $10,000 cash.
  - POST /api/portfolio/trade with `{ticker, quantity, side}` changes cash and positions; an insufficient-cash buy and an oversell are rejected with an error body.
  - GET /api/portfolio/history returns snapshot rows with `total_value` and `recorded_at`.
  - POST /api/chat with `LLM_MOCK=true` returns a JSON body with a non-empty reply and no raw JSON brackets.
  - GET /api/stream/prices responds with `text/event-stream`.
- Verify: `cd finally/backend && uv run pytest tests/test_api.py -q`

### te-5n9: finally/planning/PLAN.md
- Scope: project planning documentation for agents, including this phase's bead map and the test strategy.
- Architecture: Planning documentation for testing-release; Module / bead ownership.
- Interfaces: documentation only; no code exports.
- Depends on: `<none>` (documents the other files; does not import them)
- Consumed by: all agents as the shared contract.
- Acceptance:
  - Lists the nine canonical phase IDs and the eight user-facing phases.
  - Documents the mandatory verification command and the rule that `--list` is not execution proof.
  - Documents the content assertion rule and the browser interaction rule.
  - Records the env precedence rule and the mock LLM mode.
- Verify: `test -f finally/planning/PLAN.md && wc -c finally/planning/PLAN.md`

# Implementation plan — testing-release

## Scope

Active phase `testing-release`: backend pytest API suite, Playwright E2E harness
(package, config, compose, spec), and the planning document. Bead IDs below come
from `bd list --limit=0 ` in this session. Routes and scenarios are taken from SPEC Section 8
and Section 13 and architecture.md.

## Bead map

### te-rak: finally/test/package.json
- Scope: Playwright test package manifest.
- Architecture: architecture.md testing-release phase, Playwright E2E per SPEC Section 13.
- Acceptance: declares `@playwright/test` as a devDependency at `^1.47.0`.
- Acceptance: `test` and `test:e2e` scripts run `npx playwright test --project=chromium`.
- Acceptance: `npm install --ignore-scripts` succeeds inside `finally/test`.
- Verify: cd finally/test && npm install --ignore-scripts

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration for the E2E suite.
- Architecture: testDir points at the e2e spec directory; baseURL reads `BASE_URL`.
- Depends on: te-rak (finally/test/package.json).
- Acceptance: `baseURL` reads `process.env.BASE_URL`, defaulting to `http://localhost:8010`.
- Acceptance: `npx playwright test --list` loads the config without error.
- Verify: cd finally/test && npx playwright test --list

### te-9o3: finally/test/docker-compose.test.yml
- Scope: compose harness with app and playwright services.
- Architecture: app healthcheck targets `/api/health` on port 8010.
- Depends on: te-eku (finally/test/playwright.config.ts).
- Acceptance: app healthcheck targets `/api/health`.
- Acceptance: playwright waits for app health and receives `BASE_URL=http://app:8010`.
- Verify: docker compose -f finally/test/docker-compose.test.yml config

### te-7by: finally/test/e2e.spec.ts
- Scope: one E2E case per SPEC Section 13 mandatory scenario.
- Architecture: Section 13 scenarios; selectors via getByRole, getByText, getByTestId only.
- Depends on: te-eku (finally/test/playwright.config.ts), te-9o3 (finally/test/docker-compose.test.yml).
- Acceptance: fresh load asserts `getByText('FinAlly')`, `getByText('$10,000')`, and title contains "FinAlly".
- Acceptance: default watchlist asserts all ten tickers AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX visible.
- Acceptance: connection status asserts `getByTestId('connection-status')` visible.
- Acceptance: component composition asserts heading FinAlly, `cash-balance`, Watchlist heading, `Market overview`, price chart, `portfolio-summary`, `positions-table`, `trading-panel`, and `Chat assistant`.
- Acceptance: browser interaction — add ticker by typing PYPL and clicking add, then assert `getByText('PYPL')` appears (state change).
- Acceptance: browser interaction — remove AAPL, then assert `getByText('AAPL')` disappears and list has nine items.
- Acceptance: buy and sell via trade bar assert cash decreases and position appears or updates in the DOM.
- Acceptance: heatmap `portfolio-heatmap` and P&L `pnl-chart` assert rendered SVG/canvas content.
- Acceptance: mocked chat (LLM_MOCK) sends a message and asserts the assistant bubble and `✓ Trade Fill` badge appear.
- Acceptance: SSE reconnection asserts status returns to green after restart.
- Acceptance: `npx playwright test --list` enumerates the cases without error.
- Verify: cd finally/test && npx playwright test --list

### te-2iz: finally/backend/tests/test_api.py
- Scope: full API contract across SPEC Section 8 routes.
- Architecture: GET / returns real dashboard content; 503 diagnostic if export is missing (no placeholder page).
- Acceptance: GET `/api/health` returns success.
- Acceptance: GET `/api/portfolio` and GET `/api/portfolio/history` return shapes with cash and positions.
- Acceptance: POST `/api/portfolio/trade` with `{ticker, quantity, side}` changes cash and positions.
- Acceptance: GET `/api/watchlist`, POST `/api/watchlist` with `{ticker}`, and DELETE `/api/watchlist/{ticker}` cover add, duplicate, and removal.
- Acceptance: POST `/api/chat` returns message plus executed actions with LLM_MOCK=true.
- Acceptance: GET `/` asserts real dashboard content (FinAlly heading, ten tickers, $10,000 cash) and never a placeholder string.
- Acceptance: missing export returns 503 with a diagnostic body.
- Acceptance: `uv run pytest tests/test_api.py -q` from `finally/backend` passes.
- Verify: cd finally/backend && uv run pytest tests/test_api.py -q

### te-5n9: finally/planning/PLAN.md
- Scope: planning document for support artifacts and verification commands.
- Acceptance: lists the verification commands that exist on disk for this phase.
- Acceptance: documents the Section 13 mandatory E2E coverage and the browser-interaction rule.
- Verify: test -f finally/planning/PLAN.md

## Execution order

1. te-rak (package.json)
2. te-eku (playwright.config.ts)
3. te-9o3 (docker-compose.test.yml) and te-7by (e2e.spec.ts)
4. te-2iz (test_api.py) and te-5n9 (PLAN.md), independent of the e2e chain

## Future considerations

- Sparkline and price-flash CSS transitions are covered by SPEC Section 13 but are not mandatory beads in this phase.

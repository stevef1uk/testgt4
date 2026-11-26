# Implementation plan: testing-release phase

## Scope

This plan covers only the testing-release phase. Its six required files are the backend API test module, the Playwright harness (package manifest, config, compose file, E2E spec), and the planning document. Files owned by earlier phases (app wiring, Dockerfile, routers) are not implemented here. Missing earlier-phase pieces are deferred to those phases, not blocked on in this plan.

## Bead map

### te-2iz: finally/backend/tests/test_api.py
- Scope: pytest API tests for the REST surface under /api/* (portfolio, watchlist, trades) and the GET / dashboard response.
- Architecture: backend tests section of architecture.md; single origin on port 8010, no CORS.
- Interfaces: pytest test functions using a TestClient against the FastAPI app.
- Depends on: <none> in this phase (router registration is owned by the project-foundation phase).
- Consumed by: finally/test/e2e.spec.ts (behavioural parity only, no import).
- Acceptance: GET / returns the dashboard HTML with the FinAlly heading and the ten default tickers.
- Acceptance: GET /api/watchlist returns the ten default tickers for user "default".
- Acceptance: POST /api/watchlist returns 201 for a new ticker and 409 for a duplicate.
- Acceptance: DELETE of a missing watchlist ticker returns 404.
- Acceptance: GET /api/portfolio starts with $10,000 cash.
- Acceptance: a market buy fills at the cached price and debits cash (201).
- Acceptance: selling without a position returns 400; buying beyond cash returns 400.
- Acceptance: when the export is missing, the dashboard route returns 503 with a diagnostic body.
- Verify: cd finally/backend && uv run pytest tests/test_api.py -q

### te-rak: finally/test/package.json
- Scope: Node package manifest for the Playwright E2E harness.
- Architecture: test harness section of architecture.md.
- Interfaces: npm scripts "test" and "test:e2e" running playwright test on chromium.
- Depends on: <none>
- Consumed by: finally/test/playwright.config.ts, finally/test/e2e.spec.ts
- Acceptance: declares @playwright/test as a dev dependency.
- Acceptance: installs with npm install --ignore-scripts and lists the suite without errors.
- Verify: cd finally/test && npm install --ignore-scripts && npx playwright test --list

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration targeting the single-origin app on port 8010.
- Architecture: test harness section of architecture.md.
- Interfaces: default export of the Playwright config object.
- Depends on: finally/test/package.json
- Consumed by: finally/test/e2e.spec.ts
- Acceptance: baseURL points at http://localhost:8010; the chromium project is defined.
- Acceptance: the test directory resolves to finally/test.
- Verify: cd finally/test && npx playwright test --list

### te-9o3: finally/test/docker-compose.test.yml
- Scope: Compose file that brings up the containerised app and the Playwright runner for E2E runs.
- Architecture: deployment section of architecture.md.
- Interfaces: app service exposing port 8010 with a health check.
- Depends on: <none> in this phase (Dockerfile build is owned by a later phase).
- Consumed by: finally/test/e2e.spec.ts
- Acceptance: one app container, one port, one origin; no CORS configuration.
- Acceptance: the playwright service waits for app health before running tests.
- Verify: cd finally/test && docker compose -f docker-compose.test.yml config

### te-7by: finally/test/e2e.spec.ts
- Scope: End-to-end browser tests for dashboard load, trading, watchlist, and chat.
- Architecture: test harness section of architecture.md.
- Interfaces: Playwright test specs using the config from playwright.config.ts.
- Depends on: finally/test/playwright.config.ts, finally/test/docker-compose.test.yml
- Consumed by: <none>
- Acceptance: the dashboard shows the FinAlly heading, ten tickers with prices, and $10,000 cash.
- Acceptance: a market buy updates cash and positions.
- Acceptance: chat output contains no raw JSON.
- Verify: cd finally/test && npx playwright test

### te-5n9: finally/planning/PLAN.md
- Scope: Planning document for the layout under finally/planning/.
- Architecture: planned file layout section of architecture.md.
- Interfaces: none (documentation).
- Depends on: <none>
- Consumed by: <none>
- Acceptance: file exists and lists the planned layout paths under the finally/ prefix.
- Verify: test -s finally/planning/PLAN.md

## Future considerations

- Router registration in finally/backend/app/api/__init__.py belongs to the project-foundation phase; the te-2iz failures are deferred there.
- Compose build of the app image depends on the Dockerfile in a later phase; compose validation here checks only the file itself.

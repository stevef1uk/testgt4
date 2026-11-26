# Implementation plan — testing-release phase

## Bead map

### te-2iz: finally/backend/tests/test_api.py
- Scope: Backend API tests for the REST surface under /api/* (portfolio, watchlist, chat) and GET / behaviour.
- Architecture: backend tests section of architecture.md; single origin on port 8010, no CORS.
- Interfaces: test client against the FastAPI app in finally/backend/app/main.py.
- Depends on: <none>
- Consumed by: finally/test/e2e.spec.ts
- Acceptance: GET / returns the dashboard with the FinAlly heading, ten default tickers, and $10,000 cash; returns 503 with a diagnostic body when the export is missing.
- Acceptance: trade and watchlist endpoints respect single user "default" and market-order instant fill at the cached price.
- Verify: cd finally/backend && uv run pytest tests/test_api.py -q

### te-rak: finally/test/package.json
- Scope: Node package manifest for the Playwright E2E harness.
- Architecture: test harness section of architecture.md.
- Interfaces: npm scripts for test execution (playwright test).
- Depends on: <none>
- Consumed by: finally/test/playwright.config.ts, finally/test/e2e.spec.ts
- Acceptance: installs with npm install --ignore-scripts and lists the Playwright test suite.
- Verify: cd finally/test && npm install --ignore-scripts && npx playwright test --list

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration targeting the single-origin app on port 8010.
- Architecture: test harness section of architecture.md.
- Interfaces: default export of the Playwright config object.
- Depends on: finally/test/package.json
- Consumed by: finally/test/e2e.spec.ts
- Acceptance: baseURL points at http://localhost:8010; the test directory resolves to finally/test.
- Verify: cd finally/test && npx playwright test --list

### te-9o3: finally/test/docker-compose.test.yml
- Scope: Compose file that brings up the containerised app for E2E runs.
- Architecture: deployment section of architecture.md.
- Interfaces: single app service exposing port 8010.
- Depends on: finally/Dockerfile
- Consumed by: finally/test/e2e.spec.ts
- Acceptance: one container, one port, one origin; no CORS configuration.
- Verify: cd finally/test && docker compose -f docker-compose.test.yml config

### te-7by: finally/test/e2e.spec.ts
- Scope: End-to-end browser tests for dashboard load, trading, watchlist, and chat.
- Architecture: test harness section of architecture.md.
- Interfaces: Playwright test specs.
- Depends on: finally/test/playwright.config.ts, finally/test/docker-compose.test.yml
- Consumed by: <none>
- Acceptance: dashboard shows FinAlly heading, ten tickers with prices, and $10,000 cash.
- Acceptance: a market buy updates cash and positions; chat output contains no raw JSON.
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
- Items not required by SPEC for this phase are deferred to their owning phases.

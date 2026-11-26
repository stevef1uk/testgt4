# Implementation plan

Delivery phase: testing-release (Phase 8 — Testing & Release).
Scope: six implement beads for the `required_files` of this phase only. Later phases are not planned here.

## Bead map

### te-2iz: finally/backend/tests/test_api.py
- Scope: full API contract pytest module across all canonical routes, plus GET / real-dashboard assertions.
- Architecture: Unit tests section (test_api.py) and HTTP + entrypoint integration section (SPEC Section 8 routes verbatim).
- Interfaces: consumes `create_app(...) -> FastAPI` from finally/backend/app/main.py; exercises GET /api/health, GET /api/watchlist, GET /api/portfolio, POST /api/portfolio/trade, GET /api/portfolio/history, POST /api/chat, GET / (static export).
- Depends on: finally/backend/app/main.py, finally/backend/app/api/__init__.py (earlier phases).
- Consumed by: finally/test/e2e.spec.ts (same route contract, asserted through the browser).
- Acceptance: GET / returns HTML containing the FinAlly heading, all ten default tickers (AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX) and the $10,000 cash figure; no placeholder text such as "Coming soon"; /api/health returns success; watchlist and portfolio routes return the documented shapes with real values, not status codes alone.
- Verify: (cd finally/backend && uv run pytest tests/test_api.py -q)

### te-rak: finally/test/package.json
- Scope: Playwright test project manifest with @playwright/test and the chromium run script.
- Architecture: E2E harness layout (finally/test/) and Section 13 test infrastructure.
- Interfaces: npm scripts `test` and `test:e2e` running `npx playwright test --project=chromium`.
- Depends on: none within this phase.
- Consumed by: finally/test/playwright.config.ts, finally/test/docker-compose.test.yml (playwright service install step).
- Acceptance: manifest parses as JSON; devDependencies pin @playwright/test; install uses `npm install --ignore-scripts`.
- Verify: (cd finally/test && npm install --ignore-scripts && npx playwright test --list)

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration for the chromium project.
- Architecture: Section 13 Playwright configuration (baseURL from BASE_URL, 30s test timeout, retries 1, html reporter with open never, webServer disabled).
- Interfaces: default export of a Playwright config with projects `[{ name: 'chromium' }]`.
- Depends on: finally/test/package.json.
- Consumed by: finally/test/e2e.spec.ts, finally/test/docker-compose.test.yml.
- Acceptance: baseURL falls back to http://localhost:8010; the chromium project uses Desktop Chrome; `npx playwright test --list` discovers tests.
- Verify: (cd finally/test && npx playwright test --list)

### te-9o3: finally/test/docker-compose.test.yml
- Scope: compose harness with the app container (build context `..`) and a playwright container.
- Architecture: Section 12 harness contract. The app healthcheck hits `curl -f http://localhost:8010/api/health`; LLM_MOCK=true; BASE_URL=http://app:8010; playwright mounts the project root and runs `npm install` (not `npm ci`).
- Interfaces: service `app` on port 8010; service `playwright` depending on `app` being healthy.
- Depends on: finally/Dockerfile (project-foundation-support), finally/test/package.json, finally/test/playwright.config.ts.
- Consumed by: CI runs of finally/test/e2e.spec.ts.
- Acceptance: `docker compose -f finally/test/docker-compose.test.yml config` validates; app healthcheck path and BASE_URL match the SPEC.
- Verify: (cd finally/test && docker compose -f docker-compose.test.yml config)

### te-7by: finally/test/e2e.spec.ts
- Scope: end-to-end scenarios driven through the browser with real content assertions.
- Architecture: SPEC Section 13 mandatory scenarios, reduced to one file for this phase.
- Interfaces: Playwright tests using getByRole, getByText and getByTestId only.
- Depends on: finally/test/playwright.config.ts, finally/test/package.json; the running app from finally/test/docker-compose.test.yml.
- Consumed by: testing-release gate (`npx playwright test --list`).
- Acceptance: fresh load shows FinAlly heading, ten tickers and $10,000; one real interaction (Buy 5 AAPL or Add ticker) followed by a DOM state-change assertion; chat Send shows a non-empty assistant reply with no raw JSON braces.
- Verify: (cd finally/test && npm install --ignore-scripts && npx playwright test --list)

### te-5n9: finally/planning/PLAN.md
- Scope: project planning document for agents covering this plan's contract and delivery phases.
- Architecture: Planned file layout (`finally/planning/PLAN.md`) and Section 14 design contract.
- Interfaces: none (documentation).
- Depends on: none.
- Consumed by: agents reading the shared contract.
- Acceptance: file exists with a Scope, Acceptance and Verification section; verification commands match the phase gate.
- Verify: test -f finally/planning/PLAN.md

## Future considerations
- Remaining SPEC Section 13 scenarios beyond the mandatory happy path are deferred to later test passes.

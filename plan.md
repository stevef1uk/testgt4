# Implementation plan — testing-release

## Scope

Phase `testing-release` (SPEC Section 14.3). Layout root is `finally/`. This plan
covers exactly six implement beads, one per path in the phase `required_files`:

- `finally/backend/tests/test_api.py` (bead te-2iz)
- `finally/test/package.json` (bead te-rak)
- `finally/test/playwright.config.ts` (bead te-eku)
- `finally/test/docker-compose.test.yml` (bead te-9o3)
- `finally/test/e2e.spec.ts` (bead te-7by)
- `finally/planning/PLAN.md` (bead te-5n9)

Files owned by earlier or later phases are out of scope for this plan.

## Bead map

### te-2iz: finally/backend/tests/test_api.py
- Scope: pytest API contract tests covering every route in SPEC Section 8.
- Architecture: Unit tests section, entry `finally/backend/tests/test_api.py`.
- Interfaces: none exported; test file only.
- Depends on: <none>
- Consumed by: <none>
- Acceptance:
  - Each Section 8 route (`/api/stream/prices`, `/api/portfolio`, `/api/portfolio/trade`, `/api/portfolio/history`, `/api/watchlist`, `/api/chat`, `/api/health`) has at least one assertion on status code and response shape.
  - `GET /` asserts real dashboard content: the FinAlly heading, the ten default tickers (AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX), and the `$10,000` cash figure.
  - No test asserts placeholder text such as "Coming soon" or a bare "Finally" match.
  - Tests run with `LLM_MOCK=true`.
- Verify: (cd finally/backend && uv run pytest tests/test_api.py -q)

### te-rak: finally/test/package.json
- Scope: npm manifest for the Playwright suite with `@playwright/test` as the only devDependency.
- Architecture: E2E harness entry `finally/test/package.json`.
- Interfaces: npm scripts `test` and `test:e2e`, both running the chromium project.
- Depends on: <none>
- Consumed by: finally/test/playwright.config.ts, finally/test/e2e.spec.ts, finally/test/docker-compose.test.yml
- Acceptance:
  - Manifest parses as valid JSON with name, private flag, and both scripts.
  - `@playwright/test` is pinned to the ^1.47.0 range.
- Verify: (cd finally/test && npm install --ignore-scripts && npx playwright test --list)

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration for the chromium project against the app container.
- Architecture: SPEC Section 13 Playwright configuration.
- Interfaces: default-exported Playwright config; `baseURL` read from `process.env.BASE_URL`.
- Depends on: finally/test/package.json
- Consumed by: finally/test/e2e.spec.ts, finally/test/docker-compose.test.yml
- Acceptance:
  - Defines a single chromium project using Desktop Chrome.
  - `baseURL` falls back to `http://localhost:8010` when `BASE_URL` is unset.
  - Timeout is 30s per test and retries is 1.
- Verify: (cd finally/test && npx playwright test --list)

### te-9o3: finally/test/docker-compose.test.yml
- Scope: compose stack with an `app` service and a `playwright` service.
- Architecture: Docker & Deployment and E2E sections; harness contract in SPEC Section 12.
- Interfaces: service `app` on port 8010 with health check; service `playwright` gated on app health.
- Depends on: finally/test/package.json, finally/test/playwright.config.ts
- Consumed by: finally/test/e2e.spec.ts (run target)
- Acceptance:
  - `app.build.context` is `..` so the real Dockerfile is used.
  - App health check runs `curl -f http://localhost:8010/api/health`.
  - `playwright` sets `BASE_URL=http://app:8010` and `LLM_MOCK=true`.
  - `playwright` waits on `depends_on` with `condition: service_healthy`.
- Verify: (cd finally/test && docker compose -f docker-compose.test.yml config)

### te-7by: finally/test/e2e.spec.ts
- Scope: browser tests for the dashboard and trading flows in SPEC Section 13.
- Architecture: SPEC Section 13 mandatory coverage table.
- Interfaces: Playwright spec file; no exports.
- Depends on: finally/test/playwright.config.ts, finally/test/package.json
- Consumed by: <none>
- Acceptance:
  - Dashboard test asserts ten tickers, `$10,000` cash, and a live price.
  - At least one test performs a real Buy or Send interaction and asserts the state change (cash decreases and a position appears, or an assistant reply appears).
  - Selectors use `getByRole`, `getByText`, or `getByTestId` only.
  - No test asserts placeholder text.
- Verify: (cd finally/test && npx playwright test --list)

### te-5n9: finally/planning/PLAN.md
- Scope: planning support document for the foundation support artifacts and schema defaults.
- Architecture: planning documentation entry `finally/planning/PLAN.md`.
- Interfaces: documentation only.
- Depends on: <none>
- Consumed by: <none>
- Acceptance:
  - Lists the foundation support verification files.
  - States SPEC defaults: ten-ticker watchlist and `$10,000` cash for user "default".
- Verify: test -f finally/planning/PLAN.md

## Verification gate

Phase gate command (single quoted scalar from architecture.md):
(cd finally/backend && uv run pytest tests/test_api.py -q) && (cd finally/test && npm install --ignore-scripts && npx playwright test --list)

## Future considerations

- None in this phase. Items outside the six required paths are deferred to their owning phases.

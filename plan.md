# Implementation plan

Active phase: testing-release (Testing & Release). Scope is limited to the six
paths in this phase's required_files. Other phases' files are deferred and get
their own beads when those phases become active.

Phase verification (qa_verify_command):
`(cd finally/backend && uv run pytest tests/test_api.py -q) && (cd finally/test && npm install --ignore-scripts && npx playwright test --list)`

## Revision note (QA rework)

te-eku failed its auto-verify because `npx playwright test --list` reports
"No tests found" until finally/test/e2e.spec.ts (te-7by) exists. The list gate
is therefore owned by te-7by, not te-eku. te-eku verifies only its own artifact
(config present, non-empty, loadable as TypeScript). te-7by runs the full phase
gate after it lands. Queue order is unchanged: te-rak, te-eku, te-7by, te-9o3.

## Bead map

### te-rak: finally/test/package.json
- Scope: npm manifest for the Playwright E2E harness under finally/test/.
- Architecture: E2E harness section lists finally/test/package.json.
- Interfaces: devDependency `@playwright/test`; script `test` runs `npx playwright test --project=chromium`.
- Depends on: <none>
- Consumed by: te-eku (playwright.config.ts), te-7by (e2e.spec.ts), te-9o3 (docker-compose.test.yml)
- Acceptance:
  - Valid JSON that `npm install --ignore-scripts` accepts.
  - Declares @playwright/test so the Playwright CLI resolves.
- Verify: `test -s finally/test/package.json`

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration for chromium, baseURL from BASE_URL.
- Architecture: E2E harness section lists finally/test/playwright.config.ts.
- Interfaces: default export config with project `chromium`; testDir is finally/test.
- Depends on: te-rak (package.json)
- Consumed by: te-9o3 (compose passes --config=test/playwright.config.ts), te-7by
- Acceptance:
  - File exists and is non-empty.
  - baseURL honours BASE_URL with default http://localhost:8010.
  - Does not require e2e.spec.ts to exist; test discovery is verified by te-7by.
- Verify: `test -s finally/test/playwright.config.ts`

### te-7by: finally/test/e2e.spec.ts
- Scope: browser E2E flows covering SPEC section 8 user journeys against the running app.
- Architecture: E2E harness section lists finally/test/e2e.spec.ts.
- Interfaces: Playwright test file importing @playwright/test; uses BASE_URL.
- Depends on: te-rak, te-eku
- Consumed by: te-9o3 (compose runs it inside the playwright service)
- Acceptance:
  - Asserts GET / shows the FinAlly heading, ten default tickers, and $10,000 cash.
  - Covers a market buy and sell round trip and watchlist add/remove, per SPEC.
  - Lists cleanly with `npx playwright test --list` (this makes the phase list gate pass).
- Verify: `(cd finally/test && npm install --ignore-scripts && npx playwright test --list)`

### te-9o3: finally/test/docker-compose.test.yml
- Scope: compose harness that builds the app image and runs Playwright against it on the internal network.
- Architecture: E2E harness section lists finally/test/docker-compose.test.yml.
- Interfaces: service `app` (port 8010, healthcheck on /api/health); service `playwright` with BASE_URL=http://app:8010.
- Depends on: te-rak, te-eku, te-7by
- Consumed by: release gate (docker compose test run)
- Acceptance:
  - `docker compose -f test/docker-compose.test.yml config` validates.
  - Playwright service waits for app health before running tests.
- Verify: `cd finally && docker compose -f test/docker-compose.test.yml config`

### te-5n9: finally/planning/PLAN.md
- Scope: planning artifact retained with the delivered project.
- Architecture: Root and deployment section lists finally/planning/PLAN.md.
- Interfaces: none (documentation).
- Depends on: <none>
- Consumed by: <none>
- Acceptance:
  - File exists and is non-empty under finally/planning/.
  - Content is consistent with the phase bead map above.
- Verify: `test -s finally/planning/PLAN.md`

### te-2iz: finally/backend/tests/test_api.py
- Scope: backend API tests for the SPEC section 8 endpoints, run by the phase gate.
- Architecture: Backend tests list finally/backend/tests/test_api.py.
- Interfaces: pytest module exercising the FastAPI app via the test client.
- Depends on: finished backend app modules from earlier phases (app/main.py, app/api routers)
- Consumed by: phase qa_verify_command
- Acceptance:
  - Asserts functional behaviour from SPEC: health, portfolio, watchlist, trade endpoints.
  - No placeholder `assert True` tests; each case maps to a SPEC requirement.
  - `uv run pytest tests/test_api.py -q` passes in finally/backend.
- Verify: `(cd finally/backend && uv run pytest tests/test_api.py -q)`

## Dependency order

1. te-rak (package.json)
2. te-eku (playwright.config.ts, artifact check only)
3. te-7by (e2e.spec.ts, enables the list gate)
4. te-9o3 (docker-compose.test.yml)
5. te-5n9 (PLAN.md, independent)
6. te-2iz (test_api.py, depends on earlier backend phases)

## Future considerations

Frontend and backend source files from earlier phases are verified by their own phase gates and are not re-planned here.

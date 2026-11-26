# Implementation plan: testing-release

Active phase: testing-release (Testing and Release). This plan covers only the six
required_files for this phase. Backend, frontend, and entrypoint files belong to
other phases and are deferred.

Phase verification (polecat must run this green before completing any bead):
cd finally/backend && uv run pytest tests/test_api.py -q
cd finally/test && npm install --ignore-scripts && npx playwright test --list

## Bead map

### te-rak: finally/test/package.json
- Scope: npm manifest for the Playwright end-to-end suite.
- Architecture: testing-release section of architecture.md (e2e harness).
- Interfaces: npm scripts test and test:e2e, both running the chromium project.
- Depends on: <none>
- Consumed by: finally/test/playwright.config.ts, finally/test/e2e.spec.ts
- Acceptance: declares @playwright/test as a devDependency at ^1.47.0.
- Acceptance: npm install --ignore-scripts succeeds inside finally/test.
- Verify: cd finally/test && npm install --ignore-scripts

### te-eku: finally/test/playwright.config.ts
- Scope: Playwright configuration with a chromium project and BASE_URL support.
- Architecture: testing-release section of architecture.md (e2e harness).
- Interfaces: default-exported Playwright config with a chromium project.
- Depends on: finally/test/package.json
- Consumed by: finally/test/e2e.spec.ts, finally/test/docker-compose.test.yml
- Acceptance: testDir points at the e2e spec directory; baseURL reads BASE_URL.
- Acceptance: npx playwright test --list loads the config without error.
- Verify: cd finally/test && npx playwright test --list

### te-9o3: finally/test/docker-compose.test.yml
- Scope: compose harness running the app service and the playwright service.
- Architecture: testing-release section of architecture.md (compose harness).
- Interfaces: services app (port 8010) and playwright.
- Depends on: finally/test/playwright.config.ts
- Consumed by: <none>
- Acceptance: app healthcheck targets /api/health.
- Acceptance: playwright waits for app health and receives BASE_URL=http://app:8010.
- Verify: docker compose -f finally/test/docker-compose.test.yml config

### te-7by: finally/test/e2e.spec.ts
- Scope: end-to-end spec covering the SPEC user flows for this phase.
- Architecture: testing-release section of architecture.md (e2e tests).
- Interfaces: Playwright test cases only; no exported production symbols.
- Depends on: finally/test/package.json, finally/test/playwright.config.ts
- Consumed by: <none>
- Acceptance: one test per SPEC user flow, asserting visible UI state.
- Acceptance: npx playwright test --list enumerates the cases without error.
- Verify: cd finally/test && npx playwright test --list

### te-2iz: finally/backend/tests/test_api.py
- Scope: API test module for the backend endpoints SPEC defines for this phase.
- Architecture: testing-release section of architecture.md (backend tests).
- Interfaces: test functions only; no exported production symbols.
- Depends on: <none>
- Consumed by: <none>
- Acceptance: each test maps to a SPEC functional requirement, one assertion group per endpoint.
- Acceptance: uv run pytest tests/test_api.py -q from finally/backend passes.
- Verify: cd finally/backend && uv run pytest tests/test_api.py -q

### te-5n9: finally/planning/PLAN.md
- Scope: project foundation support plan referenced by the testing-release phase.
- Architecture: testing-release section of architecture.md (planning artifacts).
- Interfaces: none (documentation artifact).
- Depends on: <none>
- Consumed by: <none>
- Acceptance: lists the verification commands that exist on disk for this phase.
- Verify: test -f finally/planning/PLAN.md

## Ordering

1. te-rak (package.json)
2. te-eku (playwright.config.ts)
3. te-9o3 (docker-compose.test.yml) and te-7by (e2e.spec.ts)
4. te-2iz (test_api.py) and te-5n9 (PLAN.md), independent of the e2e chain

## Future considerations

- Watchlist and portfolio routes are owned by later phases and are not part of
  this phase's acceptance.

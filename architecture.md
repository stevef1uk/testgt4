# Architecture for testgt4

## Overview
This design implements the SPEC as a Next.js/TypeScript static frontend served by a FastAPI/Python backend, with uv-managed dependencies, persistent SQLite, SSE market prices, portfolio/trading and AI chat, and the complete Playwright coverage specified in Section 13. The layout_root is finally. The layout root is `finally/`; every deliverable is rooted there. Configuration comes from the environment, the application entrypoint owns startup, and the API layer exposes the routes and schemas named by the SPEC. Docker and host scripts provide reproducible startup without changing the application contract.

The backend is organized around `finally/backend/app/main.py` as the composition root and `finally/backend/app/api/__init__.py` plus `finally/backend/app/api/schemas.py` as the API boundary. The frontend is built from `finally/frontend/`; browser tests live in `finally/test/`. SQLite schema and repository code live in `finally/backend/db/`, while the persistent database is mounted at /app/db in the container. SPEC Section 7's six tables, ten seed tickers and 10,000-dollar cash seed are required, not optional.

## Planned file layout
Every file listed below is an owned deliverable; no directory placeholder substitutes for a file.
- `finally/scripts/start_mac.sh`
- `finally/scripts/stop_mac.sh`
- `finally/scripts/start_windows.ps1`
- `finally/scripts/stop_windows.ps1`
- `finally/db/.gitkeep`
- `finally/.env`
- `finally/.gitignore`
- `finally/backend/app/main.py`
- `finally/backend/app/api/__init__.py`
- `finally/backend/app/api/schemas.py`
- `finally/test/playwright.config.ts`
- `finally/test/e2e.spec.ts`
- `finally/Dockerfile`
- `finally/docker-compose.yml`
- `finally/test/docker-compose.test.yml`
- `finally/.env.example`
- `finally/.dockerignore`
- `finally/backend/pyproject.toml`
- `finally/backend/uv.lock`
- `finally/backend/app/__init__.py`
- `finally/backend/db/__init__.py`
- `finally/backend/db/schema.py`
- `finally/backend/db/store.py`
- `finally/backend/tests/test_foundation.py`
- `finally/frontend/package.json`
- `finally/frontend/next.config.mjs`
- `finally/frontend/tsconfig.json`
- `finally/frontend/app/layout.tsx`
- `finally/frontend/app/page.tsx`
- `finally/frontend/app/globals.css`
- `finally/frontend/lib/api.ts`
- `finally/frontend/lib/types.ts`
- `finally/backend/app/market/__init__.py`
- `finally/backend/app/market/providers.py`
- `finally/backend/app/market/simulator.py`
- `finally/backend/app/market/massive.py`
- `finally/backend/app/market/cache.py`
- `finally/backend/app/market/stream.py`
- `finally/backend/tests/test_market.py`
- `finally/frontend/lib/usePrices.ts`
- `finally/backend/app/portfolio.py`
- `finally/backend/tests/test_portfolio.py`
- `finally/backend/app/api/watchlist.py`
- `finally/backend/tests/test_watchlist.py`
- `finally/frontend/components/Header.tsx`
- `finally/frontend/components/Watchlist.tsx`
- `finally/frontend/components/PriceChart.tsx`
- `finally/backend/app/api/portfolio.py`
- `finally/backend/tests/test_trading.py`
- `finally/frontend/components/TradeBar.tsx`
- `finally/frontend/components/Positions.tsx`
- `finally/frontend/components/PortfolioSummary.tsx`
- `finally/frontend/components/PortfolioHeatmap.tsx`
- `finally/frontend/components/PnlChart.tsx`
- `finally/backend/app/chat.py`
- `finally/backend/app/api/chat.py`
- `finally/backend/tests/test_chat.py`
- `finally/frontend/components/ChatPanel.tsx`
- `finally/frontend/components/Notifications.tsx`
- `finally/frontend/tests/dashboard.test.tsx`
- `finally/frontend/tests/watchlist.test.tsx`
- `finally/frontend/tests/trading.test.tsx`
- `finally/frontend/tests/chat.test.tsx`
- `finally/frontend/vitest.config.ts`
- `finally/frontend/tests/setup.ts`
- `finally/test/package.json`
- `finally/test/fixtures/base.ts`
- `finally/test/api/helpers.ts`
- `finally/test/pages/dashboard.page.ts`
- `finally/test/pages/watchlist.page.ts`
- `finally/test/pages/trade.page.ts`
- `finally/test/pages/portfolio.page.ts`
- `finally/test/pages/chat.page.ts`
- `finally/test/specs/dashboard.spec.ts`
- `finally/test/specs/watchlist.spec.ts`
- `finally/test/specs/trading.spec.ts`
- `finally/test/specs/portfolio.spec.ts`
- `finally/test/specs/chat.spec.ts`
- `finally/test/specs/sse.spec.ts`
- `finally/test/specs/navigation.spec.ts`
- `finally/test/specs/mvp.spec.ts`
- `finally/README.md`

The scripts are thin operational wrappers and must not duplicate API behavior. The compose files are harness/deployment files, and the Playwright files are test-harness files even though they participate in delivery verification.

## Module / bead ownership
| File | Owns | Must not define |
|---|---|---|
| `finally/backend/app/main.py` | Application factory, startup configuration, dependency wiring, and server entrypoint | Duplicate schema definitions or browser-test logic |
| `finally/backend/app/api/__init__.py` | API router construction and route handlers named by the SPEC | Process startup, compose behavior, or a second application factory |
| `finally/backend/app/api/schemas.py` | Request/response schema declarations and validation helpers | Route registration or persistence side effects |
| `finally/test/playwright.config.ts` | Playwright project, base URL, timeout, and artifact policy | Application routes |
| `finally/test/e2e.spec.ts` | User-visible smoke assertions and API/UI integration checks | Backend implementation |
| `finally/Dockerfile` | Reproducible image build and runtime command | Environment-specific host orchestration |
| `finally/docker-compose.yml` | Local service, ports, environment, and volume wiring | Business logic |
| `finally/test/docker-compose.test.yml` | Isolated test service and test-only overrides | Production deployment settings |
| `finally/scripts/start_mac.sh` | macOS startup invocation | Service implementation |
| `finally/scripts/stop_mac.sh` | macOS shutdown invocation | Data or API logic |
| `finally/scripts/start_windows.ps1` | Windows startup invocation | Service implementation |
| `finally/scripts/stop_windows.ps1` | Windows shutdown invocation | Data or API logic |
| `finally/db/.gitkeep` | Explicit empty database mount directory | Runtime code |
| `finally/.env` | Safe local configuration defaults required by the SPEC | Secrets or generated state |
| `finally/.gitignore` | Exclusions for local state and test artifacts | Source files |

Python exported symbols use normal Python signatures. The entrypoint owns create_app() -> FastAPI (or the framework application type required by the SPEC); the API module owns `router` and its route callables with typed request and response models; schemas owns each SPEC-named Pydantic model with typed fields and defaults. If the SPEC names a different framework spelling, that spelling is authoritative; no additional public symbol is introduced.

## HTTP + entrypoint integration
The implementation must copy the SPEC's HTTP API table verbatim: method, path, request shape, response shape, status code, and error behavior are authoritative. No route is renamed, aliased, or broadened. `finally/backend/app/api/__init__.py` registers those exact routes and imports models from `finally/backend/app/api/schemas.py`; handlers validate input before performing the prescribed operation and return the prescribed status and JSON shape.

`finally/backend/app/main.py` is the sole composition root. It reads the configured host and port, creates the application, includes the API router, and exposes the server entrypoint. Startup proceeds in this order: parse configuration; initialize the application and any SPEC-required state; construct the router dependencies; register routes; then start the configured server. Health, error, content-type, and CORS behavior must follow the SPEC rather than incidental framework defaults. A request must never require the browser test runner to be installed.

## Unit tests
The SPEC's functional requirements are verified by pytest in `finally/backend/tests/`, React Testing Library/Vitest in `finally/frontend/tests/`, and Playwright Page Objects and scenario files under `finally/test/`. The concrete test files are enumerated above and assigned in workflow-profile.json. Tests assert actual behavior and real rendered content, not only imports, successful HTTP statuses, or placeholders. Existing smoke tests must be expanded; their presence alone is not acceptance.

## Integration and testing
The canonical verification command is the full-suite command specified by the workflow profile. The test harness starts the service using `finally/test/docker-compose.test.yml` or the profile's prescribed command, waits for the configured readiness condition, runs Playwright using `finally/test/playwright.config.ts`, and tears down containers afterward. Tests use a stable base URL from configuration and must not depend on a developer's current directory. Failures retain Playwright diagnostics while cleanup remains best effort.

## Docker & Deployment
`finally/Dockerfile` uses a Node 20 frontend stage and Python 3.12/uv runtime stage. The frontend stage builds output: export into /frontend/out; COPY --from=frontend /frontend/out /app/frontend/out preserves SPEC Section 4's static-serving contract. The backend lives at /app/backend and exports create_app() -> FastAPI and app from app.main. uv sync --frozen installs from `finally/backend/pyproject.toml` and `finally/backend/uv.lock`. The container serves port 8000; GET /api/health is the readiness endpoint. `finally/docker-compose.yml` supplies environment values and a persistent /app/db volume. The isolated `finally/test/docker-compose.test.yml` builds from context .., mounts the project root into the browser runner, sets LLM_MOCK=true, and waits for /api/health. No Go module, Go server, or web directory is part of this application.

## E2E / integration testing
`finally/test/playwright.config.ts` sets the base URL from the test environment, uses a deterministic browser project, and records traces/screenshots only on failure. `finally/test/e2e.spec.ts` drives the SPEC's externally visible flow and asserts exact visible/API outcomes, including the required route status and response shape. The test must work against the compose service and a locally started service, so it uses no hard-coded host filesystem paths or private backend imports.

## Delivery phases
Delivery is staged according to the exact delivery phase IDs in the workflow profile. Infrastructure phases create only their assigned scripts, environment, database marker, ignore rules, and harness/deployment files; application behavior remains in the phase assigned by the SPEC. The phase contracts below preserve that separation and map every required file to an owner.

## Requirements

### project-foundation-1
The foundation phase owns the runnable skeleton, not just scripts: the cross-platform scripts, environment/ignore files, Python uv project and lockfile, backend application/router/schema boundaries, idempotent SQLite schema and default seed repository, Next.js package/configuration/layout/page/styles/API types, production Dockerfile and compose, and foundation tests. Use the concrete active-phase file list in workflow-profile.json. GET /api/health must succeed and GET / must serve the built Market Dashboard with real seeded ticker/cash content; no hardcoded fallback HTML. The prior completion marker is invalid because the frontend and dependencies were absent; recover existing files rather than deleting them.

The workflow's phase-size limit splits foundation into two subphases. Part 1 implements backend runtime/seed/health contracts and dependency manifests. Its pytest foundation test must assert canonical API health and idempotent initial state; it must not require the frontend export before part 2 exists. Keep the already-repaired production Docker harness intact; full-container acceptance runs after source prerequisites exist.

### project-foundation-2
Complete the Next.js layout/page/styles and shared API/types listed in the profile, using output: export. Render the actual Market Dashboard with the ten SPEC tickers and 10,000-dollar cash seed. Verify npm run build succeeds and produces the real static export. Do not introduce a Go service or a fallback HTML dashboard.

### core-market-infrastructure
This phase implements the SPEC market-data platform in `finally/backend/app/market/`: interchangeable simulator and Massive providers, environment selection, shared cache, background lifecycle and GET /api/stream/prices. The provider contract is async prices for known tickers; cache snapshots expose ticker, price, previous_price, timestamp, and direction as specified by SPEC. `finally/frontend/lib/usePrices.ts` owns EventSource subscription, reconnection and cleanup. `finally/backend/tests/test_market.py` verifies provider/cache/event behavior. Routers and main wire these modules without duplicating their ownership.

### database-portfolio-engine
This phase completes SQLite transaction/repository behavior in `finally/backend/db/schema.py` and `finally/backend/db/store.py`, and portfolio/trade calculations in `finally/backend/app/portfolio.py`. Initialize the six SPEC tables and seeds idempotently; enforce unique watchlist/positions, fractional quantities, weighted average costs, available cash/holdings checks, atomic rollback and snapshots. `finally/backend/tests/test_portfolio.py` verifies math and persistence. Extend the existing foundation database code in place.

### watchlist-market-ui
This phase implements watchlist handlers in `finally/backend/app/api/watchlist.py`, wiring via the existing router and main, with API tests in `finally/backend/tests/test_watchlist.py`. The actual Next.js page composes `finally/frontend/components/Header.tsx`, `finally/frontend/components/Watchlist.tsx`, and `finally/frontend/components/PriceChart.tsx` using the shared API/types/price hook. Implement exact SPEC watchlist CRUD, SSE-driven prices, flashes, sparklines, selected ticker state and connection indicators. Preserve foundation code and the static export contract.

### portfolio-visualisation-trading
This phase implements API handlers in `finally/backend/app/api/portfolio.py`, API tests in `finally/backend/tests/test_trading.py`, and the TradeBar, Positions, PortfolioSummary, PortfolioHeatmap and PnlChart components enumerated above. Wire them into the existing page/router/main without duplicating shared types or database logic. Preserve GET /api/portfolio, POST /api/portfolio/trade and GET /api/portfolio/history contracts, error semantics and atomic trading behavior.

### ai-trading-assistant
This phase implements LiteLLM/OpenRouter orchestration and deterministic mock parsing in `finally/backend/app/chat.py`, POST /api/chat in `finally/backend/app/api/chat.py`, behavior tests in `finally/backend/tests/test_chat.py`, and `finally/frontend/components/ChatPanel.tsx`. Reuse the existing portfolio/watchlist operations, persist conversation/actions, and wire router/main/page in place. LLM_MOCK=true must require no API key and yield deterministic structured actions.

### application-polish
This phase refines existing page/styles and adds `finally/frontend/components/Notifications.tsx` for the complete SPEC dark terminal experience, loading/empty/error states, responsive behavior, accessibility and streaming performance. It also prepares the frontend unit-test/Vitest setup and the Playwright package/config, five Page Objects and shared fixture/API helpers; the profile assigns these prerequisites here so they exist before the release scenario files run. Preserve existing features, routes, types and static-serving contracts. Verify both the Next.js build and real frontend component tests.

### testing-release
This phase completes the frontend component tests/Vitest setup, test package/config, all five Page Objects, shared fixtures/API helpers, all eight SPEC scenario files and the existing smoke test, isolated compose harness and README. The exact concrete file list is in workflow-profile.json and above. Preserve already implemented application files. Run backend tests, frontend component tests and full Playwright verification against the real image with LLM_MOCK=true. Assert ticker/cash/trade/chat/chart content and canonical API schemas; status-only smoke checks do not count.

## Acceptance mapping
The architecture satisfies the SPEC by keeping the exact HTTP contract at the API boundary, making the backend entrypoint the only composition root, and providing the required cross-platform operational and test harness files under finally/. The planned layout enumerates every SPEC required file. Environment and database placeholders support repeatable local execution; Docker supports isolated execution; Playwright verifies the user-visible result. Acceptance is complete only when each workflow phase's exit criteria pass, the exact route methods and paths match the SPEC, the required response schemas validate, and the full profile verification command succeeds without untracked implementation paths outside finally/.

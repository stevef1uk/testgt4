# Architecture for testgt4

## Overview
This design implements the SPEC as a small, locally runnable web application with a Python backend, a browser-facing API contract, and a Playwright smoke path. The layout_root is finally. The layout root is `finally/`; every deliverable is rooted there. The service is deliberately dependency-light: configuration comes from the environment, the application entrypoint owns startup, and the API layer exposes only the routes and schemas named by the SPEC. Docker and host scripts provide reproducible startup without changing the application contract.

The backend is organized around `finally/backend/app/main.py` as the composition root and `finally/backend/app/api/__init__.py` plus `finally/backend/app/api/schemas.py` as the API boundary. Static and browser verification concerns remain in `finally/test/`. The database directory is retained as the persistent-data mount required by the SPEC, while the initial implementation may use the SPEC's prescribed lightweight behavior rather than introducing an unrequested data model.

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
The SPEC's functional requirements are verified at the API boundary and through the browser journey. Schema validation cases belong with the API contract represented by `finally/backend/app/api/schemas.py`; route success and failure cases are exercised through the handlers in `finally/backend/app/api/__init__.py`. The delivery set does not invent extra test source files beyond the concrete SPEC required files. `finally/test/e2e.spec.ts` covers the externally observable happy path, validation/error behavior explicitly called out by the SPEC, and a reload or repeatability check where required.

## Integration and testing
The canonical verification command is the full-suite command specified by the workflow profile. The test harness starts the service using `finally/test/docker-compose.test.yml` or the profile's prescribed command, waits for the configured readiness condition, runs Playwright using `finally/test/playwright.config.ts`, and tears down containers afterward. Tests use a stable base URL from configuration and must not depend on a developer's current directory. Failures retain Playwright diagnostics while cleanup remains best effort.

## Docker & Deployment
`finally/Dockerfile` builds only the application runtime needed by the SPEC, copies the backend application, installs its declared dependencies, exposes the configured HTTP port, and uses the entrypoint in `finally/backend/app/main.py`. `finally/docker-compose.yml` supplies environment values, port mapping, and the `finally/db/` mount without baking secrets into the image. `finally/test/docker-compose.test.yml` layers isolated test settings and a deterministic readiness/test command over the same application contract. Host scripts delegate to compose and report failures; they do not silently ignore a failed startup.

## E2E / integration testing
`finally/test/playwright.config.ts` sets the base URL from the test environment, uses a deterministic browser project, and records traces/screenshots only on failure. `finally/test/e2e.spec.ts` drives the SPEC's externally visible flow and asserts exact visible/API outcomes, including the required route status and response shape. The test must work against the compose service and a locally started service, so it uses no hard-coded host filesystem paths or private backend imports.

## Delivery phases
Delivery is staged according to the exact delivery phase IDs in the workflow profile. Infrastructure phases create only their assigned scripts, environment, database marker, ignore rules, and harness/deployment files; application behavior remains in the phase assigned by the SPEC. The phase contracts below preserve that separation and map every required file to an owner.

## Requirements

### project-foundation
The foundation phase creates only its concrete profile-owned files: `finally/scripts/start_mac.sh`, `finally/scripts/stop_mac.sh`, `finally/scripts/start_windows.ps1`, `finally/scripts/stop_windows.ps1`, `finally/db/.gitkeep`, `finally/.env`, and `finally/.gitignore`. It establishes the runnable skeleton described by the SPEC, including environment loading, SQLite initialization, Docker startup, health behavior, and real static dashboard serving. It must not pull later market, portfolio, AI, or release-test implementation into this phase.

### core-market-infrastructure
This phase implements the SPEC market-data platform: an interchangeable GBM simulator and optional Massive provider, environment selection, shared price cache, background updates, and continuous SSE delivery at `GET /api/stream/prices`. The profile assigns no additional concrete required file; implementation may use the backend structure while preserving the exact route and event semantics. SSE reconnection remains a client responsibility supported by the server's long-lived stream.

### database-portfolio-engine
This phase implements the SPEC SQLite schema, lazy initialization, repository/data access behavior, ten default watchlist tickers, the 10,000-dollar cash seed, positions, trades, portfolio calculations, and snapshots. The profile assigns no additional concrete required file. It must preserve persistence across restarts and must not move the later API schema or E2E harness ownership into this phase.

### watchlist-market-ui
This phase delivers the live watchlist and market experience: the exact watchlist API, SSE-driven prices, price flashes, accumulated sparklines, selected-ticker chart state, responsive terminal layout, header, and connection indicator. Its concrete profile-owned file is `finally/backend/app/main.py`; that entrypoint must wire the feature while preserving the SPEC static export contract and never serving placeholder HTML.

### portfolio-visualisation-trading
This phase delivers the manual trade bar, market buy/sell workflow, validation, positions table, portfolio summary, heatmap, P&L chart, live valuation, and immediate UI updates. The profile assigns no additional concrete required file. The implementation must preserve the exact `GET /api/portfolio`, `POST /api/portfolio/trade`, and `GET /api/portfolio/history` contracts and their SPEC request/response meanings.

### ai-trading-assistant
This phase delivers the specified LiteLLM/OpenRouter integration using the Cerebras inference path, structured output parsing, prompt and portfolio context construction, conversation persistence, automatic trade and watchlist actions, deterministic `LLM_MOCK=true` behavior, and error recovery. The profile assigns no additional concrete required file. The exact `POST /api/chat` contract remains authoritative.

### application-polish
This phase refines the complete SPEC experience with dark terminal styling, animations, loading and empty states, notifications, responsive improvements, accessibility, and streaming performance. The profile assigns no additional concrete required file. It must preserve all earlier routes, data semantics, static serving behavior, and real-content dashboard assertions.

### testing-release
This phase owns these concrete profile-required files: `finally/test/playwright.config.ts`, `finally/backend/app/api/__init__.py`, `finally/backend/app/api/schemas.py`, `finally/test/e2e.spec.ts`, `finally/Dockerfile`, `finally/docker-compose.yml`, and `finally/test/docker-compose.test.yml`. The harness uses the real static export and dashboard content, sets `LLM_MOCK=true`, health-checks `/api/health`, uses the required compose context and mount, and covers the SPEC Section 13 scenarios and Page Object contract. Tests must assert real content and exact schemas, never a placeholder page or status-only success.

## Acceptance mapping
The architecture satisfies the SPEC by keeping the exact HTTP contract at the API boundary, making the backend entrypoint the only composition root, and providing the required cross-platform operational and test harness files under finally/. The planned layout enumerates every SPEC required file. Environment and database placeholders support repeatable local execution; Docker supports isolated execution; Playwright verifies the user-visible result. Acceptance is complete only when each workflow phase's exit criteria pass, the exact route methods and paths match the SPEC, the required response schemas validate, and the full profile verification command succeeds without untracked implementation paths outside finally/.

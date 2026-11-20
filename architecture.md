# Architecture for testgt4

## Overview

FinAlly is a single-origin AI trading workstation matching SPEC. Next.js
TypeScript is exported statically and served by FastAPI in one container on
port 8000. SQLite is persistent, market prices use a simulator by default or
Massive when configured, SSE provides live prices, and Playwright verifies
real rendered behavior. The initial database contains AAPL, GOOGL, MSFT,
AMZN, TSLA, NVDA, META, JPM, V, NFLX and $10,000 cash. Missing exported
HTML is an error, never a placeholder.

## Planned file layout

All paths use the `finally/` layout root.

- `finally/planning/PLAN.md`
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

Additional frontend, backend, unit-test, page-object, and fixture files are
owned by their implementing phases under `finally/frontend/`,
`finally/backend/`, and `finally/test/`. Generated `finally/frontend/out/`
and runtime `finally/db/finally.db` are outputs, not handwritten deliverables.

## Delivery phases

```yaml
delivery_phases:
  - id: project-foundation
    title: Project Foundation
    spec_focus: Project Foundation
    required_files:
      - finally/scripts/start_mac.sh
      - finally/scripts/stop_mac.sh
      - finally/scripts/start_windows.ps1
      - finally/scripts/stop_windows.ps1
      - finally/db/.gitkeep
      - finally/.env
      - finally/.gitignore
      - finally/backend/app/main.py
      - finally/Dockerfile
      - finally/docker-compose.yml
    qa_verify_command: 'test -x finally/scripts/start_mac.sh && test -x finally/scripts/stop_mac.sh && sh -n finally/scripts/start_mac.sh && sh -n finally/scripts/stop_mac.sh && test -f finally/scripts/start_windows.ps1 && test -f finally/scripts/stop_windows.ps1 && test -f finally/db/.gitkeep && test -f finally/.env && test -f finally/.gitignore && test -f finally/backend/app/main.py && test -f finally/Dockerfile && test -f finally/docker-compose.yml'
    depends_on: []
    file_dependencies:
      finally/Dockerfile: [finally/backend/app/main.py]
      finally/docker-compose.yml: [finally/Dockerfile, finally/.env]
  - id: core-market-infrastructure
    title: Core Market Infrastructure
    spec_focus: Core Market Infrastructure
    required_files:
      - finally/planning/PLAN.md
      - finally/backend/app/main.py
    qa_verify_command: 'test -f finally/planning/PLAN.md && PYTHONPATH=finally/backend python -c "from app.main import create_app; assert any(r.path == "/api/stream/prices" for r in create_app().routes)"'
    depends_on: [project-foundation]
  - id: database-portfolio-engine
    title: Database & Portfolio Engine
    spec_focus: Database & Portfolio Engine
    required_files: [finally/backend/app/main.py]
    qa_verify_command: 'PYTHONPATH=finally/backend python -c "from app.main import create_app; p={r.path for r in create_app().routes}; assert {\"/api/portfolio\", \"/api/portfolio/trade\", \"/api/portfolio/history\"} <= p"'
    depends_on: [core-market-infrastructure]
  - id: watchlist-market-ui
    title: Watchlist & Market UI
    spec_focus: Watchlist & Market UI
    required_files: [finally/backend/app/main.py]
    qa_verify_command: 'PYTHONPATH=finally/backend python -c "from app.main import create_app; p={r.path for r in create_app().routes}; assert \"/api/watchlist\" in p and \"/api/watchlist/{ticker}\" in p"'
    depends_on: [database-portfolio-engine]
  - id: portfolio-visualisation-trading
    title: Portfolio Visualisation & Trading
    spec_focus: Portfolio Visualisation & Trading
    required_files: [finally/backend/app/main.py]
    qa_verify_command: 'PYTHONPATH=finally/backend python -c "from app.main import create_app; assert any(r.path == \"/api/portfolio/trade\" for r in create_app().routes)"'
    depends_on: [watchlist-market-ui]
  - id: ai-trading-assistant
    title: AI Trading Assistant
    spec_focus: AI Trading Assistant
    required_files: [finally/backend/app/main.py]
    qa_verify_command: 'PYTHONPATH=finally/backend python -c "from app.main import create_app; assert any(r.path == \"/api/chat\" for r in create_app().routes)"'
    depends_on: [portfolio-visualisation-trading]
  - id: application-polish
    title: Application Polish
    spec_focus: Application Polish
    required_files: [finally/backend/app/main.py]
    qa_verify_command: 'PYTHONPATH=finally/backend python -c "from app.main import create_app; assert create_app() is not None"'
    depends_on: [ai-trading-assistant]
  - id: testing-release
    title: Testing & Release
    spec_focus: Testing & Release
    required_files:
      - finally/test/playwright.config.ts
      - finally/backend/app/api/__init__.py
      - finally/backend/app/api/schemas.py
      - finally/test/e2e.spec.ts
      - finally/Dockerfile
      - finally/docker-compose.yml
      - finally/test/docker-compose.test.yml
    qa_verify_command: 'docker compose -f finally/test/docker-compose.test.yml down --remove-orphans && docker compose -f finally/test/docker-compose.test.yml build --no-cache && docker compose -f finally/test/docker-compose.test.yml up --exit-code-from playwright'
    depends_on: [application-polish]
    file_dependencies:
      finally/backend/app/api/__init__.py: [finally/backend/app/main.py]
      finally/backend/app/api/schemas.py: [finally/backend/app/api/__init__.py]
      finally/test/playwright.config.ts: [finally/test/e2e.spec.ts]
      finally/test/docker-compose.test.yml: [finally/docker-compose.yml, finally/Dockerfile, finally/test/playwright.config.ts]
```

## Requirements

### project-foundation

Deliver the runnable repository skeleton, planning document, Next.js export,
FastAPI/uv project, SQLite initialization boundary, Docker files, scripts,
environment loading, and health endpoint. `GET /` must serve actual
`finally/frontend/out/index.html` containing the Market Dashboard heading,
ten default tickers with prices, and $10,000 cash. Scripts must be idempotent,
resolve their own directory, retain the database volume, and preserve errors.

### core-market-infrastructure

Define one interface for a GBM simulator and Massive REST provider. Select
Massive only when MASSIVE_API_KEY is non-empty. Maintain latest and previous
prices, timestamps, and direction in a shared cache. `GET /api/stream/prices`
is an SSE stream of those values; EventSource reconnects automatically.

### database-portfolio-engine

Lazily create users_profile, watchlist, positions, trades,
portfolio_snapshots, and chat_messages in SQLite with user_id `"default"`.
Seed ten tickers and 10000.0 cash. Use parameterized transactions; support
fractional market orders, cash/share validation, immediate position updates,
and snapshots after trades and periodically. Persistence survives restarts.

### watchlist-market-ui

Implement `GET /api/watchlist`, `POST /api/watchlist`, and
`DELETE /api/watchlist/{ticker}`. Render a dark desktop-first dashboard with
live prices, green/red flash transitions, accumulated sparklines, a selected
ticker chart, responsive layout, and green/yellow/red connection status.
Add, remove, and duplicate behavior must be visible.

### portfolio-visualisation-trading

Implement `GET /api/portfolio`, `POST /api/portfolio/trade`, and
`GET /api/portfolio/history` with SPEC schemas. Render trade controls,
positions, portfolio summary, P&L heatmap, and value-history chart. Buy and
sell are instant fee-free market orders; failed validation is atomic.

### ai-trading-assistant

Implement `POST /api/chat` returning message, trades, and watchlist_changes.
Construct portfolio-aware prompts and use LiteLLM via OpenRouter with the
specified Cerebras model and structured output. LLM_MOCK=true is deterministic.
Validate and auto-execute actions through shared services and persist history.

### application-polish

Complete dark terminal styling, animations, loading and empty states,
notifications, accessible controls, responsive behavior, and recovery for
API, SSE, and chat failures while retaining real rendered data.

### testing-release

Provide backend unit/API tests, frontend component tests, and the mandatory
Playwright Page Objects and scenarios in SPEC. Cover seeded content, live
prices, SSE reconnect, watchlist CRUD, trading validation, charts, heatmap,
mock chat actions, navigation, and the full MVP journey. Assertions must
check real headings, ticker text, prices, cash, portfolio values, or chat
content, never placeholder text.

## Module / bead ownership

| File | Owns | Must not define |
|---|---|---|
| `finally/backend/app/main.py` | `create_app(...) -> FastAPI`, module `app`, lifecycle and static serving | duplicate routes or schemas |
| `finally/backend/app/api/__init__.py` | `router` and canonical route registration | Docker startup or database schema |
| `finally/backend/app/api/schemas.py` | Pydantic request/response contracts | route handlers or persistence |
| `finally/planning/PLAN.md` | shared phase notes and agent contract | runtime behavior |
| `finally/test/playwright.config.ts` | Playwright configuration | production UI behavior |
| `finally/test/e2e.spec.ts` | release smoke assertions | server implementation |

## HTTP + entrypoint integration

The exact SPEC API paths are `GET /api/stream/prices`,
`GET /api/portfolio`, `POST /api/portfolio/trade`,
`GET /api/portfolio/history`, `GET /api/watchlist`, `POST /api/watchlist`,
`DELETE /api/watchlist/{ticker}`, `POST /api/chat`, and `GET /api/health`.
`create_app()` initializes providers, registers the router exactly once, serves
the real `finally/frontend/out/index.html` at `GET /`, and returns a diagnostic
error if it is absent. The module-level `app` is the ASGI target on
0.0.0.0:8000.

## Unit tests

Backend tests cover GBM, Massive normalization, provider selection, cache and
SSE payloads, schema/seed initialization, trade math, snapshots, route shapes,
errors, and structured chat parsing. Frontend tests cover dashboard rendering,
SSE state, flash classes, watchlist CRUD, trade state, charts, heatmap,
chat loading, and accessibility. Tests isolate SQLite and use LLM_MOCK=true
for network-free behavior.

## Integration and testing

Verification runs from the repository root. Compose cleanup is in a trap or
finally path and preserves the original exit status. The release harness
builds the real image, waits for `GET /api/health`, runs Playwright in its own
container, and checks user-visible content. BASE_URL defaults to
http://localhost:8000 and the browser project is chromium.

## Docker & Deployment

`finally/Dockerfile` is a two-stage build. The frontend stage uses
`node:20-slim`, copies the Next.js project under `finally/frontend/`, runs
`npm install --ignore-scripts`, and runs `npm run build` with
`output: "export"` to produce `finally/frontend/out/`. The runtime stage uses
`python:3.12-slim`, installs uv, copies `finally/backend/` with project
metadata and lockfile, runs `uv sync --frozen`, and copies the generated
export into the runtime image. Node tooling is absent at runtime.

The image exposes TCP port 8000 and runs
`CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`.
`finally/docker-compose.yml` maps host port 8000 to container port 8000,
loads `finally/.env`, mounts persistent database storage, and health-checks
http://localhost:8000/api/health. `finally/test/docker-compose.test.yml` uses
the project root as build context, mounts it into Playwright, sets
LLM_MOCK=true, and runs the release suite against the app service.

## E2E / integration testing

The Playwright harness uses Page Objects for dashboard, watchlist, trade,
portfolio, and chat and uses role, text, or test-ID selectors. It asserts all
ten tickers, $10,000, prices, connection status, watchlist changes, price
flashes, sparklines, buy/sell state, validation errors, visualizations,
mocked chat execution, SSE reconnection, navigation, and the complete happy
path. Every SPEC UI feature has behavioral browser evidence.

## Acceptance mapping

The design follows the SPEC dependency flow from foundation through market
infrastructure, persistence, market UI, trading, AI, polish, and release. It
preserves exact HTTP paths, static-export behavior, SQLite persistence, seeded
data, provider selection, deterministic mock mode, cross-platform scripts,
Docker port and command, and real-content E2E evidence.

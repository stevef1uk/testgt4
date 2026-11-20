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
- `finally/.github/workflows/ci.yml`
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
- `finally/frontend/package.json`
- `finally/frontend/tsconfig.json`
- `finally/frontend/next.config.js`
- `finally/frontend/next-env.d.ts`
- `finally/frontend/app/layout.tsx`
- `finally/frontend/app/page.tsx`
- `finally/frontend/app/globals.css`
- `finally/frontend/components/Header.tsx`
- `finally/frontend/components/Sidebar.tsx`
- `finally/frontend/components/MarketOverview.tsx`
- `finally/frontend/components/PortfolioSummary.tsx`
- `finally/frontend/components/Watchlist.tsx`
- `finally/frontend/components/TradingPanel.tsx`
- `finally/frontend/components/PriceChart.tsx`
- `finally/frontend/components/ChatAssistant.tsx`
- `finally/frontend/components/ChatAssistant.test.tsx`
- `finally/backend/db/schema.py`
- `finally/backend/app/portfolio/engine.py`
- `finally/backend/app/market/gbm.py`
- `finally/backend/app/market/massive.py`
- `finally/backend/app/market/cache.py`
- `finally/backend/app/market/sse.py`
- `finally/backend/tests/test_market_infrastructure.py`
- `finally/test/watchlist-market-ui.spec.ts`
- `finally/test/portfolio-visualisation-trading.spec.ts`
- `finally/frontend/app/polish.css`
- `finally/test/application-polish.spec.ts`

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
      - finally/planning/PLAN.md
      - finally/backend/app/main.py
      - finally/frontend/package.json
      - finally/frontend/tsconfig.json
      - finally/frontend/next.config.js
      - finally/frontend/app/layout.tsx
      - finally/frontend/app/page.tsx
      - finally/frontend/app/globals.css
      - finally/Dockerfile
      - finally/docker-compose.yml
    qa_verify_command: 'test -f finally/planning/PLAN.md && test -f finally/backend/app/main.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && docker compose -f finally/docker-compose.yml build'
    depends_on: []
    file_dependencies:
      finally/frontend/next.config.js: [finally/frontend/package.json, finally/frontend/tsconfig.json]
      finally/frontend/app/layout.tsx: [finally/frontend/next.config.js, finally/frontend/app/globals.css]
      finally/frontend/app/page.tsx: [finally/frontend/app/layout.tsx]
      finally/Dockerfile: [finally/backend/app/main.py, finally/frontend/package.json, finally/frontend/next.config.js, finally/frontend/app/page.tsx]
  - id: project-foundation-support
    title: Project Foundation Support
    spec_focus: Project Foundation
    required_files:
      - finally/scripts/start_mac.sh
      - finally/scripts/stop_mac.sh
      - finally/scripts/start_windows.ps1
      - finally/scripts/stop_windows.ps1
      - finally/.env
      - finally/.gitignore
      - finally/.github/workflows/ci.yml
      - finally/db/.gitkeep
      - finally/backend/db/schema.py
    qa_verify_command: 'test -f finally/scripts/start_mac.sh && test -f finally/scripts/stop_mac.sh && test -f finally/scripts/start_windows.ps1 && test -f finally/scripts/stop_windows.ps1 && test -f finally/.env && test -f finally/.gitignore && test -f finally/.github/workflows/ci.yml && test -f finally/db/.gitkeep && test -f finally/backend/db/schema.py'
    depends_on: [project-foundation]
    file_dependencies:
      finally/backend/db/schema.py: [finally/db/.gitkeep]
  - id: core-market-infrastructure
    title: Core Market Infrastructure
    spec_focus: Core Market Infrastructure
    required_files:
      - finally/backend/app/api/__init__.py
      - finally/backend/app/api/schemas.py
      - finally/frontend/next-env.d.ts
      - finally/backend/tests/test_market_infrastructure.py
      - finally/backend/app/market/sse.py
      - finally/backend/app/market/cache.py
      - finally/backend/app/market/massive.py
      - finally/backend/app/market/gbm.py
    qa_verify_command: 'test -f finally/.env && test -f finally/.gitignore && test -f finally/backend/app/api/__init__.py && test -f finally/backend/app/api/schemas.py && test -f finally/frontend/next-env.d.ts && test -f finally/backend/app/market/gbm.py && test -f finally/backend/app/market/massive.py && test -f finally/backend/app/market/cache.py && test -f finally/backend/app/market/sse.py && test -f finally/backend/tests/test_market_infrastructure.py && PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py && (cd finally/frontend && npm run build)' 
    depends_on: [project-foundation-support]
    file_dependencies:
      finally/backend/app/market/gbm.py: [finally/backend/app/main.py]
      finally/backend/app/market/massive.py: [finally/backend/app/main.py]
      finally/backend/app/market/cache.py: [finally/backend/app/main.py]
      finally/backend/app/market/sse.py: [finally/backend/app/main.py, finally/backend/app/market/cache.py]
      finally/backend/tests/test_market_infrastructure.py: [finally/backend/app/market/gbm.py, finally/backend/app/market/massive.py, finally/backend/app/market/cache.py, finally/backend/app/market/sse.py]
  - id: database-portfolio-engine
    title: Database & Portfolio Engine
    spec_focus: Database & Portfolio Engine
    required_files:
      - finally/backend/app/portfolio/engine.py
    qa_verify_command: 'PYTHONPATH=finally/backend python -c "from app.main import create_app; p={r.path for r in create_app().routes}; assert {\"/api/portfolio\", \"/api/portfolio/trade\", \"/api/portfolio/history\"} <= p"'
    depends_on: [core-market-infrastructure]
  - id: watchlist-market-ui
    title: Watchlist & Market UI
    spec_focus: Watchlist & Market UI
    required_files:
      - finally/frontend/components/Header.tsx
      - finally/frontend/components/Sidebar.tsx
      - finally/frontend/components/MarketOverview.tsx
      - finally/frontend/components/Watchlist.tsx
      - finally/frontend/components/PriceChart.tsx
      - finally/test/watchlist-market-ui.spec.ts
    qa_verify_command: 'test -f finally/frontend/components/Header.tsx && test -f finally/frontend/components/Sidebar.tsx && test -f finally/frontend/components/MarketOverview.tsx && test -f finally/frontend/components/Watchlist.tsx && test -f finally/frontend/components/PriceChart.tsx && PYTHONPATH=finally/backend python -c "from app.main import create_app; p={r.path for r in create_app().routes}; assert \"/api/watchlist\" in p and \"/api/watchlist/{ticker}\" in p"  && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) (cd finally/frontend && npm run build)'
    depends_on: [database-portfolio-engine]
    file_dependencies:
      finally/frontend/components/Header.tsx: [finally/frontend/app/layout.tsx]
      finally/frontend/components/Sidebar.tsx: [finally/frontend/app/layout.tsx]
      finally/frontend/components/MarketOverview.tsx: [finally/frontend/app/page.tsx]
      finally/frontend/components/Watchlist.tsx: [finally/frontend/app/page.tsx]
      finally/frontend/components/PriceChart.tsx: [finally/frontend/app/page.tsx]
      finally/test/watchlist-market-ui.spec.ts: [finally/frontend/components/Watchlist.tsx, finally/frontend/components/PriceChart.tsx]
  - id: portfolio-visualisation-trading
    title: Portfolio Visualisation & Trading
    spec_focus: Portfolio Visualisation & Trading
    required_files:
      - finally/frontend/components/PortfolioSummary.tsx
      - finally/frontend/components/TradingPanel.tsx
      - finally/test/portfolio-visualisation-trading.spec.ts
    qa_verify_command: 'test -f finally/frontend/components/PortfolioSummary.tsx && test -f finally/frontend/components/TradingPanel.tsx && PYTHONPATH=finally/backend python -c "from app.main import create_app; assert any(r.path == \"/api/portfolio/trade\" for r in create_app().routes)"  && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) (cd finally/frontend && npm run build)'
    depends_on: [watchlist-market-ui]
    file_dependencies:
      finally/frontend/components/PortfolioSummary.tsx: [finally/frontend/app/page.tsx]
      finally/frontend/components/TradingPanel.tsx: [finally/frontend/app/page.tsx]
      finally/test/portfolio-visualisation-trading.spec.ts: [finally/frontend/components/PortfolioSummary.tsx, finally/frontend/components/TradingPanel.tsx]
  - id: ai-trading-assistant
    title: AI Trading Assistant
    spec_focus: AI Trading Assistant
    required_files:
      - finally/frontend/components/ChatAssistant.tsx
      - finally/frontend/components/ChatAssistant.test.tsx
    qa_verify_command: 'test -f finally/frontend/components/ChatAssistant.tsx && test -f finally/frontend/components/ChatAssistant.test.tsx && PYTHONPATH=finally/backend python -c "from app.main import create_app; assert any(r.path == \"/api/chat\" for r in create_app().routes)"  && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) && (cd finally/frontend && npm run build) (cd finally/frontend && npm run build)'
    depends_on: [portfolio-visualisation-trading]
    file_dependencies:
      finally/frontend/components/ChatAssistant.tsx: [finally/frontend/app/page.tsx]
  - id: application-polish
    title: Application Polish
    spec_focus: Application Polish
    required_files:
      - finally/frontend/app/polish.css
      - finally/test/application-polish.spec.ts
    qa_verify_command: 'PYTHONPATH=finally/backend python -c "from app.main import create_app; assert create_app() is not None"'
    depends_on: [ai-trading-assistant]
  - id: testing-release
    title: Testing & Release
    spec_focus: Testing & Release
    required_files:
      - finally/test/playwright.config.ts
      - finally/test/e2e.spec.ts
      - finally/test/docker-compose.test.yml
    qa_verify_command: 'docker compose -f finally/test/docker-compose.test.yml down --remove-orphans && docker compose -f finally/test/docker-compose.test.yml build --no-cache && docker compose -f finally/test/docker-compose.test.yml up --exit-code-from playwright'
    depends_on: [application-polish]
    file_dependencies:
      finally/test/playwright.config.ts: [finally/test/e2e.spec.ts]
      finally/test/docker-compose.test.yml: [finally/docker-compose.yml, finally/Dockerfile, finally/test/playwright.config.ts]
```

## Requirements

### project-foundation
This phase owns the cross-platform launch and shutdown scripts, environment loading from finally/.env, repository hygiene in finally/.gitignore, the SQLite marker and schema initialization in finally/db/.gitkeep and finally/backend/db/schema.py, and CI linting in finally/.github/workflows/ci.yml. These foundation assets are intentionally delivered before market infrastructure or portfolio behavior; later phases consume the initialized database rather than owning its bootstrap.

Deliver the runnable repository skeleton, planning document, Next.js export,
FastAPI/uv project, SQLite initialization boundary, Docker files, scripts,
environment loading, and health endpoint. `GET /` must serve actual
`finally/frontend/out/index.html` containing the Market Dashboard heading,
ten default tickers with prices, and $10,000 cash. Scripts must be idempotent,
resolve their own directory, retain the database volume, and preserve errors.

### project-foundation-support
This continuation of Project Foundation owns the cross-platform launch and
shutdown scripts, environment loading, repository hygiene, CI linting, the
SQLite runtime marker, and schema initialization. It is a foundation-only
batch that completes every Phase 1 deliverable before market behavior begins.

Scripts resolve their own location, are idempotent, preserve the database
volume, and return failures. The environment and CI files are configuration
artifacts consumed by the runnable skeleton and later verification.

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
The assistant component is delivered with focused interaction coverage in `finally/frontend/components/ChatAssistant.test.tsx`; the phase gate must run that test together with the frontend production build.

Implement `POST /api/chat` returning message, trades, and watchlist_changes.
Construct portfolio-aware prompts and use LiteLLM via OpenRouter with the
specified Cerebras model and structured output. LLM_MOCK=true is deterministic.
Validate and auto-execute actions through shared services and persist history.

### application-polish
Application-polish verification is owned by `finally/test/application-polish.spec.ts`. It must exercise the responsive layout at narrow and wide viewports, assert accessible names and keyboard focus order, and verify that a market/API failure renders a recoverable error state rather than a blank or misleading panel. The polish phase owns this test alongside `finally/frontend/app/polish.css`; release remains responsible for the full-suite harness and broader end-to-end regression.

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

## Rework ownership additions

The core-market-infrastructure phase owns the market behavior seams as concrete implementation and test paths: `finally/backend/app/market/gbm.py` provides deterministic geometric-Brownian-motion simulation, `finally/backend/app/market/massive.py` provides the configured Massive provider with fallback/error handling, `finally/backend/app/market/cache.py` owns bounded quote caching and expiry, and `finally/backend/app/market/sse.py` owns the streaming response and disconnect cleanup. Their behavioral regression coverage is owned by `finally/backend/tests/test_market_infrastructure.py`, including GBM validity, provider normalization, cache expiry, and SSE event framing.

The watchlist-market-ui phase owns browser coverage in `finally/test/watchlist-market-ui.spec.ts`; it must assert rendered market rows, symbol selection, watchlist state, and live-price refresh rather than only checking source files. The portfolio-visualisation-trading phase owns browser coverage in `finally/test/portfolio-visualisation-trading.spec.ts`; it must assert portfolio values, chart rendering, order validation, and the visible post-trade state. These tests remain phase deliverables alongside their production components.


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

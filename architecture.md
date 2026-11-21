# Architecture for testgt4

## Overview

FinAlly is a single-origin AI trading workstation. The design follows SPEC exactly: a static-export Next.js TypeScript dashboard is built into `finally/frontend/out/`, and FastAPI serves that export and the REST/SSE API from port 8000. SQLite is the persistent single-user store, initialized lazily with the ten specified tickers and $10,000 cash. The market provider is selected by environment: deterministic/in-process GBM simulation by default, or Massive REST polling when its key is present. LiteLLM/OpenRouter structured responses power chat, with deterministic `LLM_MOCK=true` behavior.

The backend owns persistence, validation, portfolio calculations, market-provider coordination, SSE, chat orchestration, and static serving. The frontend owns rendering, EventSource lifecycle, local sparkline history, chart selection, trade controls, portfolio visualizations, and chat interaction. The Docker image is multi-stage (Node build followed by Python runtime); the compose and scripts are convenience and test harness integration, not a second runtime service. No placeholder HTML is permitted: the root route reads the real exported index and returns an error if it is absent.

## Planned file layout

Every implementation and test artifact is enumerated below. `finally/backend/app/main_test.py` is an explicit foundation integration test, added because the foundation exit criterion tests real root content rather than merely file existence. `finally/backend/tests/test_chat.py` is the backend chat contract test used alongside the frontend chat test.
The planning contract is `finally/planning/PLAN.md`.

- `finally/planning/PLAN.md`
- `finally/backend/app/main.py`
- `finally/backend/app/main_test.py`
- `finally/backend/app/api/__init__.py`
- `finally/backend/app/api/schemas.py`
- `finally/backend/db/schema.py`
- `finally/backend/app/market/gbm.py`
- `finally/backend/app/market/massive.py`
- `finally/backend/app/market/cache.py`
- `finally/backend/app/market/sse.py`
- `finally/backend/app/portfolio/engine.py`
- `finally/backend/tests/test_market_infrastructure.py`
- `finally/backend/tests/test_chat.py`
- `finally/frontend/package.json`
- `finally/frontend/tsconfig.json`
- `finally/frontend/next.config.js`
- `finally/frontend/next-env.d.ts`
- `finally/frontend/app/layout.tsx`
- `finally/frontend/app/page.tsx`
- `finally/frontend/app/globals.css`
- `finally/frontend/app/polish.css`
- `finally/frontend/components/Header.tsx`
- `finally/frontend/components/Sidebar.tsx`
- `finally/frontend/components/MarketOverview.tsx`
- `finally/frontend/components/Watchlist.tsx`
- `finally/frontend/components/PriceChart.tsx`
- `finally/frontend/components/PortfolioSummary.tsx`
- `finally/frontend/components/TradingPanel.tsx`
- `finally/frontend/components/ChatAssistant.tsx`
- `finally/frontend/components/ChatAssistant.test.tsx`
- `finally/test/watchlist-market-ui.spec.ts`
- `finally/test/portfolio-visualisation-trading.spec.ts`
- `finally/test/application-polish.spec.ts`
- `finally/test/playwright.config.ts`
- `finally/test/e2e.spec.ts`
- `finally/test/docker-compose.test.yml`
- `finally/Dockerfile`
- `finally/docker-compose.yml`
- `finally/scripts/start_mac.sh`
- `finally/scripts/stop_mac.sh`
- `finally/scripts/start_windows.ps1`
- `finally/scripts/stop_windows.ps1`
- `finally/.env`
- `finally/.gitignore`
- `finally/.github/workflows/ci.yml`
- `finally/db/.gitkeep`

## Module / bead ownership

| File | Owns exported symbols and responsibilities | Must not define |
|---|---|---|
| `finally/backend/app/main.py` | `create_app(...) -> FastAPI`, health/root/static wiring, provider lifecycle | Database schema SQL, UI markup, duplicate route implementations |
| `finally/backend/app/api/__init__.py` | FastAPI route registration/factory helpers for canonical API paths | A second application entrypoint or divergent paths |
| `finally/backend/app/api/schemas.py` | Pydantic request/response models for watchlist, portfolio, trade, history, and chat contracts | Persistence or market polling |
| `finally/backend/db/schema.py` | SQLite initialization, idempotent tables, and exact default seed values | HTTP handlers or frontend state |
| `finally/backend/app/market/gbm.py` | GBM simulator/provider interface and seeded-price generation | Database writes or SSE formatting |
| `finally/backend/app/market/massive.py` | Massive REST adapter implementing the same provider interface | Portfolio calculations |
| `finally/backend/app/market/cache.py` | Latest/previous/timestamp price cache and provider selection support | Browser rendering |
| `finally/backend/app/market/sse.py` | `/api/stream/prices` event generator and SSE response | Trade authorization or HTML |
| `finally/backend/app/portfolio/engine.py` | Position, cash, market-order, P&L, snapshot, watchlist, and chat persistence operations | React components or provider-specific polling |
| `finally/frontend/app/page.tsx` | Dashboard composition and client state boundary | Python/API server |
| `finally/frontend/app/layout.tsx` | Metadata, document shell, global styles | Feature-specific trading logic |
| `finally/frontend/components/Header.tsx` | Header cash/value/status presentation | API route definitions |
| `finally/frontend/components/Sidebar.tsx` | Terminal/sidebar layout and chat placement | Portfolio mutation rules |
| `finally/frontend/components/MarketOverview.tsx` | Market panel composition | SQLite access |
| `finally/frontend/components/Watchlist.tsx` | Watchlist rows, CRUD controls, flash classes, sparkline data | Server-side price generation |
| `finally/frontend/components/PriceChart.tsx` | Selected ticker history visualization | Trade execution |
| `finally/frontend/components/PortfolioSummary.tsx` | Positions, heatmap, P&L chart, live totals | API validation |
| `finally/frontend/components/TradingPanel.tsx` | Market-order form and error/result presentation | Direct database access |
| `finally/frontend/components/ChatAssistant.tsx` | Chat history, loading state, structured action confirmations | LLM provider calls |
| `finally/frontend/components/ChatAssistant.test.tsx` | Component tests for rendering/loading/action confirmations | Production components |
| the concrete browser test files listed below | Browser-level behavior and real-content assertions | Unit implementation |

Python public contracts use typed functions/classes and Pydantic models; TypeScript components use typed props and event callbacks. The engine is the sole owner of transaction validation: buys require sufficient cash, sells require sufficient shares, and every successful trade records a trade and immediate portfolio snapshot.

## HTTP + entrypoint integration

The canonical routes are exactly those in SPEC:

| Method | Path | Contract |
|---|---|---|
| GET | `/api/stream/prices` | SSE events containing ticker, price, previous price, timestamp, and change direction |
| GET | `/api/portfolio` | Current positions, cash balance, total value, and unrealized P&L |
| POST | `/api/portfolio/trade` | Accepts `{ticker, quantity, side}` and executes a market order |
| GET | `/api/portfolio/history` | Portfolio value snapshots |
| GET | `/api/watchlist` | Watchlist tickers with latest prices |
| POST | `/api/watchlist` | Accepts `{ticker}` and adds it |
| DELETE | `/api/watchlist/{ticker}` | Removes the ticker |
| POST | `/api/chat` | Complete JSON response containing `message` and executed actions |
| GET | `/api/health` | Deployment health success response |

`finally/backend/app/main.py` exposes `create_app(...) -> FastAPI`. The entrypoint reads configuration, establishes the SQLite path, initializes schema lazily/on startup, creates the cache and selected provider, passes those dependencies into route registration, starts/stops the background market task, mounts API routes before the static fallback, and serves `finally/frontend/out/index.html` at root. The root handler uses the SPEC path calculation and returns a diagnostic server error if that file is absent; it never synthesizes placeholder HTML. The Docker command runs the app on port 8000. EventSource clients reconnect natively and the frontend maps connection state to the required green/yellow/red indicator.

Portfolio and chat routes call the engine and schemas, never duplicate arithmetic. Chat loads recent conversation, portfolio/watchlist context, invokes LiteLLM through the specified OpenRouter model/provider contract unless `LLM_MOCK=true`, validates structured trades and watchlist changes through the same engine, persists user/assistant messages, and returns complete JSON.

## Delivery phases

```yaml
delivery_phases:
  - id: project-foundation
    title: Project Foundation
    spec_focus: Project Foundation
    required_files:
      - finally/backend/app/main.py
      - finally/backend/app/main_test.py
      - finally/frontend/package.json
      - finally/frontend/tsconfig.json
      - finally/frontend/next.config.js
      - finally/frontend/app/layout.tsx
      - finally/frontend/app/page.tsx
      - finally/frontend/app/globals.css
      - finally/Dockerfile
      - finally/docker-compose.yml
    qa_verify_command: 'test -f finally/backend/app/main.py && test -f finally/backend/app/main_test.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py && (cd finally/frontend && npm run build)'
    depends_on: []
    file_dependencies:
      finally/backend/app/main.py: [finally/frontend/app/page.tsx, finally/frontend/app/layout.tsx]
      finally/backend/app/main_test.py: [finally/backend/app/main.py, finally/frontend/app/page.tsx]
      finally/Dockerfile: [finally/backend/app/main.py, finally/frontend/package.json, finally/frontend/next.config.js, finally/frontend/app/page.tsx]
      finally/frontend/app/layout.tsx: [finally/frontend/next.config.js, finally/frontend/app/globals.css]
      finally/frontend/app/page.tsx: [finally/frontend/app/layout.tsx]
      finally/frontend/next.config.js: [finally/frontend/package.json, finally/frontend/tsconfig.json]
  - id: project-foundation-support

    title: Project Foundation Support
    spec_focus: Project Foundation
    required_files:
      - finally/planning/PLAN.md
      - finally/scripts/start_mac.sh
      - finally/scripts/stop_mac.sh
      - finally/scripts/start_windows.ps1
      - finally/scripts/stop_windows.ps1
      - finally/.env
      - finally/.gitignore
      - finally/.github/workflows/ci.yml
      - finally/db/.gitkeep
      - finally/backend/db/schema.py
    qa_verify_command: 'test -f finally/planning/PLAN.md && test -f finally/scripts/start_mac.sh && test -f finally/scripts/stop_mac.sh && test -f finally/scripts/start_windows.ps1 && test -f finally/scripts/stop_windows.ps1 && test -f finally/.env && test -f finally/.gitignore && test -f finally/.github/workflows/ci.yml && test -f finally/db/.gitkeep && test -f finally/backend/db/schema.py'
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
    qa_verify_command: 'test -f finally/backend/app/api/__init__.py && test -f finally/backend/app/api/schemas.py && test -f finally/frontend/next-env.d.ts && test -f finally/backend/tests/test_market_infrastructure.py && PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py && (cd finally/frontend && npm run build)'
    depends_on: [project-foundation-support]
    file_dependencies:
      finally/backend/app/market/cache.py: [finally/backend/app/main.py]
      finally/backend/app/market/gbm.py: [finally/backend/app/main.py]
      finally/backend/app/market/massive.py: [finally/backend/app/main.py]
      finally/backend/app/market/sse.py: [finally/backend/app/main.py, finally/backend/app/market/cache.py]
      finally/backend/tests/test_market_infrastructure.py: [finally/backend/app/market/gbm.py, finally/backend/app/market/massive.py, finally/backend/app/market/cache.py, finally/backend/app/market/sse.py]
  - id: database-portfolio-engine
    title: Database & Portfolio Engine
    spec_focus: Database & Portfolio Engine
    required_files:
      - finally/backend/app/portfolio/engine.py
    qa_verify_command: 'PYTHONPATH=finally/backend python -c "from app.main import create_app; p={r.path for r in create_app().routes}; assert {\"/api/portfolio\", \"/api/portfolio/trade\", \"/api/portfolio/history\"} <= p"'
    depends_on: [core-market-infrastructure]
    file_dependencies:
      finally/backend/app/portfolio/engine.py: [finally/backend/db/schema.py, finally/backend/app/market/cache.py]
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
    qa_verify_command: 'test -f finally/frontend/components/Header.tsx && test -f finally/frontend/components/Sidebar.tsx && test -f finally/frontend/components/MarketOverview.tsx && test -f finally/frontend/components/Watchlist.tsx && test -f finally/frontend/components/PriceChart.tsx && test -f finally/test/watchlist-market-ui.spec.ts && (cd finally/frontend && npm run build)'
    depends_on: [database-portfolio-engine]
    file_dependencies:
      finally/frontend/components/Header.tsx: [finally/frontend/app/layout.tsx]
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
    qa_verify_command: 'test -f finally/frontend/components/PortfolioSummary.tsx && test -f finally/frontend/components/TradingPanel.tsx && test -f finally/test/portfolio-visualisation-trading.spec.ts && PYTHONPATH=finally/backend python -c "from app.main import create_app; assert any(r.path == \"/api/portfolio/trade\" for r in create_app().routes)" && (cd finally/frontend && npm run build)'
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
      - finally/backend/tests/test_chat.py
    qa_verify_command: 'test -f finally/frontend/components/ChatAssistant.tsx && test -f finally/frontend/components/ChatAssistant.test.tsx && test -f finally/backend/tests/test_chat.py && PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_chat.py && PYTHONPATH=finally/backend python -c "from app.main import create_app; assert any(r.path == \"/api/chat\" for r in create_app().routes)" && (cd finally/frontend && npm run build)'
    depends_on: [portfolio-visualisation-trading]
    file_dependencies:
      finally/frontend/components/ChatAssistant.tsx: [finally/frontend/app/page.tsx]
      finally/backend/tests/test_chat.py: [finally/backend/app/main.py, finally/backend/app/portfolio/engine.py]
  - id: application-polish
    title: Application Polish
    spec_focus: Application Polish
    required_files:
      - finally/frontend/app/polish.css
      - finally/test/application-polish.spec.ts
    qa_verify_command: 'test -f finally/frontend/app/polish.css && test -f finally/test/application-polish.spec.ts && (cd finally/frontend && npm run build)'
    depends_on: [ai-trading-assistant]
    file_dependencies:
      finally/frontend/app/polish.css: [finally/frontend/app/globals.css]
      finally/test/application-polish.spec.ts: [finally/frontend/app/polish.css]
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
      finally/test/docker-compose.test.yml: [finally/docker-compose.yml, finally/Dockerfile, finally/test/playwright.config.ts]
      finally/test/playwright.config.ts: [finally/test/e2e.spec.ts]
```

## Requirements

### project-foundation

The foundation delivers a buildable Next.js export, FastAPI factory and root/health behavior, Docker and compose runtime, planning document, and the explicit test `finally/backend/app/main_test.py`. Its test must assert `/api/health` succeeds and root content is the actual dashboard: heading, all ten required ticker symbols, and `$10,000`; it must reject missing export/error behavior rather than accept placeholder HTML. The production frontend build and foundation pytest command are the phase gate.

### project-foundation-support

Support files provide environment defaults, idempotent cross-platform lifecycle scripts, CI configuration, runtime `finally/db/` mount marker, and SQLite schema/seed initialization. The schema must be safe to initialize repeatedly and seed the exact user, watchlist, and cash specified by SPEC. The phase check confirms every declared support artifact exists after the foundation dependency.

### core-market-infrastructure

The market layer defines one provider shape implemented by GBM and Massive, chooses by `MASSIVE_API_KEY`, stores latest/previous/timestamp values in one cache, and drives a background task. SSE emits the specified fields at approximately the simulator cadence, while the frontend-facing protocol permits reconnect and status changes. `finally/backend/tests/test_market_infrastructure.py` verifies valid GBM prices, Massive parsing, provider interchangeability, cache behavior, and SSE event shape; the phase also runs a production frontend build.

### database-portfolio-engine

The engine and schema deliver lazy SQLite initialization, default data, fractional market orders, cash/share validation, average cost, unrealized P&L, history snapshots, and persistence. The exact portfolio route paths are registered and backed by the same engine used by manual and AI trades. Acceptance checks route registration plus executable engine behavior without moving UI scope into this phase.

### watchlist-market-ui

The market UI consumes the exact watchlist routes and EventSource path, renders the ten seeded symbols and prices, accumulates per-symbol sparkline points, selects the detailed chart, flashes green/red on direction, and exposes header connection status. Add/remove operations and duplicate handling are visible user flows. `finally/test/watchlist-market-ui.spec.ts` uses browser assertions for rendered symbols, updates, controls, and chart content; the production build is required.

### portfolio-visualisation-trading

The trading UI calls the exact trade route and displays validation errors, immediate cash/position changes, positions table, P&L values, heatmap rectangles colored by P&L, and history chart data. `finally/test/portfolio-visualisation-trading.spec.ts` covers buy, sell, insufficient cash, excessive sell, visual output, and snapshot behavior through the running application. The build and route check are both required.

### ai-trading-assistant

The backend and frontend implement the exact `/api/chat` complete JSON contract: message plus executed trades/watchlist changes. LiteLLM uses the specified OpenRouter/Cerebras model arrangement, structured output is validated, actions use engine validation, messages persist, provider errors recover, and `LLM_MOCK=true` is deterministic. `finally/backend/tests/test_chat.py` is the explicit backend test path for this phase, covering contract, mock repeatability, persistence, and rejected actions; `finally/frontend/components/ChatAssistant.test.tsx` covers loading and inline confirmations. The production build and route check gate delivery.

### application-polish

Polish applies the SPEC dark terminal palette, responsive layout, animations, loading/error/empty states, accessible labels, notifications, and streaming stability without changing route contracts. `finally/test/application-polish.spec.ts` checks real rendered styles and interaction states in a browser, and the production build proves the delivered stylesheet is included.

### testing-release

The release harness runs the complete app in the declared compose test environment with `LLM_MOCK=true`, healthchecks on `/api/health`, and Playwright on the required project. `finally/test/playwright.config.ts` defines the Docker-managed base URL, retries, timeout, Chromium project, and reporters; `finally/test/e2e.spec.ts` asserts real dashboard content and the required watchlist, trading, portfolio, chat, SSE, navigation, and happy-path behavior. The compose build/run command is the final gate and must preserve failure exit codes while cleaning containers.

## Unit tests

`finally/backend/tests/test_market_infrastructure.py` tests provider math, parsing, cache, and stream serialization. `finally/backend/app/main_test.py` tests foundation HTTP wiring and real static content. `finally/backend/tests/test_chat.py` tests structured chat parsing, mock determinism, persistence, and action validation. `finally/frontend/components/ChatAssistant.test.tsx` tests component rendering, loading, assistant messages, and action confirmations. Browser tests remain integration/UI tests and must assert content rather than status alone.

## Integration and testing

The dependency graph is executable: foundation precedes support, market infrastructure precedes the database engine, market UI precedes trading UI, and both precede chat, polish, and release. Each phase command checks all files it delivers and runs a relevant behavioral check; every phase that delivers frontend source runs `npm run build`. The full release command starts from a clean compose state, uses the real Dockerfile, sets deterministic mock mode, runs Playwright, and removes compose resources on completion. API assertions use the exact SPEC paths and request shapes; browser assertions use roles, text, or test IDs and never bless placeholder output.

## Docker & Deployment
The multi-stage image uses node:20-slim for the frontend build stage and python:3.12-slim for the runtime stage. The Node stage installs the dependencies from `finally/frontend/package.json`, runs the production export, and the Python stage copies the resulting `finally/frontend/out/` plus the backend sources and installs the Python requirements. The runtime exposes port 8000 and its Dockerfile instruction is CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]; compose publishes host port 8000 to container port 8000 and mounts the database directory.


`finally/Dockerfile` uses a Node build stage to produce the default static export at `finally/frontend/out/`, then a Python 3.12/uv runtime stage. It copies that exact export to the runtime location expected by `finally/backend/app/main.py`, exposes port 8000, and runs uvicorn. `finally/docker-compose.yml` provides the single application service, environment loading, port mapping, and persistent `finally/db/` volume. `finally/test/docker-compose.test.yml` builds from the `finally/` root via its compose-relative context, mounts the project for Playwright, sets `BASE_URL` and `LLM_MOCK=true`, checks `/api/health`, and runs the full test command.

## E2E / integration testing

The release tests cover first launch with all ten symbols and cash, live price changes and SSE reconnection, watchlist add/remove/duplicate behavior, market buy/sell and validation, portfolio table/heatmap/P&L chart, chat response and executed actions, selected ticker navigation, dark styling, and the full happy path. Tests must observe actual DOM content and changed values. The test harness remains under `finally/test/`; it is a required delivery artifact even though it orchestrates the production container.

## Acceptance mapping

The architecture satisfies the vision through one port and one container, real static dashboard serving, seeded SQLite state, live interchangeable market providers, SSE, manual simulated trading, portfolio visualizations, and structured AI actions. SPEC's visual requirements map to the frontend components and styles; its persistence and validation rules map to the schema and engine; its exact API table maps to route registration; and its mandatory testing strategy maps to explicit unit, component, browser, and Docker release artifacts. No later phase is pulled into foundation, and the foundation now has a concrete test file that directly proves its distinctive real-dashboard exit criterion.

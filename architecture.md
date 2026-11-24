# Architecture for testgt4
layout_root: finally

## Overview

FinAlly is a single-origin AI trading workstation. A static-exported Next.js frontend is built from `finally/frontend/` and served by FastAPI on port 8010. SQLite is lazily initialized at `finally/db/finally.db`, seeded with the ten SPEC tickers and $10,000 cash. The simulator is the default market provider; a non-empty MASSIVE_API_KEY selects Massive. LLM_MOCK=true supplies deterministic chat responses.

GET `/` reads `finally/frontend/out/index.html` and never emits placeholder HTML. If the export is absent it returns HTTP 503 with `{"error":"Frontend export unavailable"}`. The real dashboard contains the level-1 heading Trading dashboard and brand text FinAlly, ten tickers with prices, cash, portfolio, watchlist, chart, trading, and chat surfaces. Manual and AI trades share validation. Browser tests assert rendered content and state changes after real interactions.

## Planned file layout

Every implementation, configuration, test, harness, and marker file named by SPEC is listed exactly once as a repository path under the layout root:
- `finally/backend/app/main.py`
- `finally/backend/pyproject.toml`
- `finally/backend/uv.lock`
- `finally/frontend/package.json`
- `finally/frontend/tsconfig.json`
- `finally/frontend/next.config.js`
- `finally/frontend/app/layout.tsx`
- `finally/frontend/app/page.tsx`
- `finally/frontend/app/globals.css`
- `finally/Dockerfile`
- `finally/backend/app/main_test.py`
- `finally/planning/PLAN.md`
- `finally/scripts/start_mac.sh`
- `finally/scripts/stop_mac.sh`
- `finally/scripts/start_windows.ps1`
- `finally/scripts/stop_windows.ps1`
- `finally/frontend/next-env.d.ts`
- `finally/docker-compose.yml`
- `finally/.github/workflows/ci.yml`
- `finally/backend/app/api/__init__.py`
- `finally/backend/app/api/schemas.py`
- `finally/backend/app/market/sse.py`
- `finally/backend/app/market/cache.py`
- `finally/backend/app/market/massive.py`
- `finally/backend/app/market/gbm.py`
- `finally/backend/tests/test_market_infrastructure.py`
- `finally/.gitignore`
- `finally/backend/db/schema.py`
- `finally/backend/app/portfolio/engine.py`
- `finally/.env.example`
- `finally/.env`
- `finally/db/.gitkeep`
- `finally/test/package.json`
- `finally/test/api/helpers.ts`
- `finally/test/pages/dashboard.page.ts`
- `finally/test/specs/dashboard.spec.ts`
- `finally/test/fixtures/base.ts`
- `finally/frontend/lib/api.ts`
- `finally/frontend/lib/sse.ts`
- `finally/frontend/components/Header.tsx`
- `finally/frontend/components/Sidebar.tsx`
- `finally/frontend/components/MarketOverview.tsx`
- `finally/frontend/components/Watchlist.tsx`
- `finally/frontend/components/PriceChart.tsx`
- `finally/test/watchlist-market-ui.spec.ts`
- `finally/frontend/components/PortfolioSummary.tsx`
- `finally/frontend/components/PortfolioHeatmap.tsx`
- `finally/frontend/components/PnlChart.tsx`
- `finally/frontend/components/PositionsTable.tsx`
- `finally/frontend/components/TradingPanel.tsx`
- `finally/test/portfolio-visualisation-trading.spec.ts`
- `finally/test/pages/watchlist.page.ts`
- `finally/test/specs/watchlist.spec.ts`
- `finally/test/pages/trade.page.ts`
- `finally/test/specs/trading.spec.ts`
- `finally/backend/app/ai/llm.py`
- `finally/backend/app/ai/prompts.py`
- `finally/backend/app/ai/structured.py`
- `finally/frontend/components/ChatAssistant.tsx`
- `finally/frontend/components/ChatAssistant.test.tsx`
- `finally/backend/tests/test_chat.py`
- `finally/test/pages/portfolio.page.ts`
- `finally/test/specs/portfolio.spec.ts`
- `finally/test/pages/chat.page.ts`
- `finally/test/specs/chat.spec.ts`
- `finally/frontend/app/polish.css`
- `finally/frontend/tailwind.config.ts`
- `finally/frontend/postcss.config.js`
- `finally/test/application-polish.spec.ts`
- `finally/test/specs/sse.spec.ts`
- `finally/test/specs/navigation.spec.ts`
- `finally/test/specs/mvp.spec.ts`
- `finally/test/playwright.config.ts`
- `finally/test/e2e.spec.ts`
- `finally/test/docker-compose.test.yml`

## Module / bead ownership

`finally/backend/app/main.py` owns `create_app(...) -> FastAPI`, importable `app`, configuration, lazy database wiring, health, root export response, provider selection, and dependency assembly. `finally/backend/app/api/__init__.py` owns route registration; it provides the SPEC-required FastAPI factory; main.py delegates to it. `finally/backend/app/api/schemas.py` owns Pydantic request and response contracts.

`finally/backend/db/schema.py` owns idempotent DDL and seed rows. `finally/backend/app/market/gbm.py` and `finally/backend/app/market/massive.py` implement the shared provider interface. `finally/backend/app/market/cache.py` owns latest, previous, and timestamp state. `finally/backend/app/market/sse.py` owns SSE serialization and streaming. `finally/backend/app/portfolio/engine.py` owns watchlist, trades, positions, cash, P&L, snapshots, and persistence. `finally/backend/app/ai/llm.py`, `finally/backend/app/ai/prompts.py`, and `finally/backend/app/ai/structured.py` own provider calls, prompts, structured parsing, and action validation. Frontend libraries own same-origin HTTP and EventSource clients; components own their rendered surfaces and controls. Tests assert behavior and never define production behavior.

## HTTP + entrypoint integration

The backend launch command from SPEC is: `uvicorn app.main:app --host 0.0.0.0 --port 8010`.

The exact SPEC runtime command, run from the backend working directory, is:

    uvicorn app.main:app --host 0.0.0.0 --port 8010

The entrypoint parses configuration, lazily initializes SQLite, selects GBM or Massive, creates cache and portfolio services, registers routes, serves the export, and starts FastAPI. The root derives the frontend directory from `Path(__file__).resolve().parents[2] / "frontend"` and reads `frontend_root / "out" / "index.html"`.

The routes match SPEC exactly: GET `/api/stream/prices`; GET `/api/portfolio`; POST `/api/portfolio/trade` with `{ticker, quantity, side}`; GET `/api/portfolio/history`; GET and POST `/api/watchlist`; DELETE `/api/watchlist/{ticker}`; POST `/api/chat`; and GET /api/health. SSE events contain ticker, price, previous price, timestamp, and direction. No alias or convenience route is introduced.

## Delivery phases

```yaml
delivery_phases:
  - id: project-foundation
    title: Project Foundation
    spec_focus: Project Foundation
    required_files:
      - finally/backend/app/main.py
      - finally/backend/pyproject.toml
      - finally/backend/uv.lock
      - finally/frontend/package.json
      - finally/frontend/tsconfig.json
      - finally/frontend/next.config.js
      - finally/frontend/app/layout.tsx
      - finally/frontend/app/page.tsx
      - finally/frontend/app/globals.css
      - finally/Dockerfile
    qa_verify_command: 'test -f finally/backend/app/main.py && test -f finally/backend/pyproject.toml && test -f finally/backend/uv.lock && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && (cd finally/frontend && npm run build) && (cd finally/backend && uvicorn app.main:app --host 0.0.0.0 --port 8010 >/tmp/testgt4-foundation.log 2>&1 & pid=$!; trap "kill $pid" EXIT; sleep 2; curl -fsS http://127.0.0.1:8010/api/health && curl -fsS http://127.0.0.1:8010/ | grep -F "Trading dashboard" && curl -fsS http://127.0.0.1:8010/ | grep -F "FinAlly")'
    depends_on: []
    file_dependencies:
      finally/backend/app/main.py:
        - finally/backend/pyproject.toml
        - finally/frontend/app/page.tsx
      finally/frontend/app/layout.tsx:
        - finally/frontend/app/globals.css
      finally/frontend/app/page.tsx:
        - finally/frontend/app/layout.tsx
      finally/Dockerfile:
        - finally/backend/pyproject.toml
        - finally/backend/uv.lock
        - finally/frontend/package.json
        - finally/frontend/next.config.js
  - id: project-foundation-support
    title: Project Foundation Support
    spec_focus: Project Foundation
    required_files:
      - finally/backend/app/main_test.py
      - finally/backend/db/schema.py
      - finally/planning/PLAN.md
      - finally/scripts/start_mac.sh
      - finally/scripts/stop_mac.sh
      - finally/scripts/start_windows.ps1
      - finally/scripts/stop_windows.ps1
      - finally/.env
      - finally/frontend/next-env.d.ts
      - finally/docker-compose.yml
    qa_verify_command: '(cd finally/frontend && npm run build) && test -f finally/backend/app/main_test.py && test -f finally/backend/db/schema.py && test -f finally/planning/PLAN.md && test -f finally/scripts/start_mac.sh && test -f finally/scripts/stop_mac.sh && test -f finally/scripts/start_windows.ps1 && test -f finally/scripts/stop_windows.ps1 && test -f finally/.env && test -f finally/frontend/next-env.d.ts && test -f finally/docker-compose.yml && (cd finally/backend && pytest -q app/main_test.py)'
    depends_on:
      - project-foundation
    file_dependencies:
      finally/backend/app/main_test.py:
        - finally/backend/db/schema.py
        - finally/backend/app/main.py
      finally/backend/db/schema.py:
        - finally/backend/pyproject.toml
      finally/docker-compose.yml:
        - finally/Dockerfile
        - finally/backend/app/main.py
  - id: core-market-infrastructure
    title: Core Market Infrastructure
    spec_focus: Core Market Infrastructure
    required_files:
      - finally/backend/app/api/__init__.py
      - finally/backend/app/api/schemas.py
      - finally/backend/app/market/sse.py
      - finally/backend/app/market/cache.py
      - finally/backend/app/market/massive.py
      - finally/backend/app/market/gbm.py
      - finally/backend/tests/test_market_infrastructure.py
      - finally/.gitignore
    qa_verify_command: 'test -f finally/backend/app/api/__init__.py && test -f finally/backend/app/api/schemas.py && test -f finally/backend/app/market/sse.py && test -f finally/backend/app/market/cache.py && test -f finally/backend/app/market/massive.py && test -f finally/backend/app/market/gbm.py && test -f finally/backend/tests/test_market_infrastructure.py && test -f finally/.gitignore && (cd finally/frontend && npm run build) && (cd finally/backend && pytest -q tests/test_market_infrastructure.py)'
    depends_on:
      - project-foundation-support
    file_dependencies:
      finally/backend/app/api/__init__.py:
        - finally/backend/app/main.py
        - finally/backend/app/api/schemas.py
      finally/backend/app/market/cache.py:
        - finally/backend/app/market/gbm.py
        - finally/backend/app/market/massive.py
      finally/backend/app/market/sse.py:
        - finally/backend/app/market/cache.py
      finally/backend/tests/test_market_infrastructure.py:
        - finally/backend/app/market/sse.py
  - id: database-portfolio-engine
    title: Database & Portfolio Engine
    spec_focus: Database & Portfolio Engine
    required_files:
      - finally/backend/app/portfolio/engine.py
      - finally/.env.example
      - finally/db/.gitkeep
      - finally/test/package.json
      - finally/test/api/helpers.ts
      - finally/test/pages/dashboard.page.ts
      - finally/test/specs/dashboard.spec.ts
      - finally/test/fixtures/base.ts
    qa_verify_command: 'test -f finally/backend/app/portfolio/engine.py && test -f finally/.env.example && test -f finally/db/.gitkeep && test -f finally/test/package.json && test -f finally/test/api/helpers.ts && test -f finally/test/pages/dashboard.page.ts && test -f finally/test/specs/dashboard.spec.ts && test -f finally/test/fixtures/base.ts && (cd finally/backend && pytest -q tests/test_market_infrastructure.py app/main_test.py)'
    depends_on:
      - core-market-infrastructure
    file_dependencies:
      finally/backend/app/portfolio/engine.py:
        - finally/backend/db/schema.py
        - finally/backend/app/market/cache.py
      finally/test/api/helpers.ts:
        - finally/test/package.json
      finally/test/pages/dashboard.page.ts:
        - finally/test/fixtures/base.ts
  - id: watchlist-market-ui
    title: Watchlist & Market UI
    spec_focus: Watchlist & Market UI
    required_files:
      - finally/frontend/lib/api.ts
      - finally/frontend/lib/sse.ts
      - finally/frontend/components/Header.tsx
      - finally/frontend/components/Sidebar.tsx
      - finally/frontend/components/MarketOverview.tsx
      - finally/frontend/components/Watchlist.tsx
      - finally/frontend/components/PriceChart.tsx
      - finally/test/watchlist-market-ui.spec.ts
    qa_verify_command: 'test -f finally/frontend/lib/api.ts && test -f finally/frontend/lib/sse.ts && test -f finally/frontend/components/Header.tsx && test -f finally/frontend/components/Sidebar.tsx && test -f finally/frontend/components/MarketOverview.tsx && test -f finally/frontend/components/Watchlist.tsx && test -f finally/frontend/components/PriceChart.tsx && test -f finally/test/watchlist-market-ui.spec.ts && (cd finally/frontend && npm run build)'
    depends_on:
      - database-portfolio-engine
    file_dependencies:
      finally/frontend/components/Watchlist.tsx:
        - finally/frontend/lib/api.ts
        - finally/frontend/lib/sse.ts
      finally/frontend/components/PriceChart.tsx:
        - finally/frontend/lib/sse.ts
      finally/test/watchlist-market-ui.spec.ts:
        - finally/frontend/components/Watchlist.tsx
  - id: portfolio-visualisation-trading
    title: Portfolio Visualisation & Trading
    spec_focus: Portfolio Visualisation & Trading
    required_files:
      - finally/frontend/components/PortfolioSummary.tsx
      - finally/frontend/components/PortfolioHeatmap.tsx
      - finally/frontend/components/PnlChart.tsx
      - finally/frontend/components/PositionsTable.tsx
      - finally/frontend/components/TradingPanel.tsx
      - finally/test/portfolio-visualisation-trading.spec.ts
      - finally/test/pages/watchlist.page.ts
      - finally/test/specs/watchlist.spec.ts
      - finally/test/pages/trade.page.ts
      - finally/test/specs/trading.spec.ts
    qa_verify_command: 'test -f finally/frontend/components/PortfolioSummary.tsx && test -f finally/frontend/components/PortfolioHeatmap.tsx && test -f finally/frontend/components/PnlChart.tsx && test -f finally/frontend/components/PositionsTable.tsx && test -f finally/frontend/components/TradingPanel.tsx && test -f finally/test/portfolio-visualisation-trading.spec.ts && test -f finally/test/pages/watchlist.page.ts && test -f finally/test/specs/watchlist.spec.ts && test -f finally/test/pages/trade.page.ts && test -f finally/test/specs/trading.spec.ts && (cd finally/frontend && npm run build)'
    depends_on:
      - watchlist-market-ui
    file_dependencies:
      finally/test/portfolio-visualisation-trading.spec.ts:
        - finally/frontend/components/TradingPanel.tsx
  - id: ai-trading-assistant
    title: AI Trading Assistant
    spec_focus: AI Trading Assistant
    required_files:
      - finally/backend/app/ai/llm.py
      - finally/backend/app/ai/prompts.py
      - finally/backend/app/ai/structured.py
      - finally/frontend/components/ChatAssistant.tsx
      - finally/frontend/components/ChatAssistant.test.tsx
      - finally/backend/tests/test_chat.py
      - finally/test/pages/portfolio.page.ts
      - finally/test/specs/portfolio.spec.ts
      - finally/test/pages/chat.page.ts
      - finally/test/specs/chat.spec.ts
    qa_verify_command: '(cd finally/frontend && npm run build) && test -f finally/backend/app/ai/llm.py && test -f finally/backend/app/ai/prompts.py && test -f finally/backend/app/ai/structured.py && test -f finally/frontend/components/ChatAssistant.tsx && test -f finally/frontend/components/ChatAssistant.test.tsx && test -f finally/backend/tests/test_chat.py && test -f finally/test/pages/portfolio.page.ts && test -f finally/test/specs/portfolio.spec.ts && test -f finally/test/pages/chat.page.ts && test -f finally/test/specs/chat.spec.ts && (cd finally/backend && pytest -q tests/test_chat.py)'
    depends_on:
      - portfolio-visualisation-trading
    file_dependencies:
      finally/backend/app/ai/llm.py:
        - finally/backend/pyproject.toml
      finally/backend/app/ai/prompts.py:
        - finally/backend/app/ai/structured.py
      finally/backend/tests/test_chat.py:
        - finally/backend/app/ai/structured.py
        - finally/backend/app/portfolio/engine.py
  - id: application-polish
    title: Application Polish
    spec_focus: Application Polish
    required_files:
      - finally/frontend/app/polish.css
      - finally/frontend/tailwind.config.ts
      - finally/frontend/postcss.config.js
      - finally/test/application-polish.spec.ts
      - finally/test/specs/sse.spec.ts
      - finally/test/specs/navigation.spec.ts
      - finally/test/specs/mvp.spec.ts
    qa_verify_command: 'test -f finally/frontend/app/polish.css && test -f finally/frontend/tailwind.config.ts && test -f finally/frontend/postcss.config.js && test -f finally/test/application-polish.spec.ts && test -f finally/test/specs/sse.spec.ts && test -f finally/test/specs/navigation.spec.ts && test -f finally/test/specs/mvp.spec.ts && (cd finally/frontend && npm run build)'
    depends_on:
      - ai-trading-assistant
    file_dependencies:
      finally/frontend/app/polish.css:
        - finally/frontend/app/globals.css
      finally/frontend/postcss.config.js:
        - finally/frontend/tailwind.config.ts
  - id: testing-release
    title: Testing & Release
    spec_focus: Testing & Release
    required_files:
      - finally/test/playwright.config.ts
      - finally/test/e2e.spec.ts
      - finally/test/docker-compose.test.yml
      - finally/.github/workflows/ci.yml
    qa_verify_command: 'test -f finally/test/playwright.config.ts && test -f finally/test/e2e.spec.ts && test -f finally/test/docker-compose.test.yml && test -f finally/.github/workflows/ci.yml && (cd /app/test cd finally/test && npm installcd finally/test && npm install npm install && npx playwright test --project=chromium)'
    depends_on:
      - application-polish
    file_dependencies:
      finally/test/playwright.config.ts:
        - finally/test/package.json
      finally/test/e2e.spec.ts:
        - finally/test/playwright.config.ts
      finally/test/docker-compose.test.yml:
        - finally/Dockerfile
        - finally/docker-compose.yml
```

## Requirements

### project-foundation

Deliver the runnable Next static export and FastAPI skeleton, uv metadata, Docker stages, and real health/root behavior. The gate builds the frontend, launches FastAPI with the exact SPEC command, probes /api/health, and asserts real dashboard content rather than placeholder HTML.

### project-foundation-support

Own SQLite initialization and support artifacts. `finally/backend/db/schema.py` creates the directory, idempotent schema, seed cash, and ten ticker rows; `finally/backend/app/main_test.py` verifies initialization, health, real export content, and missing-export 503 behavior. Scripts, environment files, Compose, planning, and the frontend type declaration are verified in the same gate.

### core-market-infrastructure

Deliver route registration, exact schemas, interchangeable GBM and Massive providers, environment selection, cache, background updates, SSE serialization, and infrastructure tests. GET `/api/stream/prices` emits ticker, price, previous price, timestamp, and direction.

### database-portfolio-engine

Consume the initialized database and the CI workflow, then deliver persistent portfolio calculations, watchlist and trade behavior, cash and positions, validation, snapshots, and dashboard E2E foundations. Market orders execute at current prices with no fees. The pytest gate exercises portfolio behavior in addition to infrastructure.

### watchlist-market-ui

Deliver typed REST and EventSource clients, live CRUD, progressive sparklines, selected-ticker charting, price flashes, connection status, and responsive layout. The frontend build and real interaction assertions are mandatory.

### portfolio-visualisation-trading

Deliver summary, meaningful treemap heatmap, P&L chart, positions table, and manual market-order controls. Browser actions prove cash and position changes and visualizations reflect current data.

### ai-trading-assistant

Deliver LiteLLM through OpenRouter using openrouter/openai/gpt-oss-120b with Cerebras inference, structured parsing, context prompts, deterministic mock mode, persistence, recovery, and engine-validated trades and watchlist actions.

### application-polish

Deliver dark terminal styling, Tailwind/PostCSS configuration, animations, loading/error/empty states, responsive accessibility improvements, and stable SSE rendering. The production frontend build is required.

### testing-release

Deliver Page Objects, complete Playwright coverage, Docker test harness, mocked LLM execution, healthchecks, SSE reconnection, and the full happy path. The harness uses build context `..`, mounts `..:/app`, sets LLM_MOCK=true, and runs `cd /app/test && npm install && npx playwright test --project=chromium`.

## Unit tests

`finally/backend/app/main_test.py` verifies factory behavior, health, real root export, ten tickers, $10,000, and the exact missing-export response. `finally/backend/tests/test_market_infrastructure.py` verifies GBM, Massive parsing, provider interchangeability, cache state, and SSE serialization. `finally/backend/tests/test_chat.py` verifies structured parsing, deterministic mock output, persistence, recovery, and action validation. `finally/frontend/components/ChatAssistant.test.tsx` verifies chat rendering and loading. Tests assert behavior and are written before the corresponding implementation.

## Integration and testing

Each phase gate checks every concrete file it owns. Every phase delivering frontend files runs `(cd finally/frontend && npm run build)`. Backend gates run named pytest files from `finally/backend`; release runs the exact Playwright command from `finally/test`. Browser tests use Page Objects and role, text, or test-id assertions, prove seeded content and prices, and assert changed DOM or API state after real click, type, or submit interactions. Cleanup preserves the original failure status.

## Docker & Deployment

Stage 1 is the Node build stage based on `node:20-slim`. It copies the project in `finally/frontend/`, installs dependencies from `finally/frontend/package.json`, and runs `npm install && npm run build`, producing `finally/frontend/out/`. Stage 2 is the Python runtime stage based on `python:3.12-slim`. It installs uv, copies `finally/backend/`, runs `uv sync --frozen` using `finally/backend/uv.lock`, and consumes the Stage 1 artifact with COPY --from=frontend /frontend/out /app/frontend/out. This is the explicit `finally/frontend/out/` handoff; the stages are not independent. Stage 2 exposes port 8010 and starts exactly with `uvicorn app.main:app --host 0.0.0.0 --port 8010`. The named volume command is `docker run -v finally-data:/app/db -p 8010:8010 --env-file finally/.env finally`.

## E2E / integration testing

`finally/test/docker-compose.test.yml` uses the real `finally/Dockerfile` with build context `..`; the Playwright service mounts `..:/app`, sets BASE_URL and LLM_MOCK=true, waits on /api/health, and runs `cd /app/test && npm install && npx playwright test --project=chromium`. Scenarios cover the dashboard, all ten tickers, prices, watchlist CRUD, trade validation and cash changes, heatmap, P&L chart, positions, chat actions, SSE reconnection, navigation, and the full happy path. Every interactive scenario proves a state change.

## Acceptance mapping

The design maps every SPEC goal to an owned file and executable phase gate: static same-origin serving and missing-export failure, exact REST and SSE routes, seeded SQLite, provider abstraction, portfolio persistence, manual and AI trading, structured mockable chat, terminal UI, two-stage Docker deployment, and mandatory Playwright coverage. All nine canonical phase IDs appear once, all required files are concrete and prefixed with `finally/`, dependencies are acyclic, frontend phases have build gates, and unrelated phase contracts remain preserved.

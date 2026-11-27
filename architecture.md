# Architecture for test4

## Overview

FinAlly is a single-origin, single-container AI trading workstation. A FastAPI app (Python, uv-managed) serves the REST API under /api/*, the SSE price stream under /api/stream/*, and the statically exported Next.js dashboard at /. State lives in one SQLite file at `finally/db/finally.db`, volume-mounted for persistence. One in-process background task produces prices (GBM simulator by default; Massive REST polling when MASSIVE_API_KEY is non-empty) and writes them to a shared in-memory price cache that SSE clients read. Portfolio snapshots are recorded every 30 seconds and after each trade. Chat goes through LiteLLM to OpenRouter (Cerebras inference), or to a deterministic mock when LLM_MOCK=true.

Constraints from SPEC:

- One port (8010), one container, one origin. No CORS.
- Market orders only: instant fill at the cached price, no fees, no confirmation.
- Single user (user_id "default"); every table carries a user_id column.
- GET / renders the real dashboard: FinAlly heading, ten default tickers with prices, $10,000 cash. No placeholder page. If the export is missing, GET / returns 503 with a diagnostic body.
- LLM output passes a resilient multi-key parser; raw JSON never reaches a chat bubble.
- Every LLM prompt embeds live prices, for example AAPL ($190.50).

## Planned file layout

The layout root is `finally`. Every path carries the `finally/` prefix.

Root and deployment: `finally/Dockerfile`, `finally/docker-compose.yml`, `finally/.env`, `finally/.gitignore`, `finally/db/.gitkeep`, `finally/scripts/start_mac.sh`, `finally/scripts/stop_mac.sh`, `finally/scripts/start_windows.ps1`, `finally/scripts/stop_windows.ps1`, `finally/planning/PLAN.md`.

Backend (uv project): `finally/backend/pyproject.toml`, `finally/backend/app/main.py`, `finally/backend/app/api/__init__.py`, `finally/backend/app/api/schemas.py`, `finally/backend/app/api/routes_portfolio.py`, `finally/backend/app/api/routes_watchlist.py`, `finally/backend/app/api/routes_chat.py`, `finally/backend/app/db/__init__.py`, `finally/backend/app/db/schema.sql`, `finally/backend/app/db/seed.py`, `finally/backend/app/db/connection.py`, `finally/backend/app/market/__init__.py`, `finally/backend/app/market/base.py`, `finally/backend/app/market/simulator.py`, `finally/backend/app/market/massive_client.py`, `finally/backend/app/market/cache.py`, `finally/backend/app/market/stream.py`, `finally/backend/app/market/poller.py`, `finally/backend/app/portfolio/__init__.py`, `finally/backend/app/portfolio/repository.py`, `finally/backend/app/portfolio/engine.py`, `finally/backend/app/portfolio/snapshots.py`, `finally/backend/app/llm/__init__.py`, `finally/backend/app/llm/client.py`, `finally/backend/app/llm/prompts.py`, `finally/backend/app/llm/parser.py`, `finally/backend/app/llm/chat_service.py`, `finally/backend/tests/test_market.py`, `finally/backend/tests/test_portfolio.py`, `finally/backend/tests/test_portfolio_api.py`, `finally/backend/tests/test_watchlist_api.py`, `finally/backend/tests/test_llm.py`, `finally/backend/tests/test_api.py`, `finally/backend/tests/test_health.py`, `finally/backend/tests/test_schema.py`, `finally/backend/tests/test_trading_flow.py`.

Frontend (Next.js static export to `finally/frontend/out/`): `finally/frontend/package.json`, `finally/frontend/tsconfig.json`, `finally/frontend/next.config.js`, `finally/frontend/next-env.d.ts`, `finally/frontend/app/layout.tsx`, `finally/frontend/app/page.tsx`, `finally/frontend/app/globals.css`, `finally/frontend/app/polish.css`, `finally/frontend/components/Header.tsx`, `finally/frontend/components/Sidebar.tsx`, `finally/frontend/components/MarketOverview.tsx`, `finally/frontend/components/Watchlist.tsx`, `finally/frontend/components/PriceChart.tsx`, `finally/frontend/components/PortfolioSummary.tsx`, `finally/frontend/components/TradingPanel.tsx`, `finally/frontend/components/PositionsTable.tsx`, `finally/frontend/components/PnlChart.tsx`, `finally/frontend/components/PortfolioHeatmap.tsx`, `finally/frontend/components/ChatAssistant.tsx`, `finally/frontend/components/ChatAssistant.test.tsx`.

E2E harness: `finally/test/package.json`, `finally/test/playwright.config.ts`, `finally/test/docker-compose.test.yml`, `finally/test/e2e.spec.ts`, plus the SPEC Section 13 harness files: `finally/test/specs/dashboard.spec.ts`, `finally/test/specs/watchlist.spec.ts`, `finally/test/specs/trading.spec.ts`, `finally/test/specs/portfolio.spec.ts`, `finally/test/specs/chat.spec.ts`, `finally/test/specs/sse.spec.ts`, `finally/test/specs/navigation.spec.ts`, `finally/test/specs/mvp.spec.ts`, `finally/test/pages/dashboard.page.ts`, `finally/test/pages/watchlist.page.ts`, `finally/test/pages/trade.page.ts`, `finally/test/pages/portfolio.page.ts`, `finally/test/pages/chat.page.ts`, `finally/test/fixtures/base.ts`, `finally/test/api/helpers.ts`.

Generated tool outputs, not hand-written (`finally/backend/uv.lock` is written by `uv sync` and is owned by core-market-infrastructure per the delivery contract; the npm lockfile is an install side effect of the `npm install --ignore-scripts` step in project-foundation-support's gate; it is verified there, is not a declared deliverable, and has no separate phase owner): `finally/backend/uv.lock`, `finally/frontend/out/`. `finally/frontend/next-env.d.ts` is also written by the Next.js build and is a declared required deliverable owned solely by project-foundation-support.

## Module / bead ownership

| File | Owns | Must not define |
|---|---|---|
| `finally/backend/app/main.py` | `def create_app(...) -> FastAPI`, lifespan wiring, GET / static route | route bodies, SQL |
| `finally/backend/app/market/base.py` | abstract `MarketDataSource` (`start`, `stop`, `get_price`, `subscribe`) | concrete providers |
| `finally/backend/app/market/cache.py` | `PriceCache` (latest, previous, timestamp per ticker) | network calls |
| `finally/backend/app/market/stream.py` | SSE generator for GET /api/stream/prices | price generation |
| `finally/backend/app/portfolio/engine.py` | `execute_trade(ticker, quantity, side)` validation and fills | HTTP types |
| `finally/backend/app/llm/parser.py` | `parse_llm_reply(raw: str)` multi-key extraction | LLM network calls |

## HTTP + entrypoint integration

Routes match SPEC Section 8 verbatim:

- GET /api/stream/prices (alias /api/stream): SSE price stream
- GET /api/portfolio
- POST /api/portfolio/trade with body `{ticker, quantity, side}`
- GET /api/portfolio/history
- GET /api/watchlist
- POST /api/watchlist with body `{ticker}`
- DELETE /api/watchlist/{ticker}
- POST /api/chat
- GET /api/health

Entrypoint order in `finally/backend/app/main.py`: read environment (existing shell variables are never overwritten by `.env`); open `finally/db/finally.db`; run lazy schema creation and seeding; create the repository and price cache; start the market background task; register routers and the SSE route; mount static serving of `finally/frontend/out/`; serve on port 8010 with `uvicorn app.main:app --host 0.0.0.0 --port 8010`.
Runtime launch command (SPEC Section 11, verbatim):
`uvicorn app.main:app --host 0.0.0.0 --port 8010`

## Delivery phases

The YAML block below is the single canonical contract. Phase IDs match SPEC Section 14.2.

```yaml
delivery_phases:
  - id: project-foundation
    title: Project Foundation
    spec_focus: Project Foundation
    required_files:
      - finally/backend/pyproject.toml
      - finally/backend/app/main.py
      - finally/backend/app/api/__init__.py
      - finally/backend/tests/test_health.py
      - finally/frontend/package.json
      - finally/frontend/tsconfig.json
      - finally/frontend/next.config.js
      - finally/frontend/app/layout.tsx
      - finally/frontend/app/page.tsx
      - finally/frontend/app/globals.css
    qa_verify_command: 'test -f finally/backend/app/main.py && test -f finally/backend/app/api/__init__.py && test -f finally/backend/tests/test_health.py && (cd finally/backend && uv sync && uv run python -c "import app.main") && (cd finally/backend && uv run pytest tests/test_health.py -q) && (cd finally/frontend && npm install --ignore-scripts) && (cd finally/frontend && npm run build) && test -f finally/frontend/out/index.html'
    depends_on: []
  - id: project-foundation-support
    title: Project Foundation Support
    spec_focus: Project Foundation
    required_files:
      - finally/backend/app/db/schema.sql
      - finally/backend/app/db/seed.py
      - finally/backend/tests/test_schema.py
      - finally/frontend/next-env.d.ts
      - finally/Dockerfile
      - finally/docker-compose.yml
      - finally/.env
      - finally/scripts/start_mac.sh
      - finally/scripts/stop_mac.sh
      - finally/db/.gitkeep
    qa_verify_command: 'test -f finally/backend/app/db/schema.sql && test -f finally/backend/app/db/seed.py && (cd finally/frontend && npm install --ignore-scripts) && test -f finally/frontend/package-lock.json && (cd finally/frontend && npm run build) && test -f finally/frontend/out/index.html && test -f finally/frontend/next-env.d.ts && (cd finally/backend && uv run pytest tests/test_schema.py -q) && test -f finally/Dockerfile'
    depends_on: [project-foundation]
    file_dependencies:
      finally/Dockerfile: [finally/frontend/package.json, finally/frontend/tsconfig.json, finally/frontend/next.config.js, finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx, finally/frontend/app/globals.css, finally/backend/pyproject.toml, finally/backend/app/main.py]

  - id: core-market-infrastructure
    title: Core Market Infrastructure
    spec_focus: Core Market Infrastructure
    required_files:
      - finally/backend/app/market/__init__.py
      - finally/backend/app/market/base.py
      - finally/backend/app/market/simulator.py
      - finally/backend/app/market/massive_client.py
      - finally/backend/app/market/cache.py
      - finally/backend/app/market/stream.py
      - finally/backend/app/market/poller.py
      - finally/backend/tests/test_market.py
      - finally/backend/uv.lock
    qa_verify_command: 'test -f finally/backend/app/market/base.py && test -f finally/backend/app/market/simulator.py && test -f finally/backend/app/market/massive_client.py && test -f finally/backend/app/market/cache.py && test -f finally/backend/app/market/stream.py && test -f finally/backend/app/market/poller.py && test -f finally/backend/uv.lock && (cd finally/backend && uv run pytest tests/test_market.py -q)'
    depends_on: [project-foundation-support]
  - id: database-portfolio-engine
    title: Database & Portfolio Engine
    spec_focus: Database & Portfolio Engine
    required_files:
      - finally/backend/app/db/__init__.py
      - finally/backend/app/db/connection.py
      - finally/backend/app/portfolio/__init__.py
      - finally/backend/app/portfolio/repository.py
      - finally/backend/app/portfolio/engine.py
      - finally/backend/app/portfolio/snapshots.py
      - finally/backend/app/api/schemas.py
      - finally/backend/app/api/routes_portfolio.py
      - finally/backend/tests/test_portfolio.py
      - finally/backend/tests/test_portfolio_api.py
    qa_verify_command: 'test -f finally/backend/app/db/connection.py && test -f finally/backend/app/portfolio/repository.py && test -f finally/backend/app/portfolio/engine.py && test -f finally/backend/app/portfolio/snapshots.py && test -f finally/backend/app/api/schemas.py && test -f finally/backend/app/api/routes_portfolio.py && (cd finally/backend && uv run pytest tests/test_portfolio.py tests/test_portfolio_api.py -q)'
    depends_on: [core-market-infrastructure]
  - id: watchlist-market-ui
    title: Watchlist & Market UI
    spec_focus: Watchlist & Market UI
    required_files:
      - finally/backend/app/api/routes_watchlist.py
      - finally/backend/tests/test_watchlist_api.py
      - finally/frontend/components/Header.tsx
      - finally/frontend/components/Sidebar.tsx
      - finally/frontend/components/MarketOverview.tsx
      - finally/frontend/components/Watchlist.tsx
      - finally/frontend/components/PriceChart.tsx
      - finally/test/pages/watchlist.page.ts
      - finally/test/specs/watchlist.spec.ts
      - finally/test/package.json
    qa_verify_command: 'test -f finally/backend/app/api/routes_watchlist.py && test -f finally/test/package.json && test -f finally/frontend/components/Header.tsx && test -f finally/frontend/components/Sidebar.tsx && test -f finally/frontend/components/MarketOverview.tsx && test -f finally/frontend/components/Watchlist.tsx && test -f finally/frontend/components/PriceChart.tsx && (cd finally/backend && uv run pytest tests/test_watchlist_api.py -q) && (cd finally/frontend && npm run build)'
    depends_on: [database-portfolio-engine]
  - id: portfolio-visualisation-trading
    title: Portfolio Visualisation & Trading
    spec_focus: Portfolio Visualisation & Trading
    required_files:
      - finally/frontend/components/PortfolioSummary.tsx
      - finally/frontend/components/TradingPanel.tsx
      - finally/frontend/components/PositionsTable.tsx
      - finally/frontend/components/PnlChart.tsx
      - finally/frontend/components/PortfolioHeatmap.tsx
      - finally/backend/tests/test_trading_flow.py
      - finally/test/pages/trade.page.ts
      - finally/test/pages/portfolio.page.ts
      - finally/test/specs/trading.spec.ts
      - finally/test/specs/portfolio.spec.ts
    qa_verify_command: 'test -f finally/frontend/components/PortfolioSummary.tsx && test -f finally/frontend/components/TradingPanel.tsx && test -f finally/frontend/components/PositionsTable.tsx && test -f finally/frontend/components/PnlChart.tsx && test -f finally/frontend/components/PortfolioHeatmap.tsx && test -f finally/backend/tests/test_trading_flow.py && (cd finally/backend && uv run pytest tests/test_portfolio_api.py tests/test_trading_flow.py -q) && (cd finally/frontend && npm run build)'
    depends_on: [database-portfolio-engine, watchlist-market-ui]
  - id: ai-trading-assistant
    title: AI Trading Assistant
    spec_focus: AI Trading Assistant
    required_files:
      - finally/backend/app/llm/__init__.py
      - finally/backend/app/llm/client.py
      - finally/backend/app/llm/prompts.py
      - finally/backend/app/llm/parser.py
      - finally/backend/app/llm/chat_service.py
      - finally/backend/app/api/routes_chat.py
      - finally/backend/tests/test_llm.py
      - finally/frontend/components/ChatAssistant.tsx
      - finally/frontend/components/ChatAssistant.test.tsx
      - finally/test/pages/chat.page.ts
    qa_verify_command: 'test -f finally/backend/app/llm/client.py && test -f finally/backend/app/llm/prompts.py && test -f finally/backend/app/llm/parser.py && test -f finally/backend/app/llm/chat_service.py && test -f finally/backend/app/api/routes_chat.py && test -f finally/frontend/components/ChatAssistant.tsx && test -f finally/frontend/components/ChatAssistant.test.tsx && (cd finally/backend && LLM_MOCK=true uv run pytest tests/test_llm.py -q) && (cd finally/frontend && npm run build)'
    depends_on: [portfolio-visualisation-trading]
  - id: application-polish
    title: Application Polish
    spec_focus: Application Polish
    required_files:
      - finally/frontend/app/polish.css
      - finally/.gitignore
      - finally/frontend/app/page.tsx
      - finally/scripts/start_windows.ps1
      - finally/scripts/stop_windows.ps1
      - finally/test/specs/chat.spec.ts
      - finally/test/specs/sse.spec.ts
      - finally/test/specs/navigation.spec.ts
      - finally/test/specs/mvp.spec.ts
    qa_verify_command: 'test -f finally/scripts/start_windows.ps1 && test -f finally/scripts/stop_windows.ps1 && test -f finally/.gitignore && test -f finally/frontend/app/polish.css && (for c in Header Watchlist MarketOverview PriceChart PortfolioSummary PositionsTable TradingPanel ChatAssistant; do grep -q "<$c" finally/frontend/app/page.tsx || exit 1; done) && (cd finally/frontend && npm run build)'
    depends_on: [ai-trading-assistant]
    file_dependencies:
      finally/frontend/app/page.tsx: [finally/frontend/components/Header.tsx, finally/frontend/components/Watchlist.tsx, finally/frontend/components/MarketOverview.tsx, finally/frontend/components/PriceChart.tsx, finally/frontend/components/PortfolioSummary.tsx, finally/frontend/components/PositionsTable.tsx, finally/frontend/components/TradingPanel.tsx, finally/frontend/components/ChatAssistant.tsx]


  - id: testing-release
    title: Testing & Release
    spec_focus: Testing & Release
    required_files:
      - finally/planning/PLAN.md
      - finally/test/playwright.config.ts
      - finally/test/docker-compose.test.yml
      - finally/test/pages/dashboard.page.ts
      - finally/test/fixtures/base.ts
      - finally/test/api/helpers.ts
      - finally/backend/tests/test_api.py
      - finally/test/e2e.spec.ts
      - finally/test/specs/dashboard.spec.ts
    qa_verify_command: "test -f finally/planning/PLAN.md && test -f finally/Dockerfile && (cd finally && docker build -f Dockerfile -t finally-foundation-check .) && (cd finally/backend && uv run pytest -q) && (cd finally/test && npm install --ignore-scripts && npx playwright test --project=chromium)"
    depends_on: [application-polish]

## Requirements

Each canonical phase ID from SPEC Section 14.2 has a requirement subsection below. These IDs match the `delivery_phases` YAML block exactly and are the only requirement IDs used by downstream test plans.

### project-foundation
Runnable skeleton: uv-managed FastAPI app imports cleanly, `GET /api/health` responds, Next.js static export builds to `finally/frontend/out/index.html`, and `GET /` serves the real dashboard shell rather than a placeholder.

### project-foundation-support
SQLite schema and seed scripts exist; the npm lockfile is produced by the install step; `finally/frontend/next-env.d.ts` is generated; the Dockerfile, docker compose file, `.env`, start/stop scripts for macOS and the database directory placeholder exist; schema tests pass.

### core-market-infrastructure
One abstract market data interface; GBM simulator produces positive prices; Massive REST parsing maps to the same tick format; provider is selected by MASSIVE_API_KEY (empty selects the simulator); shared price cache; SSE stream emits named `event: price` frames plus `data:` lines; `finally/backend/uv.lock` is produced by `uv sync`.

### database-portfolio-engine
Buys and sells update cash and positions; selling more than owned and buying with insufficient cash are rejected without changing state; average cost is recalculated on repeated buys; a portfolio snapshot is recorded after each accepted trade; GET /api/portfolio and POST /api/portfolio/trade match SPEC Section 8.

### watchlist-market-ui
Watchlist routes match SPEC Section 8 (GET /api/watchlist, POST /api/watchlist with body `{ticker}`, DELETE /api/watchlist/{ticker}); the ten seeded tickers are returned; duplicates are rejected; the dashboard shell mounts Header, Sidebar, MarketOverview, Watchlist and PriceChart with live prices and add/remove controls.

### portfolio-visualisation-trading
Trades through the trade route change cash, positions and total valuation; GET /api/portfolio/history returns snapshots; PortfolioSummary, TradingPanel, PositionsTable, PnlChart and PortfolioHeatmap render from live portfolio data; the trade bar enforces validation and shows errors.

### ai-trading-assistant
POST /api/chat returns the complete JSON response (message plus executed actions); the resilient parser accepts the reply, response, message, content, action, error and suggestion keys; trades from chat auto-execute with the same validation as manual trades; prompts embed live watchlist prices such as AAPL ($190.50); LLM_MOCK=true is deterministic; ChatAssistant renders bubbles, a thinking state, trade badges and never shows raw JSON.

### application-polish
page.tsx composes Header, Watchlist, MarketOverview, PriceChart, PortfolioSummary, PositionsTable, TradingPanel and ChatAssistant simultaneously; polish.css, start/stop Windows scripts and `.gitignore` exist; the production build succeeds; the chat, SSE, navigation and MVP E2E specs exist.

### testing-release
Backend pytest suite including the API contract test for every SPEC Section 8 route; Playwright E2E executes in a real browser against the running server with real click, submit and type interactions followed by DOM or API state-change assertions; the Docker image builds from the planning-backed Dockerfile; no test asserts placeholder text.

## Unit tests

Backend (pytest, run from `finally/backend`):
- Market: `finally/backend/tests/test_market.py` covers positive GBM ticks, Massive REST parsing into the common tick record, provider selection by MASSIVE_API_KEY, PriceCache replacement semantics, and the SSE named-event frame.
- Portfolio: `finally/backend/tests/test_portfolio.py` covers buy and sell arithmetic, average cost, oversell and insufficient-cash rejection with unchanged state, and snapshot recording after an accepted trade.
- Portfolio API: `finally/backend/tests/test_portfolio_api.py` covers the response shapes of GET /api/portfolio, POST /api/portfolio/trade and GET /api/portfolio/history.
- Watchlist API: `finally/backend/tests/test_watchlist_api.py` covers the ten seeded tickers, add, duplicate rejection and removal.
- Trading flow: `finally/backend/tests/test_trading_flow.py` covers buy then partial sell through the route and total_value equal to cash plus market value.
- LLM: `finally/backend/tests/test_llm.py` covers each reply-key variant, action-JSON to confirmation conversion, malformed and empty output fallback, prompt price embedding and mock determinism.
- Schema and health: `finally/backend/tests/test_schema.py` and `finally/backend/tests/test_health.py`.
- API contract: `finally/backend/tests/test_api.py` asserts every SPEC Section 8 route returns the documented keys and types, and that GET / returns the real dashboard content.

Frontend (component tests):
- `finally/frontend/components/ChatAssistant.test.tsx` covers the thinking indicator, bubble text with no braces, trade badge text and unwrapping of stringified JSON.

## Integration and testing

Backend integration runs through the FastAPI app created by `create_app` in `finally/backend/app/main.py`. Route tests use the real repository against a temporary SQLite file under `finally/db/`. The full backend suite is `(cd finally/backend && uv run pytest -q)`. The LLM suite runs with `LLM_MOCK=true`. Frontend production build is `(cd finally/frontend && npm run build)`, and the static export must contain `finally/frontend/out/index.html`.

## Docker & Deployment

The Dockerfile at `finally/Dockerfile` is a two-stage build with an explicit handoff:

- Stage 1 (Node build) uses the base image `node:20-slim`. It copies `finally/frontend`, installs dependencies declared in `finally/frontend/package.json`, and runs the production build with `output: "export"`. The static export is written to `finally/frontend/out/`.
- Stage 2 (Python runtime) uses the base image `python:3.12-slim`. It installs uv, copies `finally/backend`, runs `uv sync` against the lockfile, and copies the Stage 1 artifact `finally/frontend/out/` into `/app/frontend/out` with `COPY --from=frontend`. The stages are not independent builds: Stage 2 depends on the `finally/frontend/out/` artifact produced by Stage 1.
- The container exposes port 8010 (`EXPOSE 8010`).
- The runtime command is:

```
uvicorn app.main:app --host 0.0.0.0 --port 8010
```

The SQLite file persists through the volume mount `-v finally-data:/app/db`, which maps to `finally/db/` on the host. `finally/docker-compose.yml` is an optional wrapper around the same image.

## E2E / integration testing

The Playwright suite lives in `finally/test` and runs with `(cd finally/test && npm install --ignore-scripts && npx playwright test --project=chromium)` against a running server. `finally/test/playwright.config.ts` sets BASE_URL, starts the backend when none is running, and uses `finally/test/docker-compose.test.yml` for the containerised run with `LLM_MOCK=true`. Specs cover dashboard, watchlist, trading, portfolio, chat, SSE and navigation, plus `finally/test/e2e.spec.ts` for the root-path heading, ten tickers and $10,000 cash. Every scenario uses real browser interactions (click, type, submit) and asserts a DOM or API state change. Page objects live in `finally/test/pages/`, fixtures in `finally/test/fixtures/base.ts` and API helpers in `finally/test/api/helpers.ts`.

## Acceptance mapping

- One port, one container, one origin: the Docker & Deployment section and `create_app` in `finally/backend/app/main.py` serve the API and the static export on port 8010.
- Real dashboard at GET /: the project-foundation and application-polish phases require the built export and composition of all core components in `finally/frontend/app/page.tsx`.
- Live prices and SSE: core-market-infrastructure and watchlist-market-ui cover the stream and the watchlist shape.
- Trading correctness: database-portfolio-engine and portfolio-visualisation-trading cover cash, positions, average cost and snapshots.
- AI assistant: ai-trading-assistant covers the resilient parser, live prices in prompts, auto-execution and the chat UI.
- Test coverage of Section 13: testing-release covers the Playwright suite and the API contract test for every Section 8 route.

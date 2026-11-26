# Architecture for test4

## Overview

FinAlly is a single-origin, single-container AI trading workstation. A FastAPI app (Python, uv-managed) serves the REST API under /api/*, the SSE price stream under /api/stream/*, and the statically exported Next.js dashboard at /. State lives in one SQLite file at `finally/db/finally.db`, volume-mounted for persistence. One in-process background task produces prices (GBM simulator by default; Massive REST polling when MASSIVE_API_KEY is non-empty) and writes them to a shared in-memory price cache that SSE clients read. Portfolio snapshots are recorded every 30 seconds and after each trade. Chat goes through LiteLLM to OpenRouter (Cerebras inference), or to a deterministic mock when LLM_MOCK=true.

Constraints from SPEC:

- One port (8010), one container, one origin. No CORS.
- Market orders only: instant fill at the cached price, no fees, no confirmation.
- Single user (user_id "default"); every table carries a user_id column.
- GET / renders the real dashboard: FinAlly heading, ten default tickers with prices, $10,000 cash. No placeholder page. If the export is missing, GET / returns 503 with a diagnostic body.
- LLM output passes a resilient multi-key parser; raw JSON never reaches a chat bubble.
- Every LLM prompt embeds live prices, for example `AAPL ($190.50)`.

## Planned file layout

The layout root is `finally`. Every path carries the `finally/` prefix.

Root and deployment: `finally/Dockerfile`, `finally/docker-compose.yml`, `finally/.env`, `finally/.gitignore`, `finally/db/.gitkeep`, `finally/scripts/start_mac.sh`, `finally/scripts/stop_mac.sh`, `finally/scripts/start_windows.ps1`, `finally/scripts/stop_windows.ps1`, `finally/planning/PLAN.md`.

Backend (uv project): `finally/backend/pyproject.toml`, `finally/backend/app/main.py`, `finally/backend/app/api/__init__.py`, `finally/backend/app/api/schemas.py`, `finally/backend/app/api/routes_portfolio.py`, `finally/backend/app/api/routes_watchlist.py`, `finally/backend/app/api/routes_chat.py`, `finally/backend/app/db/__init__.py`, `finally/backend/app/db/schema.sql`, `finally/backend/app/db/seed.py`, `finally/backend/app/db/connection.py`, `finally/backend/app/market/__init__.py`, `finally/backend/app/market/base.py`, `finally/backend/app/market/simulator.py`, `finally/backend/app/market/massive_client.py`, `finally/backend/app/market/cache.py`, `finally/backend/app/market/stream.py`, `finally/backend/app/market/poller.py`, `finally/backend/app/portfolio/__init__.py`, `finally/backend/app/portfolio/repository.py`, `finally/backend/app/portfolio/engine.py`, `finally/backend/app/portfolio/snapshots.py`, `finally/backend/app/llm/__init__.py`, `finally/backend/app/llm/client.py`, `finally/backend/app/llm/prompts.py`, `finally/backend/app/llm/parser.py`, `finally/backend/app/llm/chat_service.py`, `finally/backend/tests/test_market.py`, `finally/backend/tests/test_portfolio.py`, `finally/backend/tests/test_portfolio_api.py`, `finally/backend/tests/test_watchlist_api.py`, `finally/backend/tests/test_llm.py`, `finally/backend/tests/test_api.py`.

Frontend (Next.js static export to `finally/frontend/out/`): `finally/frontend/package.json`, `finally/frontend/tsconfig.json`, `finally/frontend/next.config.js`, `finally/frontend/next-env.d.ts`, `finally/frontend/app/layout.tsx`, `finally/frontend/app/page.tsx`, `finally/frontend/app/globals.css`, `finally/frontend/app/polish.css`, `finally/frontend/components/Header.tsx`, `finally/frontend/components/Sidebar.tsx`, `finally/frontend/components/MarketOverview.tsx`, `finally/frontend/components/Watchlist.tsx`, `finally/frontend/components/PriceChart.tsx`, `finally/frontend/components/PortfolioSummary.tsx`, `finally/frontend/components/TradingPanel.tsx`, `finally/frontend/components/PositionsTable.tsx`, `finally/frontend/components/PnlChart.tsx`, `finally/frontend/components/PortfolioHeatmap.tsx`, `finally/frontend/components/ChatAssistant.tsx`, `finally/frontend/components/ChatAssistant.test.tsx`.

E2E harness: `finally/test/package.json`, `finally/test/playwright.config.ts`, `finally/test/docker-compose.test.yml`, `finally/test/e2e.spec.ts`.

Generated, not hand-written: `finally/backend/uv.lock`, `finally/frontend/package-lock.json`, `finally/frontend/out/`.

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
      - finally/Dockerfile
      - finally/docker-compose.yml
      - finally/.env
      - finally/.gitignore
      - finally/db/.gitkeep
      - finally/scripts/start_mac.sh
      - finally/scripts/stop_mac.sh
    qa_verify_command: 'test -f finally/backend/app/main.py && test -f finally/scripts/start_mac.sh && (cd finally/backend && uv sync && uv run python -c "import app.main")'
    depends_on: []
  - id: project-foundation-support
    title: Project Foundation Support
    spec_focus: Project Foundation
    required_files:
      - finally/frontend/next-env.d.ts
      - finally/frontend/package-lock.json
      - finally/backend/app/db/schema.sql
      - finally/backend/app/db/seed.py
      - finally/frontend/package.json
      - finally/frontend/tsconfig.json
      - finally/frontend/next.config.js
      - finally/frontend/app/layout.tsx
      - finally/frontend/app/page.tsx
      - finally/frontend/app/globals.css
    qa_verify_command: 'test -f finally/backend/app/db/schema.sql && test -f finally/backend/app/db/seed.py && (cd finally/frontend && npm install --ignore-scripts) && test -f finally/frontend/package-lock.json && (cd finally/frontend && npm run build) && test -f finally/frontend/out/index.html'
    depends_on: [project-foundation]
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
    qa_verify_command: '(cd finally/backend && uv run pytest tests/test_market.py -q)'
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
    qa_verify_command: '(cd finally/backend && uv run pytest tests/test_portfolio.py tests/test_portfolio_api.py -q)'
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
    qa_verify_command: '(cd finally/backend && uv run pytest tests/test_watchlist_api.py -q) && (cd finally/frontend && npm run build)'
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
    qa_verify_command: '(cd finally/backend && uv run pytest tests/test_portfolio_api.py -q) && (cd finally/frontend && npm run build)'
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
    qa_verify_command: '(cd finally/backend && LLM_MOCK=true uv run pytest tests/test_llm.py -q) && (cd finally/frontend && npm run build)'
    depends_on: [portfolio-visualisation-trading]
  - id: application-polish
    title: Application Polish
    spec_focus: Application Polish
    required_files:
      - finally/frontend/app/polish.css
      - finally/frontend/app/page.tsx
      - finally/scripts/start_windows.ps1
      - finally/scripts/stop_windows.ps1
    qa_verify_command: 'test -f finally/scripts/start_windows.ps1 && test -f finally/scripts/stop_windows.ps1 && (cd finally/frontend && npm run build)'
    depends_on: [ai-trading-assistant]
    file_dependencies:
      finally/frontend/app/page.tsx: [finally/frontend/components/Header.tsx, finally/frontend/components/Watchlist.tsx, finally/frontend/components/MarketOverview.tsx, finally/frontend/components/PriceChart.tsx, finally/frontend/components/PortfolioSummary.tsx, finally/frontend/components/PositionsTable.tsx, finally/frontend/components/TradingPanel.tsx, finally/frontend/components/ChatAssistant.tsx]
  - id: testing-release
    title: Testing & Release
    spec_focus: Testing & Release
    required_files:
      - finally/backend/tests/test_api.py
      - finally/test/package.json
      - finally/test/playwright.config.ts
      - finally/test/docker-compose.test.yml
      - finally/test/e2e.spec.ts
      - finally/planning/PLAN.md
    qa_verify_command: '(cd finally/backend && uv run pytest tests/test_api.py -q) && (cd finally/test && npm install --ignore-scripts && npx playwright test --list)'
    depends_on: [application-polish]
```

## Requirements

### project-foundation
Runnable skeleton: uv project, `create_app`, static serving of the Next.js export, GET /api/health, Dockerfile, compose file, start/stop scripts, `.env` loading. GET / returns real dashboard HTML once the export exists.

### project-foundation-support
SQLite schema, lazy initialization on first start, seed of ten default tickers and $10,000 cash for user "default". Next.js project setup (package.json, tsconfig, next config, layout, page, globals.css) and frontend skeleton builds to `finally/frontend/out/`.

### core-market-infrastructure
Generated uv lockfile `finally/backend/uv.lock`. Market interface, GBM simulator, Massive client, provider selection, shared price cache, background task, and GET /api/stream/prices emitting named `price` events and unnamed data lines.

### database-portfolio-engine
Trade execution, positions, cash, P&L, snapshots every 30 seconds and after trades, and the portfolio routes.

### watchlist-market-ui
Watchlist CRUD routes, header with connection status, watchlist with sparklines and price flash, main price chart.

### portfolio-visualisation-trading
Trade bar, positions table, heatmap, P&L chart, portfolio summary, all driven by live valuation.

### ai-trading-assistant
LiteLLM to OpenRouter with mock mode, live-price context, resilient parser, auto-execution with `✓ Trade Fill` badges, docked ChatAssistant.

### application-polish
Dark terminal styling, animations, loading and empty states, accessibility, and full composition of Header, Watchlist, MarketOverview, PriceChart, PortfolioSummary, PositionsTable, TradingPanel, and ChatAssistant on page.tsx. `finally/frontend/app/page.tsx` is a skeleton from project-foundation-support; this phase amends it to mount Header, Watchlist, MarketOverview, PriceChart, PortfolioSummary, PositionsTable, TradingPanel and ChatAssistant together.

### testing-release
Planning documentation at `finally/planning/PLAN.md`. Backend pytest suites, Playwright E2E per SPEC Section 13, and the docker compose test harness.

## Unit tests

- `finally/backend/tests/test_market.py`: GBM validity, simulator and Massive parsing through one interface.
- `finally/backend/tests/test_portfolio.py`: buy and sell math, insufficient cash, oversell rejection, P&L.
- `finally/backend/tests/test_portfolio_api.py`: status codes and shapes for /api/portfolio routes.
- `finally/backend/tests/test_watchlist_api.py`: add, duplicate rejection, removal.
- `finally/backend/tests/test_llm.py`: parser variants, malformed input, chat trade validation, mock determinism.
- `finally/backend/tests/test_api.py`: health, GET / real content, 503 when the export is missing.
- `finally/frontend/components/ChatAssistant.test.tsx`: bubble rendering, thinking state, JSON unwrapping.

## Integration and testing

Test strategy has three layers. Each layer has a gate that can fail the phase. The concrete gate commands are held in the `qa_verify_command` fields of the canonical `delivery_phases` block above.

Layer one, unit tests: backend pytest modules live in `finally/backend/tests/`, and frontend component tests live in `finally/frontend/components/`. They cover GBM market math and Massive parsing, portfolio buy and sell math, watchlist and portfolio route shapes, LLM parser variants, and ChatAssistant bubble rendering.

Layer two, frontend build gate: every phase that delivers frontend source must pass the production static export build. The export at `finally/frontend/out/` must exist afterwards, so a missing or placeholder page fails the gate.

Layer three, runtime smoke test: after the build, the server is started from `finally/backend` on port 8010 with `uvicorn app.main:app --host 0.0.0.0 --port 8010`. The smoke test checks that `GET /api/health` succeeds and that `GET /` returns the real dashboard HTML: the FinAlly heading, the ten default tickers, and the `$10,000` cash figure. A placeholder page or a 503 fails the smoke test.


Unit test structure: each backend module has a matching file in `finally/backend/tests/` (`test_market.py`, `test_portfolio.py`, `test_portfolio_api.py`, `test_watchlist_api.py`, `test_llm.py`, `test_api.py`). LLM tests run with `LLM_MOCK=true` so behaviour is deterministic. Tests assert returned values and state changes, not status codes alone.

Full-suite gate: the backend suite, then the frontend build, then the Playwright list check in `finally/test`. Container E2E scenarios are described in the E2E section below.


## Docker & Deployment

Stage 1 uses `node:20-slim`. It copies `finally/frontend/`, runs `npm install --ignore-scripts && npm run build`, and produces the static export at `finally/frontend/out/`.

Stage 2 uses `python:3.12-slim`. It installs uv, copies `finally/backend/`, runs `uv sync` from the lockfile, and copies the Stage 1 export with `COPY --from=frontend /frontend/out /app/frontend/out`. This `finally/frontend/out/` handoff is the only link between the stages. It exposes port 8010 with `EXPOSE 8010` and starts with `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]`.

The named volume is `finally-data:/app/db`, mapped to the project `db/` directory.

## E2E / integration testing

Playwright runs in `finally/test/` against `BASE_URL=http://app:8010` under `finally/test/docker-compose.test.yml`, with `LLM_MOCK=true`. Tests assert real content (ticker names, `$10,000`, chat text) and include at least one real interaction with a state-change assertion (Buy reduces cash and adds a position; Send shows an assistant reply).

## Acceptance mapping

- Real dashboard on GET /: project-foundation, application-polish.
- Ten tickers and $10,000 cash: project-foundation-support.
- Live prices over SSE: core-market-infrastructure.
- Trading and snapshots: database-portfolio-engine, portfolio-visualisation-trading.
- Watchlist CRUD: watchlist-market-ui.
- AI assistant with mock mode: ai-trading-assistant.
- Full E2E suite: testing-release.

# FinAlly — AI Trading Workstation

## Project Specification

## 1. Vision

FinAlly (Finance Ally) is a visually stunning AI-powered trading workstation that streams live market data, lets users trade a simulated portfolio, and integrates an LLM chat assistant that can analyze positions and execute trades on the user's behalf. It looks and feels like a modern Bloomberg terminal with an AI copilot.

This is the capstone project for an agentic AI coding course. It is built entirely by Coding Agents demonstrating how orchestrated AI agents can produce a production-quality full-stack application. 

## 2. User Experience

### First Launch

The user runs a single Docker command (or a provided start script). A browser opens to `http://localhost:8010`. No login, no signup. They immediately see:

- A watchlist of 10 default tickers with live-updating prices in a grid
- $10,000 in virtual cash
- A dark, data-rich trading terminal aesthetic
- An AI chat panel ready to assist

### What the User Can Do

- **Watch prices stream** — prices flash green (uptick) or red (downtick) with subtle CSS animations that fade
- **View sparkline mini-charts** — price action beside each ticker in the watchlist, accumulated on the frontend from the SSE stream since page load (sparklines fill in progressively)
- **Click a ticker** to see a larger detailed chart in the main chart area
- **Buy and sell shares** — market orders only, instant fill at current price, no fees, no confirmation dialog
- **Monitor their portfolio** — a heatmap (treemap) showing positions sized by weight and colored by P&L, plus a P&L chart tracking total portfolio value over time
- **View a positions table** — ticker, quantity, average cost, current price, unrealized P&L, % change
- **Chat with the AI assistant** — ask about their portfolio, get analysis, and have the AI execute trades and manage the watchlist through natural language
- **Manage the watchlist** — add/remove tickers manually or via the AI chat

### Visual Design

- **Dark theme**: backgrounds around `#0d1117` or `#1a1a2e`, muted gray borders, no pure black
- **Price flash animations**: brief green/red background highlight on price change, fading over ~500ms via CSS transitions
- **Connection status indicator**: a small colored dot (green = connected, yellow = reconnecting, red = disconnected) visible in the header
- **Professional, data-dense layout**: inspired by Bloomberg/trading terminals — every pixel earns its place
- **Responsive but desktop-first**: optimized for wide screens, functional on tablet

### Color Scheme
- Accent Yellow: `#ecad0a`
- Blue Primary: `#209dd7`
- Purple Secondary: `#753991` (submit buttons)

## 3. Architecture Overview

### Single Container, Single Port

```
┌─────────────────────────────────────────────────┐
│  Docker Container (port 8010)                   │
│                                                 │
│  FastAPI (Python/uv)                            │
│  ├── /api/*          REST endpoints             │
│  ├── /api/stream/*   SSE streaming              │
│  └── /*              Static file serving         │
│                      (Next.js export)            │
│                                                 │
│  SQLite database (volume-mounted)               │
│  Background task: market data polling/sim        │
└─────────────────────────────────────────────────┘
```

- **Frontend**: Next.js with TypeScript, built as a static export (`output: 'export'`), served by FastAPI as static files
- **Backend**: FastAPI (Python), managed as a `uv` project
- **Database**: SQLite, single file at `db/finally.db`, volume-mounted for persistence
- **Real-time data**: Server-Sent Events (SSE) — simpler than WebSockets, one-way server→client push, works everywhere
- **AI integration**: LiteLLM → OpenRouter (Cerebras for fast inference), with structured outputs for trade execution
- **Market data**: Environment-variable driven — simulator by default, real data via Massive API if key provided

### Why These Choices

| Decision | Rationale |
|---|---|
| SSE over WebSockets | One-way push is all we need; simpler, no bidirectional complexity, universal browser support |
| Static Next.js export | Single origin, no CORS issues, one port, one container, simple deployment |
| SQLite over Postgres | No auth = no multi-user = no need for a database server; self-contained, zero config |
| Single Docker container | Students run one command; no docker-compose for production, no service orchestration |
| uv for Python | Fast, modern Python project management; reproducible lockfile; what students should learn |
| Market orders only | Eliminates order book, limit order logic, partial fills — dramatically simpler portfolio math |

---

## 4. Directory Structure

```
finally/
├── frontend/                 # Next.js TypeScript project (static export)
├── backend/                  # FastAPI uv project (Python)
│   └── db/                   # Schema definitions, seed data, migration logic
├── planning/                 # Project-wide documentation for agents
│   ├── PLAN.md               # This document
│   └── ...                   # Additional agent reference docs
├── scripts/
│   ├── start_mac.sh          # Launch Docker container (macOS/Linux)
│   ├── stop_mac.sh           # Stop Docker container (macOS/Linux)
│   ├── start_windows.ps1     # Launch Docker container (Windows PowerShell)
│   └── stop_windows.ps1      # Stop Docker container (Windows PowerShell)
├── test/                     # Playwright E2E tests + docker-compose.test.yml
│   ├── specs/                # Test scenarios (*.spec.ts)
│   ├── pages/                # Page Objects (dashboard, watchlist, trade, portfolio, chat)
│   ├── fixtures/             # Shared Playwright fixtures
│   ├── api/                  # API test helpers
│   ├── docker-compose.test.yml
│   └── playwright.config.ts
├── db/                       # Volume mount target (SQLite file lives here at runtime)
│   └── .gitkeep              # Directory exists in repo; finally.db is gitignored
├── Dockerfile                # Multi-stage build (Node → Python)
├── docker-compose.yml        # Optional convenience wrapper
├── .env                      # Environment variables (gitignored, .env.example committed)
└── .gitignore
```

### Key Boundaries

- **`frontend/`** is a self-contained Next.js project. It knows nothing about Python. It talks to the backend via `/api/*` endpoints and `/api/stream/*` SSE endpoints. Internal structure is up to the Frontend Engineer agent.
- **`backend/`** is a self-contained uv project with its own `pyproject.toml`. It owns all server logic including database initialization, schema, seed data, API routes, SSE streaming, market data, and LLM integration. Internal structure is up to the Backend/Market Data agents.
- **`backend/app/main.py`** is the application entry point and **must define `def create_app(...) -> FastAPI`** wiring all canonical routes from [Section 8](#8-api-endpoints), SSE, and the static fallback. `backend/app/api/__init__.py` **must exist** and provide the FastAPI factory (this file is a required deliverable, not an implementation detail).
- **`backend/app/api/schemas.py`** defines the Pydantic request/response contracts for the routes in [Section 8](#8-api-endpoints). The contracts in `backend/tests/*` and `test/e2e.spec.ts` must match this section exactly (single source of truth).
- **`backend/db/`** contains schema SQL definitions and seed logic. The backend lazily initializes the database on first request — creating tables and seeding default data if the SQLite file doesn't exist or is empty. Seed data must include the ten default tickers (`AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX`) and a `$10,000` cash balance.
- **`db/`** at the top level is the runtime volume mount point. The SQLite file (`db/finally.db`) is created here by the backend and persists across container restarts via Docker volume.
- **`planning/`** contains project-wide documentation, including this plan. All agents reference files here as the shared contract.
- **`test/`** contains Playwright E2E tests and supporting infrastructure (e.g., `docker-compose.test.yml`). Unit tests live within `frontend/` and `backend/` respectively, following each framework's conventions.
- **`scripts/`** contains start/stop scripts that wrap Docker commands.

### Static Serving Contract (single source of truth)

The Next.js static export **must** be served by FastAPI on the same origin. This contract is fixed and both the Dockerfile and `backend/app/main.py` must agree on it:

- `npm run build` with `output: "export"` produces a static export in `frontend/out/` (Next.js default — do not set `distDir`).
- The Dockerfile **must** `COPY --from=frontend /frontend/out /app/frontend/out`.
- `backend/app/main.py` **must** serve the exported `index.html` at `GET /`. Concretely, `frontend_root = Path(__file__).resolve().parents[2] / "frontend"` and the route reads `frontend_root / "out" / "index.html"`.
- **There must be no hardcoded placeholder/fallback HTML page.** If the export file is missing, the route must return an error (e.g. 503 with a diagnostic body), **never** a hardcoded `<h1>Finally</h1>` or similar placeholder. A placeholder lets the app "work" in tests while showing nothing real to users.
- `GET /` must render the **actual dashboard**: the page title/heading, the ten default tickers with prices, and the `$10,000` cash balance.

Unit tests, E2E tests, and QA must assert this real content. A test that asserts a placeholder string (e.g. `assert "Finally" in dashboard.text`) is a **bug** — it enshrines the fallback as correct behavior.

---

## 5. Environment Variables

```bash
# Required: OpenRouter API key for LLM chat functionality
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Optional: Massive (Polygon.io) API key for real market data
# If not set, the built-in market simulator is used (recommended for most users)
MASSIVE_API_KEY=

# Optional: Set to "true" for deterministic mock LLM responses (testing)
LLM_MOCK=false
```

### Behavior

- If `MASSIVE_API_KEY` is set and non-empty → backend uses Massive REST API for market data
- If `MASSIVE_API_KEY` is absent or empty → backend uses the built-in market simulator
- If `LLM_MOCK=true` → backend returns deterministic mock LLM responses (for E2E tests)
- The backend reads `.env` from the project root (mounted into the container or read via docker `--env-file`)

---

## 6. Market Data

### Two Implementations, One Interface

Both the simulator and the Massive client implement the same abstract interface. The backend selects which to use based on the environment variable. All downstream code (SSE streaming, price cache, frontend) is agnostic to the source.

### Simulator (Default)

- Generates prices using geometric Brownian motion (GBM) with configurable drift and volatility per ticker
- Updates at ~500ms intervals
- Correlated moves across tickers (e.g., tech stocks move together)
- Occasional random "events" — sudden 2-5% moves on a ticker for drama
- Starts from realistic seed prices (e.g., AAPL ~$190, GOOGL ~$175, etc.)
- Runs as an in-process background task — no external dependencies

### Massive API (Optional)

- REST API polling (not WebSocket) — simpler, works on all tiers
- Polls for the union of all watched tickers on a configurable interval
- Free tier (5 calls/min): poll every 15 seconds
- Paid tiers: poll every 2-15 seconds depending on tier
- Parses REST response into the same format as the simulator

### Shared Price Cache

- A single background task (simulator or Massive poller) writes to an in-memory price cache
- The cache holds the latest price, previous price, and timestamp for each ticker
- SSE streams read from this cache and push updates to connected clients
- This architecture supports future multi-user scenarios without changes to the data layer

### SSE Streaming

- Endpoint: `GET /api/stream/prices`
- Long-lived SSE connection; client uses native `EventSource` API
- Server pushes price updates for all tickers known to the system at a regular cadence (~500ms) — in the single-user model this is equivalent to the user's watchlist
- Each SSE event contains ticker, price, previous price, timestamp, and change direction
- Client handles reconnection automatically (EventSource has built-in retry)

---

## 7. Database

### SQLite with Lazy Initialization

The backend checks for the SQLite database on startup (or first request). If the file doesn't exist or tables are missing, it creates the schema and seeds default data. This means:

- No separate migration step
- No manual database setup
- Fresh Docker volumes start with a clean, seeded database automatically

### Schema

All tables include a `user_id` column defaulting to `"default"`. This is hardcoded for now (single-user) but enables future multi-user support without schema migration.

**users_profile** — User state (cash balance)
- `id` TEXT PRIMARY KEY (default: `"default"`)
- `cash_balance` REAL (default: `10000.0`)
- `created_at` TEXT (ISO timestamp)

**watchlist** — Tickers the user is watching
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `ticker` TEXT
- `added_at` TEXT (ISO timestamp)
- UNIQUE constraint on `(user_id, ticker)`

**positions** — Current holdings (one row per ticker per user)
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `ticker` TEXT
- `quantity` REAL (fractional shares supported)
- `avg_cost` REAL
- `updated_at` TEXT (ISO timestamp)
- UNIQUE constraint on `(user_id, ticker)`

**trades** — Trade history (append-only log)
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `ticker` TEXT
- `side` TEXT (`"buy"` or `"sell"`)
- `quantity` REAL (fractional shares supported)
- `price` REAL
- `executed_at` TEXT (ISO timestamp)

**portfolio_snapshots** — Portfolio value over time (for P&L chart). Recorded every 30 seconds by a background task, and immediately after each trade execution.
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `total_value` REAL
- `recorded_at` TEXT (ISO timestamp)

**chat_messages** — Conversation history with LLM
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `role` TEXT (`"user"` or `"assistant"`)
- `content` TEXT
- `actions` TEXT (JSON — trades executed, watchlist changes made; null for user messages)
- `created_at` TEXT (ISO timestamp)

### Default Seed Data

- One user profile: `id="default"`, `cash_balance=10000.0`
- Ten watchlist entries: AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX

---

## 8. API Endpoints

### Market Data
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stream/prices` | SSE stream of live price updates |

### Portfolio
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/portfolio` | Current positions, cash balance, total value, unrealized P&L |
| POST | `/api/portfolio/trade` | Execute a trade: `{ticker, quantity, side}` |
| GET | `/api/portfolio/history` | Portfolio value snapshots over time (for P&L chart) |

### Watchlist
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/watchlist` | Current watchlist tickers with latest prices |
| POST | `/api/watchlist` | Add a ticker: `{ticker}` |
| DELETE | `/api/watchlist/{ticker}` | Remove a ticker |

### Chat
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send a message, receive complete JSON response (message + executed actions) |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check (for Docker/deployment) |

---

## 9. LLM Integration

When writing code to make calls to LLMs, use cerebras-inference skill to use LiteLLM via OpenRouter to the `openrouter/openai/gpt-oss-120b` model with Cerebras as the inference provider. Structured Outputs should be used to interpret the results.

There is an OPENROUTER_API_KEY in the .env file in the project root.

### How It Works

When the user sends a chat message, the backend:

1. Loads the user's current portfolio context (cash, positions with P&L, watchlist with live prices, total portfolio value)
2. Loads recent conversation history from the `chat_messages` table
3. Constructs a prompt with a system message, portfolio context, conversation history, and the user's new message
4. Calls the LLM via LiteLLM → OpenRouter, requesting structured output, using the cerebras-inference skill
5. Parses the complete structured JSON response
6. Auto-executes any trades or watchlist changes specified in the response
7. Stores the message and executed actions in `chat_messages`
8. Returns the complete JSON response to the frontend (no token-by-token streaming — Cerebras inference is fast enough that a loading indicator is sufficient)

### Structured Output Schema

The LLM is instructed to respond with JSON matching this schema:

```json
{
  "message": "Your conversational response to the user",
  "trades": [
    {"ticker": "AAPL", "side": "buy", "quantity": 10}
  ],
  "watchlist_changes": [
    {"ticker": "PYPL", "action": "add"}
  ]
}
```

- `message` (required): The conversational text shown to the user
- `trades` (optional): Array of trades to auto-execute. Each trade goes through the same validation as manual trades (sufficient cash for buys, sufficient shares for sells)
- `watchlist_changes` (optional): Array of watchlist modifications

### Auto-Execution

Trades specified by the LLM execute automatically — no confirmation dialog. This is a deliberate design choice:
- It's a simulated environment with fake money, so the stakes are zero
- It creates an impressive, fluid demo experience
- It demonstrates agentic AI capabilities — the core theme of the course

If a trade fails validation (e.g., insufficient cash), the error is included in the chat response so the LLM can inform the user.

### System Prompt Guidance

The LLM should be prompted as "FinAlly, an AI trading assistant" with instructions to:
- Analyze portfolio composition, risk concentration, and P&L
- Suggest trades with reasoning
- Execute trades when the user asks or agrees
- Manage the watchlist proactively
- Be concise and data-driven in responses
- Always respond with valid structured JSON

### LLM Mock Mode

When `LLM_MOCK=true`, the backend returns deterministic mock responses instead of calling OpenRouter. This enables:
- Fast, free, reproducible E2E tests
- Development without an API key
- CI/CD pipelines

---

## 10. Frontend Design

### Layout

The frontend is a single-page application with a dense, terminal-inspired layout. The specific component architecture and layout system is up to the Frontend Engineer, but the UI should include these elements:

- **Watchlist panel** — grid/table of watched tickers with: ticker symbol, current price (flashing green/red on change), daily change %, and a sparkline mini-chart (accumulated from SSE since page load)
- **Main chart area** — larger chart for the currently selected ticker, with at minimum price over time. Clicking a ticker in the watchlist selects it here.
- **Portfolio heatmap** — treemap visualization where each rectangle is a position, sized by portfolio weight, colored by P&L (green = profit, red = loss)
- **P&L chart** — line chart showing total portfolio value over time, using data from `portfolio_snapshots`
- **Positions table** — tabular view of all positions: ticker, quantity, avg cost, current price, unrealized P&L, % change
- **Trade bar** — simple input area: ticker field, quantity field, buy button, sell button. Market orders, instant fill.
- **AI chat panel** — docked/collapsible sidebar. Message input, scrolling conversation history, loading indicator while waiting for LLM response. Trade executions and watchlist changes shown inline as confirmations.
- **Header** — portfolio total value (updating live), connection status indicator, cash balance

### Mandatory UI Component Composition Rule (Hard Requirement)
`frontend/app/page.tsx` must be a fully integrated single-page application that mounts and renders all functional components simultaneously:
1. **Header** (`Header.tsx`): App title "FinAlly", connection status indicator (`data-testid="connection-status"`), and live cash balance (`data-testid="cash-balance"`).
2. **Watchlist & Market Overview** (`Watchlist.tsx` / `MarketOverview.tsx`): Real ticker rows with live prices, percentage changes, sparkline indicator, and add/remove ticker controls (`aria-label="Watchlist"`).
3. **Interactive Price Chart** (`PriceChart.tsx`): Displays price trends for the selected ticker (`aria-label` matching price chart).
4. **Portfolio Visualizations** (`PortfolioSummary.tsx`, `PositionsTable.tsx`, and `PortfolioHeatmap.tsx` / `PnlChart.tsx`): Shows current portfolio equity, cash, unrealized P&L (`data-testid="portfolio-summary"`), open positions table (`data-testid="positions-table"`), and heatmap/P&L chart.
5. **Trading Panel** (`TradingPanel.tsx`): Order execution panel with ticker input, quantity input, Buy and Sell buttons, and status messages (`data-testid="trading-panel"`).
6. **AI Chat Assistant** (`ChatAssistant.tsx`): Docked chat sidebar with `aria-label="Chat assistant"`, message history, input (`aria-label="Chat message"`), and Send button.

**Strict Anti-Stubbing Rule**: The main page MUST NOT be an isolated mock, minimal text placeholder, or partial stub that renders only a subset of elements. Submitting a stripped-down `page.tsx` or omitting any of the core components is strictly prohibited and constitutes an immediate QA failure.

### Technical Notes

- Use `EventSource` for SSE connection to `/api/stream/prices`
- Canvas-based charting library preferred (Lightweight Charts or Recharts) for performance
- Price flash effect: on receiving a new price, briefly apply a CSS class with background color transition, then remove it
- All API calls go to the same origin (`/api/*`) — no CORS configuration needed
- Tailwind CSS for styling with a custom dark theme

---

## 11. Docker & Deployment

### Multi-Stage Dockerfile

```
Stage 1: Node 20 slim
  - Copy frontend/
  - npm install && npm run build (produces static export)

Stage 2: Python 3.12 slim
  - Install uv
  - Copy backend/
  - uv sync (install Python dependencies from lockfile)
  - Copy frontend build output into a static/ directory
  - Expose port 8010
  - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8010
```

FastAPI serves the static frontend files and all API routes on port 8010.

The Docker build contract has two explicitly related stages. Stage 1 is the Node build stage: it uses `node:20-slim`, installs the frontend dependencies declared in `finally/frontend/package.json`, and runs the production build that produces the static export at `finally/frontend/out/`. Stage 2 is the Python runtime stage: it uses `python:3.12-slim`, installs `uv`, copies the backend sources and the Stage 1 export, installs Python dependencies from the lockfile with `uv sync`, exposes port 8010, and starts the server with `uvicorn app.main:app --host 0.0.0.0 --port 8010`. Stage 2 consumes the `finally/frontend/out/` artifact produced by Stage 1; the stages are not independent builds.

`architecture.md` must restate these two stages in its `## Docker & Deployment` section, naming each base image, the concrete work performed in each stage, the `finally/frontend/out/` handoff between them, the exposed port, and the CMD/entrypoint. A prose paragraph that only mentions base images, port 8010, and CMD without explicitly describing both stages and their relationship is insufficient for design review.

### Docker Volume

The SQLite database persists via a named Docker volume:

```bash
docker run -v finally-data:/app/db -p 8010:8010 --env-file .env finally
```

The `db/` directory in the project root maps to `/app/db` in the container. The backend writes `finally.db` to this path.

### Start/Stop Scripts

**`scripts/start_mac.sh`** (macOS/Linux):
- Builds the Docker image if not already built (or if `--build` flag passed)
- Runs the container with the volume mount, port mapping, and `.env` file
- Prints the URL to access the app
- Optionally opens the browser

**`scripts/stop_mac.sh`** (macOS/Linux):
- Stops and removes the running container
- Does NOT remove the volume (data persists)

**`scripts/start_windows.ps1`** / **`scripts/stop_windows.ps1`**: PowerShell equivalents for Windows.

All scripts should be idempotent — safe to run multiple times.

### Optional Cloud Deployment

The container is designed to deploy to AWS App Runner, Render, or any container platform. A Terraform configuration for App Runner may be provided in a `deploy/` directory as a stretch goal, but is not part of the core build.

---

## 12. Testing Strategy

### Unit Tests (within `frontend/` and `backend/`)

**Backend (pytest)**:
- Market data: simulator generates valid prices, GBM math is correct, Massive API response parsing works, both implementations conform to the abstract interface
- Portfolio: trade execution logic, P&L calculations, edge cases (selling more than owned, buying with insufficient cash, selling at a loss)
- LLM: structured output parsing handles all valid schemas, graceful handling of malformed responses, trade validation within chat flow
- API routes: correct status codes, response shapes, error handling

**Frontend (React Testing Library or similar)**:
- Component rendering with mock data
- Price flash animation triggers correctly on price changes
- Watchlist CRUD operations
- Portfolio display calculations
- Chat message rendering and loading state

### E2E Tests (in `test/`)

**Infrastructure**: A separate `docker-compose.test.yml` in `test/` that spins up the app container plus a Playwright container. This keeps browser dependencies out of the production image.

**Harness contract** (`test/docker-compose.test.yml`) — compose paths resolve relative to the compose file's own directory:
- `app.build.context` must point at the project root (`finally/`, i.e. `context: ..`), so the real `Dockerfile` is used.
- The `playwright` service mounts the project root at `/app` (`volumes: - ..:/app`), sets `BASE_URL=http://app:8010`, and runs `cd /app/test && npm install && npx playwright test --project=chromium`.
- The app healthcheck must hit `curl -f http://localhost:8010/api/health` (`/`, not `/`-only), with `LLM_MOCK=true` set for determinism and no lockfile assumption (`npm install`, not `npm ci`, unless `package-lock.json` is committed).

**Environment**: Tests run with `LLM_MOCK=true` by default for speed and determinism.

**Key Scenarios** (each must assert real rendered/returned content, not just status codes):
- Fresh start: default watchlist appears (assert the ten tickers' text is visible), $10k balance shown (assert the "$10,000" / cash figure), prices are streaming (assert a price updates)
- Add and remove a ticker from the watchlist (assert the ticker appears/disappears in the DOM)
- Buy shares: cash decreases, position appears, portfolio updates (assert the changed figures)
- Sell shares: cash increases, position updates or disappears
- Portfolio visualization: heatmap renders with correct colors, P&L chart has data points
- AI chat (mocked): send a message, receive a response, trade execution appears inline
- SSE resilience: disconnect and verify reconnection

**Content assertion rule**: The "health and dashboard are available" test must assert the actual dashboard content — the page heading (`getByRole('heading', { level: 1, name: 'Trading dashboard' })`), the FinAlly brand text (`getByText('FinAlly')`), at least one watchlist ticker, and the cash/portfolio figure — via `getByText`/`getByRole`/`toHaveText`/`toContainText`. A test that only checks `200 + content-type + body visible` is **insufficient** and must be rejected by QA: it passes when the app serves a placeholder page. Tests must never assert placeholder text (e.g. "Finally", "Coming soon").

**Browser interaction rule**: At least one mandatory E2E test must drive a real user action in the browser — click a button, submit a form, or type into an input — and assert the resulting DOM state or API state change (for example: cash decreases and a position appears after Buy; a ticker appears after Add; an assistant message appears after Send). A static page loaded with `page.goto` plus content assertions alone does **not** satisfy this SPEC. QA must reject `all_passed` when this interaction-and-state-change evidence is missing.

## 13. Playwright E2E Testing Specification

This section defines the **mandatory** Playwright end-to-end testing strategy. Every UI feature described in Sections 2 and 10 MUST have a corresponding Playwright test. No feature ships without E2E coverage.

### Test Infrastructure

**Directory layout**:
```
test/
├── docker-compose.test.yml      # App + Playwright containers
├── playwright.config.ts         # Playwright configuration
├── package.json                 # @playwright/test, test utilities
├── fixtures/
│   └── base.ts                  # Shared fixtures (page, API helpers)
├── pages/
│   ├── dashboard.page.ts        # Page Object: main dashboard
│   ├── watchlist.page.ts        # Page Object: watchlist panel
│   ├── trade.page.ts            # Page Object: trade bar
│   ├── portfolio.page.ts        # Page Object: portfolio views
│   └── chat.page.ts             # Page Object: AI chat panel
├── api/
│   └── helpers.ts               # API test helpers (reset DB, seed data)
└── specs/
    ├── dashboard.spec.ts        # Dashboard load, layout, connection status
    ├── watchlist.spec.ts        # Watchlist CRUD, live price updates
    ├── trading.spec.ts          # Buy/sell workflow, cash/position updates
    ├── portfolio.spec.ts        # Heatmap, P&L chart, positions table
    ├── chat.spec.ts             # AI chat, trade execution via chat
    ├── sse.spec.ts              # SSE streaming, reconnection
    ├── navigation.spec.ts       # Ticker selection, chart switching
    └── mvp.spec.ts              # Full happy-path smoke test
```

**Playwright configuration** (`playwright.config.ts`):
- `baseURL` from `process.env.BASE_URL || 'http://localhost:8010'`
- `timeout`: 30s per test, 60s per assertion
- `retries`: 1 (CI flake tolerance)
- `projects`: `[{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }]`
- `reporter`: `[['html', { open: 'never' }], ['list']]`
- `webServer`: disabled (Docker Compose manages the app)

**Page Objects** — every test uses Page Objects, never raw selectors:
- `DashboardPage`: header elements (total value, cash, connection status), main chart area
- `WatchlistPage`: ticker rows (symbol, price, change%, sparkline), add/remove controls
- `TradePage`: ticker input, quantity input, buy/sell buttons, error messages
- `PortfolioPage`: positions table rows, heatmap rectangles, P&L chart canvas
- `ChatPage`: message input, send button, conversation history, loading spinner

### Test Scenarios — Mandatory Coverage

Every scenario must use `page.getByRole()`, `page.getByText()`, or `page.getByTestId()` — never `page.locator('css-selector')`. Tests must assert **real content**, not visibility or status codes alone.

#### Dashboard (`dashboard.spec.ts`)

| Test | Assertions |
|------|-----------|
| Fresh load shows dashboard | `getByText('FinAlly')` visible, `getByText('$10,000')` visible, page title contains "FinAlly" |
| Default watchlist renders 10 tickers | `getByText('AAPL')`, `getByText('GOOGL')`, `getByText('MSFT')`, `getByText('AMZN')`, `getByText('TSLA')`, `getByText('NVDA')`, `getByText('META')`, `getByText('JPM')`, `getByText('V')`, `getByText('NFLX')` all visible |
| Prices display with $ prefix | At least one ticker row contains text matching `\$[\d,.]+` |
| Connection status indicator present | `getByTestId('connection-status')` visible (green dot = connected) |
| Cash balance updates after trade | After buy: cash value decreases; after sell: cash value increases |
| Layout is dark-themed | `page.locator('body')` has CSS background color close to `#0d1117` or `#1a1a2e` |
| Complete component composition | All core components must be mounted and visible simultaneously: `getByRole('heading', { name: 'FinAlly' })`, `getByTestId('connection-status')`, `getByTestId('cash-balance')`, `getByRole('heading', { name: 'Watchlist' })`, `getByLabel('Market overview')`, `getByLabel(/price chart/i)`, `getByTestId('portfolio-summary')`, `getByTestId('positions-table')`, `getByTestId('trading-panel')`, and `getByLabel('Chat assistant')` |

#### Watchlist (`watchlist.spec.ts`)

| Test | Assertions |
|------|-----------|
| Add ticker via input | Type "PYPL" in add-ticker input, click add button, `getByText('PYPL')` appears in list |
| Remove ticker | Click remove button on AAPL row, `getByText('AAPL')` disappears, list has 9 items |
| Price flash on update | After SSE push, price element briefly has green/red CSS class (check class transition) |
| Sparkline renders | Each ticker row has an SVG or canvas element for the sparkline |
| Duplicate ticker rejected | Add "AAPL" again, error message or no duplicate in list |

#### Trading (`trading.spec.ts`)

| Test | Assertions |
|------|-----------|
| Buy shares | Enter ticker "AAPL", quantity 10, click Buy. Cash decreases by `10 × current_price`. Position row appears with quantity 10. |
| Sell shares | With existing AAPL position, enter quantity 5, click Sell. Cash increases. Position quantity decreases. |
| Insufficient cash rejected | Enter quantity 999999, click Buy. Error message shown. Cash unchanged. |
| Sell more than owned rejected | Enter quantity 999999, click Sell. Error message shown. Position unchanged. |
| Portfolio value updates | After buy, total portfolio value changes (position value + cash). |
| Trade history recorded | Execute 2 trades, portfolio history endpoint returns 2+ snapshots. |

#### Portfolio (`portfolio.spec.ts`)

| Test | Assertions |
|------|-----------|
| Positions table shows holdings | After buying AAPL, table row: ticker "AAPL", quantity matches, avg cost matches buy price |
| Heatmap renders | `getByTestId('portfolio-heatmap')` contains SVG/canvas with colored rectangles |
| Heatmap colors by P&L | Profitable positions have green tint, losing positions have red tint |
| P&L chart renders | `getByTestId('pnl-chart')` contains canvas/SVG with data points |
| Empty portfolio shows zero | Fresh start: total value "$10,000", no position rows |

#### AI Chat (`chat.spec.ts`)

| Test | Assertions |
|------|-----------|
| Send message | Type "What's my portfolio value?", click send. User message appears in history. |
| Receive response | After loading, assistant message appears with text content (not empty). |
| AI executes trade via chat | Type "Buy 5 AAPL", response confirms trade. Portfolio shows new position. |
| AI manages watchlist via chat | Type "Add TSLA to watchlist", response confirms. TSLA appears in watchlist. |
| Mock mode deterministic | With `LLM_MOCK=true`, same input produces same output structure. |
| Loading spinner visible | While waiting for LLM response, spinner/loading indicator shown. |

#### SSE Streaming (`sse.spec.ts`)

| Test | Assertions |
|------|-----------|
| SSE connection established | `page.on('eventsource')` fires, connection status turns green |
| Price updates arrive | Within 5s of load, at least one ticker price changes value |
| Reconnection after disconnect | Kill server, wait, restart. SSE reconnects automatically, status returns to green |
| Multiple tickers update | Within 10s, at least 3 different tickers show price changes |

#### Navigation (`navigation.spec.ts`)

| Test | Assertions |
|------|-----------|
| Click ticker selects chart | Click AAPL in watchlist, main chart area shows "AAPL" heading or ticker label |
| Switch ticker | Click AAPL, then MSFT. Chart updates to show MSFT data. |
| Active ticker highlighted | Selected ticker row has visual indicator (border, background change) |

#### Full Happy Path (`mvp.spec.ts`)

| Test | Assertions |
|------|-----------|
| Complete user journey | Load page → verify 10 tickers → buy 5 AAPL → verify position → sell 3 AAPL → verify cash → add PYPL → remove NFLX → chat "What's my portfolio?" → verify response → check heatmap renders |

### Test Data Management

- `LLM_MOCK=true` is set in `docker-compose.test.yml` for all Playwright tests
- Database is reset before each test file via API call to `/api/health` or a dedicated test-reset endpoint
- No test depends on state from a previous test (tests are isolated)
- Seed data is consistent: 10 default tickers, $10,000 cash

### CI Integration

- Playwright tests run in Docker via `docker-compose.test.yml`
- `npx playwright test --project=chromium` — single browser for speed
- HTML report generated but not opened in CI
- Test failure blocks merge

### Content Assertion Rule (repeated for emphasis)

**Every Playwright test that checks dashboard content MUST assert real rendered content** — ticker names, cash figures, portfolio values, chat messages. Tests that only assert HTTP 200, `response.ok()`, or `element.isVisible()` are **insufficient** and will be rejected by QA. The purpose of E2E tests is to verify the user sees real data, not that the page loads.

**Browser interaction requirement (repeated for emphasis)**: E2E coverage must include a real control interaction followed by a DOM/API state-change assertion. Page load, HTTP status, static heading, or body visibility checks alone are insufficient; a static dashboard cannot pass QA or complete the workflow.

## 14. Design Output Contract (`architecture.md`)

The `architecture.md` design artifact is checked by an automated workflow validator. The design state is **rejected** unless the artifact satisfies every rule in this section. These rules are normative: reproduce the structure literally rather than paraphrasing it. This section exists so that a correct design can be produced on the first pass instead of being repaired through repeated rework cycles.

### 14.1 Required sections

`architecture.md` MUST contain the following headings:

- `## Overview`
- `## Planned file layout`
- `## Module / bead ownership`
- `## HTTP + entrypoint integration`
- `## Delivery phases`
- `## Requirements`
- `## Unit tests`
- `## Integration and testing`
- `## Docker & Deployment`
- `## E2E / integration testing`
- `## Acceptance mapping`

### 14.2 Requirement IDs

Every delivery phase listed in Section 14.3 MUST have at least one `### <req-id>` heading in `architecture.md`, where `<req-id>` is exactly the phase ID from that table. The Tester's anti-hallucination check rejects any `### <req-id>` in `TEST_PLAN.md` that has no matching `### <req-id>` in `architecture.md` or in this SPEC. Only reference requirement IDs that appear in Section 14.3; do not invent new ones.

The nine canonical phase IDs are:

1. `project-foundation`
2. `project-foundation-support`
3. `core-market-infrastructure`
4. `database-portfolio-engine`
5. `watchlist-market-ui`
6. `portfolio-visualisation-trading`
7. `ai-trading-assistant`
8. `application-polish`
9. `testing-release`

### 14.3 Delivery phase contract

The `## Delivery phases` section of `architecture.md` MUST contain a YAML block named `delivery_phases` with one entry per canonical phase ID. Each entry MUST declare `id`, `title`, `spec_focus`, `required_files`, `qa_verify_command`, and `depends_on`. Every `required_files` entry MUST be an exact literal path under `finally/`; wildcard paths such as `test_*.py` or `*_test.go` are forbidden. Each `qa_verify_command` MUST be a single quoted shell scalar that verifies every file owned by that phase.

**Frontend build gate (hard requirement).** If a phase's `required_files` includes ANY path under `finally/frontend/`, that phase's `qa_verify_command` MUST contain the exact fragment `(cd finally/frontend && npm run build)` in addition to any backend or test gates. The workflow validator enforces this and a missing build gate causes design rejection. The following phases deliver frontend files and therefore all require the build gate:

| Phase | Representative frontend files delivered |
|---|---|
| `project-foundation` | `finally/frontend/package.json`, `finally/frontend/tsconfig.json`, `finally/frontend/next.config.js`, `finally/frontend/app/layout.tsx`, `finally/frontend/app/page.tsx`, `finally/frontend/app/globals.css` |
| `project-foundation-support` | `finally/frontend/next-env.d.ts` |
| `watchlist-market-ui` | `finally/frontend/components/Header.tsx`, `Sidebar.tsx`, `MarketOverview.tsx`, `Watchlist.tsx`, `PriceChart.tsx` |
| `portfolio-visualisation-trading` | `finally/frontend/components/PortfolioSummary.tsx`, `finally/frontend/components/TradingPanel.tsx` |
| `ai-trading-assistant` | `finally/frontend/components/ChatAssistant.tsx`, `finally/frontend/components/ChatAssistant.test.tsx` |
| `application-polish` | `finally/frontend/app/polish.css` |

`database-portfolio-engine` and `testing-release` deliver no frontend source in their baseline contract; add the build gate to them only if their `required_files` is extended with a frontend path. When editing a `qa_verify_command` to add the gate, append the fragment before the closing quote and verify the resulting command text contains `npm run build` exactly once and remains a single quoted YAML scalar.

### 14.4 Route verbatim rule

Any HTTP route table in `architecture.md` MUST match Section 8 of this SPEC exactly — method, path, request shape, and response contract. No aliases, no renamed paths, and no extra convenience routes.

### 14.5 File path prefix rule

The layout root is `finally`. All file paths anywhere in `architecture.md` MUST use the `finally/` prefix. Never use `./`, bare `backend/...`, or bare `frontend/...` in backticked paths.

### 14.6 Docker section rule

The `## Docker & Deployment` section of `architecture.md` MUST explicitly describe both build stages: the Node build stage on `node:20-slim` and the Python runtime stage on `python:3.12-slim`. It MUST name the `finally/frontend/out/` handoff from the first stage to the second, the exposed port 8010, and the exact CMD/entrypoint. A paragraph that only names base images, the port, and the CMD without describing the handoff is insufficient for design review.

## Delivery Phases

These delivery phases are designed for an AI-driven software development pipeline. Each phase delivers a vertically integrated, testable milestone rather than isolated technical components, ensuring continuous progress toward a fully functional application.

The eight user-facing phases below map to the nine canonical phase IDs in Section 14.3. `project-foundation-support` is a machine-facing split of Phase 1 so that support artifacts and SQLite initialization can be verified independently. When producing `architecture.md`, use the canonical IDs from Section 14.3 verbatim; do not treat the "Phase N" labels as IDs.

| User-facing phase | Canonical design phase ID(s) |
|---|---|
| Phase 1 — Project Foundation | `project-foundation`, `project-foundation-support` |
| Phase 2 — Core Market Infrastructure | `core-market-infrastructure` |
| Phase 3 — Database & Portfolio Engine | `database-portfolio-engine` |
| Phase 4 — Watchlist & Market UI | `watchlist-market-ui` |
| Phase 5 — Portfolio Visualisation & Trading | `portfolio-visualisation-trading` |
| Phase 6 — AI Trading Assistant | `ai-trading-assistant` |
| Phase 7 — Application Polish | `application-polish` |
| Phase 8 — Testing & Release | `testing-release` |

---

# Phase 1 — Project Foundation

### Goal

Create a runnable application skeleton that starts successfully.

### Deliverables

- Repository structure
- Next.js project setup
- FastAPI project setup
- Python `uv` configuration
- Dockerfile
- Docker Compose configuration
- Cross-platform start/stop scripts
- Environment variable loading
- Static frontend served by FastAPI
- Health check endpoint
- Planning documentation
- SQLite initialization
- CI linting configuration

### Exit Criteria

- Application starts successfully using Docker
- Browser opens successfully
- `/api/health` returns success
- Static frontend is served correctly: `GET /` returns the real dashboard HTML (heading, tickers, cash figure), **not** a placeholder/fallback page

---

# Phase 2 — Core Market Infrastructure

### Goal

Implement the live market data platform that all downstream functionality depends on.

### Deliverables

- Market data abstraction/interface
- Geometric Brownian Motion (GBM) simulator
- Massive API implementation
- Environment-driven provider selection
- Shared in-memory price cache
- Background polling/simulation task
- Server-Sent Events (SSE) endpoint
- Connection status management

### Exit Criteria

- Live prices stream continuously
- SSE reconnects automatically
- Simulator and Massive implementations are interchangeable

---

# Phase 3 — Database & Portfolio Engine

### Goal

Implement persistent portfolio management and trading logic.

### Deliverables

- SQLite schema creation
- Lazy database initialization
- Default seed data
- Portfolio calculation engine
- Trade execution engine
- Position management
- Cash balance management
- Portfolio snapshot recording
- Repository/data access layer

### Exit Criteria

- Trades execute correctly
- Cash balances update correctly
- Portfolio calculations are verified
- Portfolio persists across application restarts

---

# Phase 4 — Watchlist & Market UI

### Goal

Deliver a live market monitoring experience.

### Deliverables

- Watchlist API
- Watchlist CRUD functionality
- Live updating watchlist interface
- Price flash animations
- Sparkline chart accumulation
- Main price chart
- Selected ticker state management
- Responsive desktop-first layout
- Application header
- Connection status indicator

### Exit Criteria

- Watchlist updates in real time
- Charts update continuously
- Price animations function correctly
- Users can add and remove tickers

---

# Phase 5 — Portfolio Visualisation & Trading

### Goal

Complete the manual trading workstation experience.

### Deliverables

- Trade entry bar
- Buy/Sell workflow
- Positions table
- Portfolio heatmap
- Portfolio value (P&L) chart
- Portfolio summary panel
- Live portfolio valuation
- Trading validation and error handling

### Exit Criteria

- Users can execute trades
- Portfolio updates immediately
- Visualisations reflect current positions
- Portfolio history records snapshots correctly

---

# Phase 6 — AI Trading Assistant

### Goal

Integrate an AI assistant capable of analysing and managing the portfolio.

### Deliverables

- LiteLLM integration
- OpenRouter client
- Structured output parsing
- Prompt construction
- Conversation persistence
- AI trade execution
- AI watchlist management
- Mock LLM mode
- Error handling and recovery

### Exit Criteria

- AI responds to user requests
- AI executes trades successfully
- AI manages the watchlist
- Chat history persists
- Mock mode produces deterministic responses

---

# Phase 7 — Application Polish

### Goal

Refine the application into a production-quality trading workstation.

### Deliverables

- Complete dark terminal styling
- UI animations
- Loading indicators
- Empty states
- User-friendly error handling
- Notifications
- Responsive improvements
- Performance optimisation
- Accessibility review

### Exit Criteria

- Professional user experience
- No significant UX gaps
- Stable under continuous live streaming
- Full UI Component Composition: `frontend/app/page.tsx` MUST compose and render all core components (`Header`, `Watchlist`, `MarketOverview`, `PriceChart`, `PortfolioSummary`, `PositionsTable`, `TradingPanel`, `ChatAssistant`). Stubbing, mock-only JSX, or omitting any of these components in `page.tsx` is strictly forbidden and constitutes a QA failure.

---

# Phase 8 — Testing & Release

### Goal

Validate the complete application and prepare it for release.

### Deliverables

### Backend

- Unit tests
- API tests
- Portfolio tests
- Market simulator tests
- LLM parsing tests

### Frontend

- Component tests
- Rendering tests
- State management tests

### End-to-End

- Playwright test suite covering all scenarios in Section 13
- Page Objects for dashboard, watchlist, trade bar, portfolio, and chat
- Docker test environment (`docker-compose.test.yml`)
- Mock LLM integration tests (`LLM_MOCK=true`)
- SSE streaming tests with reconnection
- Full happy-path smoke test (`mvp.spec.ts`)
- Trading workflow tests (buy, sell, insufficient cash, sell short)

### Release

- Docker validation
- Documentation
- README
- Environment examples

### Exit Criteria

- All Playwright E2E tests pass (see Section 13 for mandatory coverage)
- Complete UI visibility verified: all components (`Header`, `Watchlist`, `MarketOverview`, `PriceChart`, `PortfolioSummary`, `PositionsTable`, `TradingPanel`, `ChatAssistant`) verified mounted and visible on the page before workflow completion is granted
- All unit tests pass (backend pytest + frontend component tests)
- All automated tests **assert real content** (not just status codes / visibility)
- Every UI feature in Sections 2 and 10 has a corresponding Playwright test
- Fresh clone runs successfully
- One-command startup works
- Application is demo-ready: `GET /` renders the full dashboard (watchlist tickers with live prices, $10k cash, AI chat panel), never a placeholder page

---

# Delivery Dependency Flow

```text
Phase 1 — Project Foundation
            │
            ▼
Phase 2 — Core Market Infrastructure
            │
            ▼
Phase 3 — Database & Portfolio Engine
            │
     ┌──────┴──────┐
     ▼             ▼
Phase 4       Phase 5
Market UI   Trading UI
     │             │
     └──────┬──────┘
            ▼
Phase 6 — AI Trading Assistant
            │
            ▼
Phase 7 — Application Polish
            │
            ▼
Phase 8 — Testing & Release
```

---

# Delivery Philosophy

This project is intentionally organised into vertically integrated delivery phases rather than frontend/backend workstreams. Each phase delivers a complete, testable capability that builds on previous work while minimising dependencies between AI development agents.

Each phase should conclude with:

- A runnable application
- Passing automated tests for implemented functionality
- Updated documentation
- A demonstrable feature set
- Clear acceptance criteria before progressing to the next phase

This approach enables continuous validation, reduces integration risk, and aligns well with autonomous AI software development pipelines.

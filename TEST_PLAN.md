# Test Plan — FinAlly AI Trading Workstation

## Requirements → tests

### project-foundation
Requirement: The runnable skeleton serves the real exported dashboard and health endpoint, with Docker/Compose wiring and no placeholder fallback.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: te-0oc
Phase: project-foundation
Scenarios:
- Create the FastAPI app and request `/api/health` and `/`.
- Serve an existing `frontend/out/index.html`, then exercise the missing-export path.
- Build and start the Compose service with its configured port, environment file, volume, and healthcheck.
Assertions:
- `create_app()` returns FastAPI, health returns success, and `/` contains “Market Dashboard”, all ten seeded ticker symbols, prices, and `$10,000`.
- Missing export returns a diagnostic error rather than hardcoded placeholder HTML.
- The container serves the same real dashboard on port 8000 and the healthcheck targets `/api/health`.

Requirement: The static Next.js project exports a real dashboard with metadata, dark styling, and the required ten ticker prices and cash figure.
Level: integration
Test file: finally/frontend/app/page.test.tsx
Bead ID: te-stl
Phase: project-foundation
Scenarios:
- Run the frontend production build and inspect the generated export.
- Load the exported page through FastAPI.
Assertions:
- `frontend/out/index.html` exists and contains the dashboard heading, AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX, and `$10,000`.
- The page has FinAlly/dashboard metadata and dark-theme styling without an empty or “Coming soon” fallback.

### project-foundation-support
Requirement: Foundation support provides idempotent cross-platform launch/stop scripts, environment loading, repository hygiene, SQLite marker/schema initialization, and CI linting.
Level: integration
Test file: finally/backend/db/schema_test.py
Bead ID: pending
Phase: project-foundation-support
Scenarios:
- Inspect the shell and PowerShell launch/stop scripts, `.env`, `.gitignore`, CI workflow, SQLite marker, and schema initialization.
- Run the launch/stop scripts repeatedly with a temporary database volume and controlled environment.
Assertions:
- Scripts resolve their own directory, are idempotent, preserve the database volume, propagate failures, and load `finally/.env`.
- Repository hygiene excludes runtime database state, schema initialization creates the required SQLite boundary, and CI configuration contains the documented lint/verification behavior.
- The support assets exist at their declared paths and do not claim ownership of later market or portfolio behavior.

### core-market-infrastructure
Requirement: The GBM simulator and Massive provider implement the shared market-data contract, with provider selection controlled by `MASSIVE_API_KEY`.
Level: unit
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending
Phase: core-market-infrastructure
Scenarios:
- Generate seeded GBM prices with deterministic inputs.
- Normalize valid and malformed Massive responses.
- Select the simulator when the key is absent or empty and Massive when non-empty.
Assertions:
- GBM output is finite, positive, timestamped, and conforms to the common quote shape.
- Massive normalization preserves ticker, price, previous price, timestamp, and direction; malformed/upstream failures follow the specified error behavior.
- Provider selection changes only with a non-empty `MASSIVE_API_KEY`.

Requirement: The shared cache maintains bounded latest/previous quotes and expiry, and `/api/stream/prices` emits valid SSE updates and cleans up disconnected clients.
Level: integration
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending
Phase: core-market-infrastructure
Scenarios:
- Insert and update quotes, including an expired quote.
- Connect to the SSE endpoint and disconnect the consumer.
Assertions:
- Cache reads return latest price, previous price, timestamp, direction, and reject expired entries.
- SSE events use the `data:` framing and contain ticker, price, previous price, timestamp, and direction; disconnect cleanup does not leak the stream.
- The canonical route is `GET /api/stream/prices`.

### database-portfolio-engine
Requirement: SQLite lazily initializes all specified tables, uses the default user, seeds ten tickers and 10000.0 cash, and persists across restarts.
Level: integration
Test file: finally/backend/app/portfolio/engine_test.py
Bead ID: pending
Phase: database-portfolio-engine
Scenarios:
- Initialize an empty temporary database and inspect schema and seed rows.
- Close and reopen the database, then read the same profile, watchlist, and positions.
Assertions:
- `users_profile`, `watchlist`, `positions`, `trades`, `portfolio_snapshots`, and `chat_messages` exist with `user_id="default"` behavior.
- The ten required tickers and exactly 10000.0 starting cash are seeded.
- Reopening preserves data and uniqueness constraints prevent duplicate default-user watchlist/position rows.

Requirement: Fractional, fee-free market trades update cash, positions, history, and snapshots atomically with validation.
Level: unit
Test file: finally/backend/app/portfolio/engine_test.py
Bead ID: pending
Phase: database-portfolio-engine
Scenarios:
- Buy and sell fractional shares at current prices, including a loss.
- Attempt insufficient-cash buys, oversells, zero/negative quantities, and invalid sides.
- Force a failed transaction and inspect all affected records.
Assertions:
- Valid buys/sells update cash, quantity, average cost, trade log, and immediate portfolio snapshot using the correct market price and no fees.
- Invalid trades return the documented error and leave cash, positions, trades, and snapshots unchanged.
- Portfolio totals and unrealized P&L use current prices; periodic snapshots and persistence are supported.

### watchlist-market-ui
Requirement: Watchlist API CRUD and the live market dashboard expose current prices, duplicate handling, selection, sparklines, flashes, and connection status.
Level: ui
Test file: finally/test/watchlist-market-ui.spec.ts
Bead ID: pending
Phase: watchlist-market-ui
Scenarios:
- Load the seeded dashboard, add PYPL, remove it, and attempt to add AAPL twice.
- Click AAPL then MSFT and observe chart selection.
- Receive SSE updates and exercise connected, reconnecting, and disconnected states.
Assertions:
- The ten seeded tickers and prices render; add/remove changes the visible list and duplicate behavior shows an error or no duplicate.
- Selected ticker changes the main chart and active-row state; each row accumulates a sparkline.
- Price updates visibly apply green/red flash transitions, and the connection indicator exposes green/yellow/red states.
- `GET /api/watchlist`, `POST /api/watchlist`, and `DELETE /api/watchlist/{ticker}` return the specified shapes/statuses and errors.

### portfolio-visualisation-trading
Requirement: Portfolio API and UI display positions, cash/value/P&L, heatmap, history chart, and atomic buy/sell validation.
Level: ui
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: pending
Phase: portfolio-visualisation-trading
Scenarios:
- Start with an empty portfolio, buy AAPL, then sell part of the position.
- Attempt an unaffordable buy and a sell larger than owned.
- Inspect the positions table, heatmap, value-history chart, and live summary.
Assertions:
- `GET /api/portfolio`, `POST /api/portfolio/trade`, and `GET /api/portfolio/history` expose the specified fields and status/error shapes.
- Cash, quantity, average cost, total value, and unrealized P&L visibly change after valid trades; failed trades leave them unchanged.
- Positions table shows required columns, heatmap rectangles size/color by weight/P&L, and the P&L chart contains snapshot data; empty state shows $10,000 and no positions.

### ai-trading-assistant
Requirement: Chat returns structured portfolio-aware responses, validates and executes actions, persists history, and provides deterministic mock mode.
Level: unit
Test file: finally/frontend/components/ChatAssistant.test.tsx
Bead ID: pending
Phase: ai-trading-assistant
Scenarios:
- Render the assistant, send a question, and render loading then assistant content.
- Parse valid structured output, malformed output, empty input, and action arrays.
Assertions:
- The component sends/reads `message`, `trades`, and `watchlist_changes` with the declared JSON types and displays non-empty assistant text.
- Loading state and provider/error recovery are visible; invalid input is not submitted.
- Trade and watchlist confirmations render inline.

Requirement: `POST /api/chat` uses the required LiteLLM/OpenRouter structured contract, shared validation, persistence, and `LLM_MOCK=true` determinism.
Level: integration
Test file: finally/frontend/components/ChatAssistant.test.tsx
Bead ID: pending
Phase: ai-trading-assistant
Scenarios:
- Exercise the chat component against the `/api/chat` contract with portfolio questions and mocked trade/watchlist actions twice with `LLM_MOCK=true`.
- Post actions that fail cash/share validation and simulate provider failure.
Assertions:
- Responses contain `message`, `trades`, and `watchlist_changes`; valid actions execute through shared services and are persisted in `chat_messages`.
- Invalid actions produce included errors without partial mutation; identical mock inputs produce identical decoded JSON values.
- Provider and malformed-output failures return the documented recoverable error shape.

### application-polish
Requirement: The terminal UI is dark, responsive, accessible, animated, and recoverable from market/API/chat failures while retaining real data.
Level: ui
Test file: finally/test/application-polish.spec.ts
Bead ID: pending
Phase: application-polish
Scenarios:
- Exercise the dashboard at wide and narrow/tablet viewports.
- Traverse controls by keyboard and inspect accessible names and focus order.
- Simulate market, API, SSE, and chat failures, then recover.
Assertions:
- Dark colors, responsive layout, readable real ticker/cash content, loading/empty states, price transitions, notifications, and connection status are present.
- Controls have accessible names and usable keyboard focus order; no required control is hidden or broken at supported widths.
- Failures show a clear recoverable error state rather than blank or misleading content, and successful retry restores real data.

### testing-release
Requirement: The release harness validates the complete application with unit, component, API, and mandatory Playwright coverage.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: pending
Phase: testing-release
Scenarios:
- Build the real Docker image, start the test Compose stack with `LLM_MOCK=true`, and run the Chromium Playwright project.
- Execute dashboard, watchlist, trading, portfolio, chat, SSE, navigation, and full MVP scenarios through Page Objects.
Assertions:
- Tests assert real headings, all ten tickers, prices, cash, portfolio values, chat content, visualizations, watchlist changes, and reconnection—not status/visibility alone or placeholder text.
- Page Objects and role/text/test-ID selectors cover every mandatory scenario; test isolation and database reset hold.
- Backend pytest, frontend component tests, Docker health, production build, and Playwright all pass; Compose cleanup preserves the original failure status.

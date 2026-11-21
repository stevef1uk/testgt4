# Test Plan — Polecat

## Requirements → tests

### project-foundation
Requirement: The application serves the project workspace dashboard with the required heading, starting amount, ten specified tracked tickers, a healthy API response, and a diagnostic 404 when the frontend export is unavailable.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: te-x44
Phase: project-foundation
Scenarios:
- GET /api/health returns status 200 and the decoded JSON object {"status":"ok"}.
- GET / serves the exported dashboard and contains the heading "Project workspace" and "$10,000".
- The dashboard contains exactly the specified tracked symbols AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, JPM, V, and JNJ.
- When the configured frontend export directory has no index.html, GET / returns status 404 with {"detail":"Frontend export not found"} rather than the fallback "Polecat" response.
Assertions:
- Assert status codes and decoded JSON values/types, including the diagnostic detail.
- Assert the dashboard text contains the required heading, amount, and all ten symbols.
- Assert the missing-export response does not contain stale fallback content.

### project-foundation-support
Requirement: Support artifacts provide environment defaults, lifecycle scripts, CI, database mount marker, and idempotent seeded SQLite initialization.
Level: unit
Test file: finally/backend/db/schema_test.py
Bead ID: pending
Phase: project-foundation-support
Scenarios:
- Fresh SQLite initialization creates users_profile, watchlist, positions, trades, portfolio_snapshots, and chat_messages with the default profile, ten SPEC tickers, and 10000.0 cash.
- Repeated initialization succeeds without duplicate profile or watchlist rows.
Assertions:
- Required tables, constraints, default profile, exact ten tickers, and cash balance are present.
- A second initialization is idempotent and preserves one default profile and one row for each seeded ticker.

### core-market-infrastructure
Requirement: GBM and Massive providers share one interface, selection follows MASSIVE_API_KEY, the cache retains latest/previous/timestamp values, and SSE emits the specified event fields.
Level: unit
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending
Phase: core-market-infrastructure
Scenarios:
- Generate positive GBM prices and parse a Massive response into the shared provider shape.
- Select the simulator when MASSIVE_API_KEY is absent and Massive when it is non-empty.
- Update the cache twice and serialize an SSE event with ticker, price, previous price, timestamp, and direction.
Assertions:
- Provider outputs are interchangeable and positive.
- Cache previous value equals the prior latest value and SSE uses event-stream content with every required field.

### database-portfolio-engine
Requirement: Portfolio persistence and engine support fractional market orders, validation, average cost, P&L, snapshots, watchlist data, and persistence.
Level: unit
Test file: finally/backend/app/portfolio/engine_test.py
Bead ID: pending
Phase: database-portfolio-engine
Scenarios:
- Buy and sell fractional shares and verify cash, quantity, and weighted average cost.
- Reject insufficient-cash buys and excessive sells without mutation.
- Calculate current value and unrealized P&L, record immediate snapshots, and reopen the database.
Assertions:
- Balances, positions, average cost, P&L, trade history, and snapshots match the documented calculations.
- Portfolio, trade, and history routes are registered and use the engine.

### watchlist-market-ui
Requirement: Watchlist UI renders seeded symbols and prices, consumes SSE updates, accumulates sparklines, selects charts, flashes direction, manages CRUD, and shows connection status.
Level: ui
Test file: finally/test/watchlist-market-ui.spec.ts
Bead ID: pending
Phase: watchlist-market-ui
Scenarios:
- Render all ten seeded tickers and prices, then observe an SSE price update, sparkline point, and green/red flash.
- Select different tickers, add PYPL, remove a ticker, reject duplicate AAPL, and observe connection status.
Assertions:
- Browser assertions observe real symbols, changed prices, chart selection, sparkline elements, CRUD results, and connected/reconnecting state.

### portfolio-visualisation-trading
Requirement: Trading UI executes market orders and displays immediate cash/position changes, validation errors, positions, P&L, heatmap, and history chart data.
Level: ui
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: pending
Phase: portfolio-visualisation-trading
Scenarios:
- Buy and sell AAPL shares, then verify immediate cash and position changes.
- Reject insufficient-cash and excessive-sell orders without changing state.
- Render positions, P&L values, heatmap rectangles with P&L colors, and history chart data.
Assertions:
- Successful and rejected trade values match the API result; visualizations contain the resulting portfolio data.

### ai-trading-assistant
Requirement: Chat returns validated structured actions, supports deterministic mock mode, persists messages, executes valid actions, rejects invalid actions, and recovers from provider errors.
Level: integration
Test file: finally/backend/tests/test_chat.py
Bead ID: pending
Phase: ai-trading-assistant
Scenarios:
- POST /api/chat returns message, trades, and watchlist_changes with the documented types.
- Identical LLM_MOCK requests produce equal decoded JSON; valid actions persist and use engine validation.
- Malformed/provider failures return a usable error without corrupting state, while ChatAssistant.test.tsx covers loading and inline confirmations.
Assertions:
- Response keys/types, persistence, deterministic mock output, valid changes, and unchanged state after rejected actions are verified.

### application-polish
Requirement: Polish provides the dark terminal palette, responsive layout, animations, loading/error/empty states, accessible labels, notifications, and stable streaming.
Level: ui
Test file: finally/test/application-polish.spec.ts
Bead ID: pending
Phase: application-polish
Scenarios:
- Check dark palette, responsive layout, price transitions, loading indicators, and stable streaming.
- Exercise empty, error, notification, and accessible-control states.
Assertions:
- Computed styles match the specified palette; real dashboard content remains visible.
- State text/styles and accessible names communicate loading, errors, empty results, notifications, and operation outcomes.

### testing-release
Requirement: Dockerized Playwright release testing runs with LLM_MOCK=true, healthcheck, real-content assertions, and complete end-to-end coverage.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: pending
Phase: testing-release
Scenarios:
- Compose builds and starts the app with LLM_MOCK=true, healthchecks /api/health, and runs Playwright with the declared Chromium project.
- Fresh dashboard assertions cover heading, ten tickers, prices, connection status, and $10,000.
- Browser flows cover watchlist CRUD, streaming/reconnection, navigation, trading validation, portfolio visualizations, chat actions, and the happy path.
Assertions:
- Tests assert real content and changed values, not status alone or placeholders.
- Compose preserves Playwright failure status and cleans up resources.

# Test Plan — FinAlly

## Requirements → tests

### project-foundation
Requirement: Buildable Next.js export and FastAPI factory serve the real dashboard, health response, Docker runtime, and no placeholder fallback.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: te-x44
Phase: project-foundation
Scenarios:
- Health endpoint succeeds and root serves the exported dashboard.
- Root contains the heading, all ten seeded tickers, and $10,000.
- Missing index export returns a diagnostic error rather than placeholder HTML.
Assertions:
- Health response is successful.
- Root contains AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX, and $10,000.
- Missing export is an error and never contains synthesized placeholder markup.

### project-foundation-support
Requirement: Support artifacts provide environment defaults, lifecycle scripts, CI, database mount marker, and idempotent seeded SQLite initialization.
Level: unit
Test file: finally/backend/db/schema_test.py
Bead ID: pending
Phase: project-foundation-support
Scenarios:
- Fresh SQLite initialization creates all required tables, one default profile, ten default watchlist tickers, and 10000.0 cash.
- Repeated initialization succeeds without duplicate profile or watchlist rows.
Assertions:
- Required schema tables and exact seed values are present.
- A second initialization is idempotent and leaves one default profile and one row for each specified ticker.

### core-market-infrastructure
Requirement: GBM and Massive providers share an interface, selection follows the environment, cache stores price history, and SSE emits the specified event fields.
Level: unit
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending
Phase: core-market-infrastructure
Scenarios:
- GBM generates positive prices and Massive parsing produces the same provider shape.
- Provider selection responds to MASSIVE_API_KEY.
- Cache retains latest, previous, and timestamp values.
- SSE events contain ticker, price, previous price, timestamp, and direction.
Assertions:
- Both providers are interchangeable and prices are valid positive numbers.
- Cache transitions preserve the prior value.
- SSE serialization contains every required field and uses the event-stream media type.

### database-portfolio-engine
Requirement: Portfolio persistence and engine support fractional market orders, validation, average cost, P&L, snapshots, watchlist data, and persistence.
Level: unit
Test file: finally/backend/app/portfolio/engine_test.py
Bead ID: pending
Phase: database-portfolio-engine
Scenarios:
- Fractional buy and sell update cash, quantity, and weighted average cost.
- Insufficient cash and excessive sell requests are rejected without mutation.
- Current prices produce correct total value and unrealized P&L.
- Successful trades record snapshots and survive reopening the database.
Assertions:
- Balances, positions, average cost, and P&L match order calculations.
- Rejected orders do not alter cash, positions, or history.
- Successful trades create persisted snapshots.
- Portfolio, trade, and history route paths are registered and use the engine.

### watchlist-market-ui
Requirement: Watchlist UI renders seeded symbols and prices, consumes the price stream, accumulates sparklines, selects charts, flashes direction, manages CRUD, and shows connection status.
Level: ui
Test file: finally/test/watchlist-market-ui.spec.ts
Bead ID: pending
Phase: watchlist-market-ui
Scenarios:
- Initial page displays all ten tickers and live prices.
- A stream update changes a price, adds a sparkline point, and applies green/red flash styling.
- Clicking a ticker changes the detailed chart.
- Adding PYPL, removing a ticker, and adding duplicate AAPL produce the specified visible results.
- Connection status displays connected or reconnecting state.
Assertions:
- Browser assertions observe real ticker, price, chart, and status content.
- Add/remove changes are reflected in the DOM and duplicate entries are not created.
- Sparkline elements exist and selected chart content identifies the ticker.

### portfolio-visualisation-trading
Requirement: Trading UI executes market orders and displays immediate cash/position changes, validation errors, positions, P&L, heatmap, and history chart data.
Level: ui
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: pending
Phase: portfolio-visualisation-trading
Scenarios:
- Buy AAPL shares, then sell part of the position.
- Insufficient cash and selling more than owned show errors without changing state.
- Positions table shows quantity, average cost, current price, unrealized P&L, and percentage change.
- Heatmap colors positions by P&L and history chart renders snapshot data.
Assertions:
- Successful buy decreases cash and creates a position; sell increases cash and decreases quantity.
- Rejected trades preserve prior values.
- Heatmap contains colored position rectangles and the P&L chart contains data.

### ai-trading-assistant
Requirement: Chat returns validated structured actions, supports deterministic mock mode, persists messages, executes valid actions, rejects invalid actions, and recovers from provider errors.
Level: integration
Test file: finally/backend/tests/test_chat.py
Bead ID: pending
Phase: ai-trading-assistant
Scenarios:
- Chat returns a complete message and executed-action JSON response.
- Identical mock requests produce identical decoded responses.
- Valid trade/watchlist actions persist and use engine validation.
- Invalid actions and malformed/provider failures return usable errors without corrupting state.
Assertions:
- Response keys and types match message, trades, and watchlist_changes.
- Mock responses compare equal as decoded JSON values.
- Persisted messages and valid portfolio/watchlist changes are correct.
- Rejected actions leave balances and positions unchanged.
- finally/frontend/components/ChatAssistant.test.tsx asserts loading, assistant content, and inline confirmations.

### application-polish
Requirement: Polish provides the dark terminal palette, responsive layout, animations, loading/error/empty states, accessible labels, notifications, and stable streaming.
Level: ui
Test file: finally/test/application-polish.spec.ts
Bead ID: pending
Phase: application-polish
Scenarios:
- Dashboard has the specified dark styling and responsive layout.
- Price transitions and loading indicators appear during updates and requests.
- Empty, error, and notification states are user-readable and controls are accessible.
Assertions:
- Computed background matches the specified dark palette and real dashboard content remains visible.
- Animation and loading/error/empty state text or styles are observable.
- Interactive controls have accessible names and operation results are communicated.

### testing-release
Requirement: Dockerized Playwright release testing runs with mock LLM, healthcheck, real-content assertions, and complete end-to-end coverage.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: pending
Phase: testing-release
Scenarios:
- Compose starts the app with LLM_MOCK=true and healthchecks the health route.
- Fresh dashboard asserts heading, ten tickers, prices, connection status, and $10,000.
- Browser covers watchlist CRUD, streaming and reconnection, navigation, trading validation, portfolio visualizations, chat actions, and the happy path.
Assertions:
- Tests assert visible real content and changed values, never placeholder text or status alone.
- Browser tests use roles, text, or test IDs and cover every specified UI flow.
- Stream reconnection restores connected status and visible prices change.
- Compose preserves Playwright failure status and cleans up resources.

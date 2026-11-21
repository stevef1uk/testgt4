# Test Plan — FinAlly

## Requirements → tests

### project-foundation
Requirement: Serve the exported FinAlly dashboard, health response, required starting balance and ten tracked tickers, and a documented diagnostic response when the frontend export is unavailable.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: te-x44
Phase: project-foundation
Scenarios:
- GET /api/health returns the documented success status and JSON object.
- GET / serves the exported dashboard containing “FinAlly”, “$10,000”, and AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, JPM, V, and NFLX.
- When the frontend export is absent, GET / returns the documented diagnostic error response (including its documented detail), without fallback dashboard content; do not require an unsupported status code.
Assertions:
- Assert the documented status, decoded JSON values, and value types for health and the missing-export diagnostic.
- Assert the heading, starting amount, and every required ticker in the dashboard; assert stale fallback content is absent.

### project-foundation-support
Requirement: Initialize all six SPEC database tables with their documented columns and constraints, and seed the exact default profile, ten tickers, and $10,000 cash idempotently.
Level: unit
Test file: finally/backend/db/schema_test.py
Bead ID: te-s2x
Phase: project-foundation-support
Scenarios:
- Initialize an in-memory SQLite database and verify users_profile, watchlist, positions, trades, portfolio_snapshots, and chat_messages exist with every SPEC-documented column, type/default, primary key, foreign key, uniqueness, and required constraint.
- Verify the exact users_profile schema and seed row, including the documented profile identity and cash value 10000.0; verify exactly the ten documented watchlist tickers and no extras.
- Enable/verify foreign keys, exercise the documented relational constraints, and run initialization twice.
Assertions:
- Assert sqlite_master/PRAGMA metadata for all six tables, columns, primary keys, foreign keys, and uniqueness/not-null constraints required by SPEC.
- Assert one exact default profile row with 10000.0 cash, one row for each required ticker, and the documented default values/types.
- Assert the second initialization succeeds and leaves the same single profile and ticker set without duplicates.

### core-market-infrastructure
Requirement: Provide the documented market-data and portfolio/trade API behavior, including validation, persistence, and error handling for the core market infrastructure routes.
Level: integration
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending
Phase: core-market-infrastructure
Scenarios:
- Exercise every SPEC route owned by this phase using the documented request and response shapes.
- Verify valid market data and portfolio/trade operations cross the HTTP, store, and SQLite boundaries; verify invalid symbols, quantities, and missing records use documented errors.
Assertions:
- Assert each documented route status, content type, decoded JSON keys/types, and persisted state.
- Assert validation and not-found/error responses do not mutate the database.

### database-portfolio-engine
Requirement: Apply the documented portfolio calculations and transaction rules to persisted positions, trades, cash, and snapshots.
Level: unit
Test file: finally/backend/app/portfolio/engine_test.py
Bead ID: pending
Phase: database-portfolio-engine
Scenarios:
- Calculate holdings, cash, totals, and performance from the documented positions and trades, including empty and multi-position portfolios.
- Apply buys, sells, insufficient-cash/holdings rejection, and snapshot persistence according to the SPEC rules.
Assertions:
- Assert exact numeric results and rounding/types required by SPEC.
- Assert rejected transactions leave balances, positions, and trade history unchanged; assert accepted transactions update each required table consistently.

### watchlist-market-ui
Requirement: Let users view the documented market/watchlist data and perform the specified watchlist interactions in the dashboard UI.
Level: ui
Test file: finally/test/watchlist-market-ui.spec.ts
Bead ID: pending
Phase: watchlist-market-ui
Scenarios:
- Load the running dashboard and verify the required watchlist symbols and market values are rendered.
- Add/remove or otherwise perform each documented watchlist interaction, including the documented invalid/empty state.
Assertions:
- Assert visible controls, symbols, values, loading/error states, and accessible labels from the SPEC.
- Assert the UI sends the documented request and reflects the persisted result without showing stale data.

### portfolio-visualisation-trading
Requirement: Render the documented portfolio visualisations and support the specified trading flow with the documented validation and result states.
Level: ui
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: pending
Phase: portfolio-visualisation-trading
Scenarios:
- Render portfolio value/holdings visualisations from the documented API data, including empty and populated states.
- Submit valid buy/sell orders and exercise invalid quantity, symbol, and insufficient-funds/holdings cases.
Assertions:
- Assert charts/summary values and labels correspond to decoded API values.
- Assert successful trades update cash, holdings, and history; assert rejected trades show the documented error and do not change displayed state.

### ai-trading-assistant
Requirement: Provide the documented assistant interaction, persistence, and response/error behavior.
Level: integration
Test file: finally/backend/tests/test_chat.py
Bead ID: pending
Phase: ai-trading-assistant
Scenarios:
- Submit a valid assistant message and retrieve the documented chat response/history shape.
- Verify empty/invalid messages and the documented unavailable-provider/error path.
Assertions:
- Assert documented status, content type, decoded JSON keys/types, and persisted chat message fields.
- Assert invalid or provider-error requests return the documented diagnostic without creating an invalid assistant record.

### application-polish
Requirement: Meet the documented application-wide responsive, accessible, navigation, loading, and error-state behavior.
Level: ui
Test file: finally/test/application-polish.spec.ts
Bead ID: pending
Phase: application-polish
Scenarios:
- Exercise the documented primary navigation and dashboard flows at supported viewport sizes.
- Verify loading, empty, API-error, and responsive/accessibility states for the shipped screens.
Assertions:
- Assert required navigation targets, visible page landmarks, keyboard-accessible controls, and responsive layout behavior.
- Assert user-visible errors and loading indicators are present and stale/placeholder content is not presented as live data.

### testing-release
Requirement: Run the documented release validation and test strategy across backend, frontend, integration, and required artifact checks.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: pending
Phase: testing-release
Scenarios:
- Run the documented backend and frontend test commands against a clean checkout and verify the required release artifacts.
- Exercise the documented end-to-end smoke path from dashboard load through market data, portfolio/trade, and assistant surfaces.
Assertions:
- Assert all required test suites and artifact checks exit successfully.
- Assert the smoke path completes with documented statuses and decoded payloads, with no missing required file or unhandled error.

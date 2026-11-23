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
- GET / serves the exported dashboard whose page title contains “FinAlly”, with “$10,000” and AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, JPM, V, and NFLX in its decoded/text content.
- When the frontend export is absent, GET / returns HTTP 503 with the documented diagnostic detail and no fallback dashboard content or placeholder HTML.
Assertions:
- Assert the documented health status, decoded JSON values, and value types.
- Assert the dashboard title contains “FinAlly”, and assert the starting amount and all ten required ticker symbols occur in decoded/text content.
- Assert missing export returns exactly 503, includes the documented diagnostic, and excludes stale dashboard/fallback HTML.

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
- Click the documented Add ticker control, type PYPL, submit it, and verify PYPL appears in the watchlist; remove it using the real remove control and verify it disappears.
- Submit the documented empty/invalid ticker interaction and verify the visible validation or error state.
Assertions:
- Assert the real add/remove controls, input, symbols, values, loading/error states, and accessible labels are visible in the DOM.
- Assert the add request and resulting DOM state include PYPL, and the remove request and resulting DOM state no longer include PYPL; assert no stale row remains after persistence.

### portfolio-visualisation-trading
Requirement: Render the documented portfolio visualisations and support the specified trading flow with the documented validation and result states.
Level: ui
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: pending
Phase: portfolio-visualisation-trading
Scenarios:
- Render portfolio value/holdings visualisations from the documented API data, including empty and populated states.
- Use the real Buy control to submit a valid order and verify cash decreases and a position is added; use the real Sell control only for an owned quantity and verify the position/cash update.
- Exercise invalid quantity, symbol, insufficient-funds, and selling-more-than-owned cases. The conflicting “sell short” wording is resolved in favor of the explicit SPEC rule that selling more than owned is rejected; do not add a short-selling test.
Assertions:
- Assert charts/summary values and labels correspond to decoded API values.
- Assert the Buy interaction changes the displayed cash and adds the purchased position, and the valid Sell interaction changes holdings/cash and history.
- Assert rejected trades show the documented error and leave displayed cash, holdings, positions, and trade history unchanged.

### ai-trading-assistant
Requirement: Provide the documented assistant interaction, persistence, and response/error behavior.
Level: integration
Test file: finally/backend/tests/test_chat.py
Bead ID: pending
Phase: ai-trading-assistant
Scenarios:
- Type a valid message into the real assistant chat control and submit it; verify the assistant response appears inline and retrieve the documented chat response/history shape.
- Verify empty/invalid messages and the documented unavailable-provider/error path.
Assertions:
- Assert the submitted message and returned assistant response are visible in the chat DOM, while the API response has the documented status, content type, decoded JSON keys/types, and persisted chat fields.
- Assert invalid or provider-error requests return the documented diagnostic without creating an invalid assistant record or displaying a fabricated response.

### application-polish
Requirement: Meet the documented application-wide responsive, accessible, navigation, loading, and error-state behavior.
Level: ui
Test file: finally/test/application-polish.spec.ts
Bead ID: pending
Phase: application-polish
Scenarios:
- Click each documented primary navigation control and verify the corresponding screen/landmark appears at supported viewport sizes.
- Trigger the documented loading, empty, and API-error states and verify their visible messages; use keyboard focus and activation on the shipped controls.
Assertions:
- Assert navigation changes the visible DOM to the expected screen, controls have accessible names and keyboard focus/activation works, and the layout remains usable at each supported viewport.
- Assert loading indicators, empty-state text, and API-error text are visible in the DOM, while stale or placeholder content is absent.

### testing-release
Requirement: Run the documented release validation and test strategy across backend, frontend, integration, and required artifact checks.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: pending
Phase: testing-release
Scenarios:
- Run the documented backend and frontend test commands against a clean checkout and verify the required release artifacts.
- In the running browser, load the dashboard and assert the title contains “FinAlly”, the page contains “Market Dashboard”, all ten required ticker symbols, and “$10,000”.
- Click Add ticker, type and submit PYPL, and assert PYPL appears; use the real Buy control and assert cash changes and a position is added; type and submit a chat message and assert the assistant response appears inline.
Assertions:
- Assert all required test suites and artifact checks exit successfully.
- Assert the smoke path's decoded API responses have the documented statuses, content types, keys, and types, with no missing required file or unhandled error.
- Assert the browser DOM changes after each interaction: PYPL is added, cash decreases and the purchased position appears after Buy, and the submitted message plus assistant response appear inline.

# Test Plan — Trading Portfolio Application

## Requirements → tests

### project-foundation
Requirement: The application foundation provides the configured server and client build/test entry points.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: pending (project-foundation implementation bead)
Phase: project-foundation
Scenarios:
- Start the application with the documented configuration and exercise the health/startup path.
- Run the foundation test/build entry points with the expected dependency setup.
Assertions:
- The application starts without an initialization error and exposes its configured entry point.
- The foundation packages build and their tests complete successfully.

### core-market-infrastructure
Requirement: Market infrastructure retrieves and normalizes supported market data for the requested symbol.
Level: unit
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending (core-market-infrastructure implementation bead)
Phase: core-market-infrastructure
Scenarios:
- Normalize a valid quote response and preserve symbol, price, and change values.
- Handle an upstream error, malformed payload, and unknown symbol.
Assertions:
- Valid data is returned in the domain model with the specified numeric types.
- Errors are returned rather than producing partial or fabricated market data.

### database-portfolio-engine
Requirement: Portfolio persistence and calculations support holdings, transactions, and derived portfolio values.
Level: unit
Test file: finally/backend/db/schema_test.py
Bead ID: pending (database-portfolio-engine implementation bead)
Phase: database-portfolio-engine
Scenarios:
- Add and remove transactions and calculate holdings and totals.
- Read an empty portfolio and reject invalid quantities or prices.
Assertions:
- Persisted records round-trip with their required fields and derived totals are correct.
- Invalid operations fail without changing stored state.

### watchlist-market-ui
Requirement: Users can view market quotes and add, remove, and retain symbols in a watchlist.
Level: ui
Test file: finally/test/watchlist-market-ui.spec.ts
Bead ID: pending (watchlist-market-ui implementation bead)
Phase: watchlist-market-ui
Scenarios:
- Load the watchlist and see quote data for its symbols.
- Add a valid symbol, remove it, refresh, and exercise empty and error states.
Assertions:
- The rendered list reflects add/remove actions and persisted symbols.
- Quote values, loading state, empty state, and market-error feedback are visible as specified.

### portfolio-visualisation-trading
Requirement: Users can inspect portfolio visualisations and execute supported buy and sell actions.
Level: integration
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: pending (portfolio-visualisation-trading implementation bead)
Phase: portfolio-visualisation-trading
Scenarios:
- Request portfolio summary and chart data for an empty and funded portfolio.
- Submit valid buy and sell orders and reject invalid quantities or insufficient holdings.
Assertions:
- API responses contain the required portfolio totals, time-series data, status codes, and JSON fields.
- Successful trades update holdings and invalid trades do not mutate the portfolio.

### ai-trading-assistant
Requirement: The assistant provides contextual trading guidance from portfolio and market context while handling unavailable or invalid requests safely.
Level: integration
Test file: finally/frontend/components/ChatAssistant.spec.tsx
Bead ID: pending (ai-trading-assistant implementation bead)
Phase: ai-trading-assistant
Scenarios:
- Ask a supported question with portfolio and market context.
- Submit an empty/invalid prompt and simulate an assistant-provider failure.
Assertions:
- A successful response contains the assistant answer and required contextual fields.
- Invalid input has the specified client error and provider failures are surfaced without exposing secrets.

### application-polish
Requirement: The application presents responsive, accessible, and consistent loading, error, and navigation behavior.
Level: ui
Test file: finally/frontend/app/polish.test.tsx
Bead ID: pending (application-polish implementation bead)
Phase: application-polish
Scenarios:
- Navigate between market, watchlist, portfolio, trading, and assistant views at desktop and narrow viewport sizes.
- Trigger loading, empty, validation, and server-error states and use keyboard navigation.
Assertions:
- Navigation and responsive layout remain usable and the active view is identifiable.
- Controls have accessible names/focus behavior and state feedback is clear without console-breaking errors.

### testing-release
Requirement: The completed application passes the prescribed automated test, build, and release verification checks.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: pending (testing-release implementation bead)
Phase: testing-release
Scenarios:
- Run the documented unit, integration, UI, build, and release checks against a clean setup.
- Exercise the release artifact/startup smoke path.
Assertions:
- All required checks pass and the artifact is produced with the expected application entry points.
- The release smoke test starts successfully and no required route or asset is missing.

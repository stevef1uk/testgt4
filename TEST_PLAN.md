# Test Plan — testgt4

## Requirements → tests

### project-foundation
Requirement: The application foundation starts successfully and provides the configured application shell and health behavior specified by the project contract.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: te-0oc
Phase: project-foundation
Scenarios:
- Start the application with the documented configuration and verify the foundation initializes.
- Exercise the foundation health/readiness behavior and its failure path.
Assertions:
- Initialization succeeds with valid configuration and reports failure for invalid configuration.
- The health response has the documented status and decoded JSON values.

### core-market-infrastructure
Requirement: Market infrastructure retrieves and serves the specified market data through the documented API routes.
Level: integration
Test file: finally/internal/api/handlers_test.go
Bead ID: pending
Phase: core-market-infrastructure
Scenarios:
- Request each documented market-data route with valid parameters.
- Exercise missing, malformed, and unavailable-symbol inputs.
Assertions:
- Successful responses use the documented status/content type and contain the required decoded fields.
- Invalid requests return the documented client error and unavailable data returns the documented error without leaking internal details.

### database-portfolio-engine
Requirement: The portfolio store and engine persist, retrieve, and calculate portfolio holdings and values according to the specified data model and rules.
Level: unit
Test file: finally/internal/portfolio/portfolio_test.go
Bead ID: pending
Phase: database-portfolio-engine
Scenarios:
- Create, update, retrieve, and delete portfolio records and positions.
- Calculate positions, totals, and the documented edge cases such as empty portfolios and invalid quantities.
Assertions:
- Store operations preserve identifiers and required fields and return the documented not-found/validation errors.
- Calculations apply the specified arithmetic and remain deterministic for empty and boundary inputs.

### watchlist-market-ui
Requirement: Users can view market data and manage the documented watchlist flows in the UI.
Level: ui
Test file: finally/tests/watchlist.spec.ts
Bead ID: pending
Phase: watchlist-market-ui
Scenarios:
- Load the watchlist, add a valid symbol, remove it, and reload the page.
- Search/select a symbol and verify loading, empty, and API-error states.
Assertions:
- The UI renders the documented symbols and market values and reflects add/remove persistence.
- Controls are usable and error/empty states are visible without displaying stale or duplicate entries.

### portfolio-visualisation-trading
Requirement: Users can view portfolio visualisations and perform the documented trading flow.
Level: ui
Test file: finally/tests/portfolio-trading.spec.ts
Bead ID: pending
Phase: portfolio-visualisation-trading
Scenarios:
- Open a portfolio and verify its balance, holdings, totals, and chart.
- Submit valid and invalid buy/sell orders, including insufficient holdings or funds.
Assertions:
- The visualisation renders required values and updates after a successful trade.
- Valid trades show the documented confirmation/result; rejected trades show validation errors and do not mutate the portfolio.

### ai-trading-assistant
Requirement: The AI trading assistant accepts the documented prompt flow and returns safe, portfolio-aware responses.
Level: integration
Test file: finally/internal/assistant/assistant_test.go
Bead ID: pending
Phase: ai-trading-assistant
Scenarios:
- Send a valid assistant request with portfolio context and receive a response.
- Exercise empty/invalid prompts, provider failure, and unsafe or unsupported advice cases.
Assertions:
- The response has the documented status and decoded fields and does not expose secrets or raw provider errors.
- Invalid or failed requests return the documented error shape and do not execute trades.

### application-polish
Requirement: The application provides the specified responsive, accessible, and consistent user experience across the shipped flows.
Level: ui
Test file: finally/tests/application-polish.spec.ts
Bead ID: pending
Phase: application-polish
Scenarios:
- Navigate the primary flows at the supported viewport sizes.
- Use keyboard navigation and inspect loading, empty, error, and success states.
Assertions:
- Required navigation, labels, focus order, and responsive content remain usable.
- All documented states render without uncaught errors or broken controls.

### testing-release
Requirement: The released application passes the documented verification and regression checks.
Level: integration
Test file: finally/tests/release.spec.ts
Bead ID: pending
Phase: testing-release
Scenarios:
- Run the documented end-to-end smoke path against the release build.
- Verify the release build starts and serves the required application entry points.
Assertions:
- The release verification command completes successfully and all required routes respond.
- No smoke-path assertion fails and the build contains the required runtime assets.

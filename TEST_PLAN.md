# Test Plan — trading portfolio application

## Requirements → tests

### project-foundation
Requirement: The application foundation starts successfully and provides the configured server and client boundaries.
Level: integration
Test file: finally/backend/app/test_main.py
Bead ID: te-0oc
Phase: project-foundation
Scenarios:
- Create the FastAPI app and request `/api/health`, then request `/` after the static export exists.
- Exercise the missing `frontend/out/index.html` case and verify the diagnostic error path.
- Verify the Docker/Compose configuration, environment loading, SQLite mount, and cross-platform start/stop scripts satisfy the foundation contract.
- Run the start/stop scripts repeatedly and inspect their exit status and retained volume behavior.
Assertions:
- `create_app()` returns a FastAPI app; health returns success; the root response contains “Market Dashboard”, all ten specified tickers with price content, and `$10,000`.
- A missing export returns a diagnostic error such as 503 and does not return hardcoded placeholder HTML.
- Docker/Compose maps port 8000, loads the environment, mounts persistent database storage, and healthchecks `/api/health`; scripts resolve their own directory, are idempotent, preserve the volume, and propagate failures.

### core-market-infrastructure
Requirement: Market data is represented, validated, and served through the specified market-data API.
Level: integration
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending
Phase: core-market-infrastructure
Scenarios:
- Request the market-data route for a supported symbol and an unknown symbol.
- Exercise empty, malformed, and stale provider data at the API boundary.
Assertions:
- A valid request returns the specified decoded JSON fields, types, status, and content type.
- Unknown or invalid input returns the specified client error; provider failure does not produce a false successful payload.

### database-portfolio-engine
Requirement: Portfolio persistence and portfolio calculations obey the store contract and preserve holdings and transactions.
Level: unit
Test file: finally/backend/db/schema_test.py
Bead ID: pending
Phase: database-portfolio-engine
Scenarios:
- Create, read, update, and delete portfolio records and transactions.
- Calculate positions, cash, and gain/loss from buys, sells, and boundary quantities.
Assertions:
- Persisted values round-trip with the specified types and relationships.
- Calculations are deterministic, reject invalid quantities, and correctly handle sells and empty portfolios.

### watchlist-market-ui
Requirement: Users can view market data and manage the specified watchlist through the UI.
Level: ui
Test file: finally/tests/watchlist.spec.ts
Bead ID: pending
Phase: watchlist-market-ui
Scenarios:
- Load the market/watchlist view, add a symbol, remove it, and reload the page.
- Exercise loading, empty, invalid-symbol, and API-error states.
Assertions:
- The UI renders the specified market values and watchlist entries from the API.
- Add/remove actions call the correct API and update visible state; error and loading states are accessible and non-stale.

### portfolio-visualisation-trading
Requirement: Users can inspect portfolio visualisations and perform the specified trading flows.
Level: ui
Test file: finally/tests/portfolio-trading.spec.ts
Bead ID: pending
Phase: portfolio-visualisation-trading
Scenarios:
- Render an empty portfolio and a populated portfolio with its chart/summary.
- Submit valid buy and sell orders and attempt invalid quantities or insufficient holdings.
Assertions:
- Portfolio totals, chart data, holdings, and transaction results match the API values.
- Successful trades update the portfolio; invalid trades are blocked and display the specified error.

### ai-trading-assistant
Requirement: The assistant accepts the specified portfolio/market context and returns a safe, user-visible response.
Level: unit
Test file: finally/frontend/components/ChatAssistant.test.tsx
Bead ID: pending
Phase: ai-trading-assistant
Scenarios:
- Send a valid assistant request with market and portfolio context.
- Exercise missing input, provider failure, timeout, and unsafe/unavailable assistant responses.
Assertions:
- The endpoint validates input and returns the specified response shape, status, and content type.
- Provider failures are surfaced as the specified error without exposing secrets or inventing account actions.

### application-polish
Requirement: The completed application preserves responsive, accessible navigation and consistent loading/error behavior.
Level: ui
Test file: finally/tests/application-polish.spec.ts
Bead ID: pending
Phase: application-polish
Scenarios:
- Navigate between all specified views at desktop and narrow viewport sizes.
- Use keyboard navigation and verify loading, empty, and error states across views.
Assertions:
- Required navigation, controls, labels, focus order, and responsive layout are present.
- No route loses state unexpectedly and visible errors remain actionable and accessible.

### testing-release
Requirement: The release build and documented verification checks pass without regressing the specified application behavior.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: pending
Phase: testing-release
Scenarios:
- Run the production build and the documented test/lint checks.
- Start the release artifact and execute the critical health, market, portfolio, and UI smoke paths.
Assertions:
- All required verification commands and the production build succeed.
- The release artifact serves the specified routes and critical flows with no console or server errors.

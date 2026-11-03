# Test Plan — testgt4

## Requirements → tests

### project-foundation
Requirement: Establish the runnable project foundation, environment configuration, persistent database mount, and cross-platform Docker start/stop scripts.
Level: integration
Test file: finally/scripts/start_mac.sh
Bead ID: te-j8l
Phase: project-foundation
Scenarios:
- Verify the seven foundation files exist at their exact finally/ paths.
- Run the phase's prescribed start/stop script file verification command.
- Confirm setup artifacts are available for later application and release phases.
Assertions:
- Start and stop scripts, environment configuration, ignore rules, and database marker exist.
- The setup-only verification command succeeds without requiring an automated test runner.
- Foundation files are located under the required layout root and contain no placeholder path substitutions.

### watchlist-market-ui
Requirement: Provide the live watchlist and market UI, including the static dashboard entrypoint, SSE-driven prices, charts, and connection indicator.
Level: integration
Test file: finally/backend/app/main.py
Bead ID: 
Phase: watchlist-market-ui
Scenarios:
- Load the dashboard and verify all ten seeded tickers, prices, cash, and connection status are rendered.
- Add and remove a ticker, select tickers for the chart, and observe price updates from SSE.
- Exercise reconnect behavior and verify loading or connection feedback when the stream is interrupted.
Assertions:
- Watchlist CRUD changes are reflected in the visible DOM and duplicate/invalid operations are handled.
- Prices update, chart selection follows the clicked ticker, and price flash/sparkline elements are present.
- The connection indicator reports connected/reconnecting/disconnected states without a page failure.

### testing-release
Requirement: Deliver the exact API contracts, Playwright harness, Docker packaging, and release verification specified for this delivery phase.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: 
Phase: testing-release
Scenarios:
- Validate schemas and route methods for health, stream, portfolio, watchlist, and chat through the running service.
- Run the Playwright suite in the isolated Compose harness with LLM_MOCK=true.
- Build the production image and test Compose stack, then verify real dashboard and full user journeys.
Assertions:
- API responses match the SPEC request/response shapes and invalid trades or watchlist changes return the prescribed errors.
- E2E tests assert real tickers, prices, cash, trades, visualizations, chat output, and SSE reconnection, never status-only or placeholder content.
- Docker build, healthcheck, startup, teardown, and test runner complete successfully with the required context, mount, and port.

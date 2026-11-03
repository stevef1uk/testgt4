# Test Plan — testgt4

## Requirements → tests

### project-foundation
Requirement: Establish the runnable project foundation, environment configuration, persistent database mount, and cross-platform Docker start/stop scripts.
Level: integration
Test file: finally/scripts/start_mac.sh
Bead ID: 
Phase: project-foundation
Scenarios:
- Verify all seven foundation files exist at their exact finally/ paths.
- Run the phase's prescribed start/stop script verification command.
- Confirm environment, database mount, and ignore-rule artifacts are available for later phases.
Assertions:
- Both platform start/stop scripts, .env, .gitignore, and db/.gitkeep exist under finally/.
- The setup-only verification command succeeds without requiring an automated test runner.
- Scripts contain no placeholder path substitutions and preserve the persistent database volume.

### watchlist-market-ui
Requirement: Provide the live watchlist and market UI, including the static dashboard entrypoint, SSE-driven prices, charts, and connection indicator.
Level: integration
Test file: finally/backend/app/main.py
Bead ID: te-5fl
Phase: watchlist-market-ui
Scenarios:
- Import the application factory and verify it wires the canonical static dashboard, watchlist, and price-stream routes without a placeholder fallback.
- Exercise the dashboard contract with seeded market data: ten tickers, prices, cash, chart selection, and connection status are represented.
- Exercise watchlist add/remove behavior and consume SSE events containing ticker, price, previous price, timestamp, and direction; cover duplicate, invalid, disconnect, and reconnect states.
Assertions:
- The app imports successfully and serves the real exported index.html or a diagnostic error when it is absent, never hardcoded placeholder HTML.
- Watchlist responses and visible state contain the ten specified seed tickers, current prices, and $10,000 cash; add/remove changes are reflected and invalid/duplicate operations fail as specified.
- SSE emits correctly shaped live updates, while client-facing connected/reconnecting/disconnected indicators, price flashes, sparklines, and selected-ticker chart state remain usable.

### testing-release
Requirement: Deliver the exact API contracts, Playwright harness, Docker packaging, and release verification specified for this delivery phase.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: 
Phase: testing-release
Scenarios:
- Run the Playwright dashboard, watchlist, trading, portfolio, chat, SSE, navigation, and full happy-path scenarios through the isolated Compose harness with LLM_MOCK=true.
- Validate health, stream, portfolio, watchlist, and chat methods, request/response shapes, invalid trade/watchlist errors, and real dashboard content.
- Build and start the production image, verify healthcheck, required context/mount/port wiring, teardown, and persistence across restart.
Assertions:
- Every UI scenario asserts real tickers, prices, cash, trade results, charts, chat text, connection state, and reconnection—not status-only or placeholder content.
- API responses match the SPEC contracts and invalid operations leave cash, positions, and watchlist state unchanged.
- Docker build, healthcheck, Playwright runner, startup, and cleanup complete successfully with deterministic mock LLM behavior.


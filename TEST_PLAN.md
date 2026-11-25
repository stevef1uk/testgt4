# Test Plan — FinAlly (testgt4)

## Requirements → tests

### project-foundation
Requirement: GET / serves the real Next.js static export (dashboard heading, ten default tickers, $10,000 cash) and GET /api/health returns HTTP 200 with {"status": "ok"}.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: te-ol5
Phase: project-foundation
Scenarios:
- Export present: GET / returns the real index.html from finally/frontend/out
- Export missing: GET / returns HTTP 503 with {"error":"Frontend export unavailable"}, never a placeholder page
- GET /api/health returns HTTP 200 and status "ok"
Assertions:
- Body of GET / contains the dashboard heading text, not "Coming soon" or any placeholder string
- 503 body decodes to {"error": "Frontend export unavailable"}
- Health JSON decodes to status "ok"

### project-foundation-support
Requirement: Docker, Compose, start/stop scripts, and the Playwright test infrastructure manifest and helpers exist and load without error.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: te-ol5
Phase: project-foundation-support
Scenarios:
- Application served by the same app factory used in the Dockerfile CMD (uvicorn app.main:app on port 8010)
- Health endpoint reachable on the configured port
Assertions:
- Health check status code is 200 and JSON status is "ok"
- Static root returns the export, not a fallback page

### core-market-infrastructure
Requirement: GBM simulator, MarketCache, and MassiveClient implement one interface; the SSE generator emits ticker, price, previous price, timestamp, and direction for each update.
Level: unit
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending (future phase; no bead in bd list yet)
Phase: core-market-infrastructure
Scenarios:
- GBM next price is positive and follows the drift/volatility formula
- MarketCache update then get_latest returns the newest price and previous price
- Concurrent cache updates from multiple threads do not lose the latest value
- MassiveClient parses a canned REST response into a float price
- SSE generator emits frames with ticker, price, previous price, timestamp, and direction
Assertions:
- GBM output equals the closed-form value for fixed inputs
- Cache get_latest returns the last written price for each ticker
- Parsed Massive price equals the fixture value
- SSE frames are text/event-stream data lines whose decoded JSON contains the required keys

### database-portfolio-engine
Requirement: Lazy SQLite initialization seeds $10,000 cash and the ten default tickers; trades execute at market price and update cash and positions; snapshots are recorded after each trade.
Level: unit
Test file: finally/backend/tests/test_portfolio.py
Bead ID: pending (future phase; no bead in bd list yet)
Phase: database-portfolio-engine
Scenarios:
- Fresh init seeds user "default" with cash 10000.0 and ten watchlist tickers
- Buy reduces cash and creates a position with average cost
- Selling more than owned is rejected and leaves the position unchanged
- Buying with insufficient cash is rejected and leaves cash unchanged
- Snapshot recorded after trade execution
Assertions:
- Cash equals 10000.0 minus quantity times price after a buy
- Position quantity and avg_cost match expected values
- Rejected trades raise a validation error and state is unchanged
- Snapshot total_value equals cash plus position market value

### watchlist-market-ui
Requirement: Watchlist add/remove works in the UI; the ten default tickers render with $ prices; each row has a sparkline; the connection status indicator is visible.
Level: ui
Test file: finally/test/watchlist-market-ui.spec.ts
Bead ID: pending (future phase; no bead in bd list yet)
Phase: watchlist-market-ui
Scenarios:
- Default ten tickers render with prices matching \$[\d,.]+
- Type PYPL in the add-ticker input, click add, and PYPL appears in the list
- Click remove on AAPL, AAPL disappears, and nine rows remain
- Adding duplicate AAPL does not create a second row
- Each ticker row contains an SVG or canvas sparkline
Assertions:
- getByText for each default ticker is visible on load
- After add, getByText('PYPL') is visible; after remove, getByText('AAPL') is not visible
- Element with test id connection-status is visible

### portfolio-visualisation-trading
Requirement: Market buy and sell update cash, the positions table, and portfolio value; the heatmap and P&L chart render from current positions; insufficient cash and overselling show visible errors.
Level: ui
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: pending (future phase; no bead in bd list yet)
Phase: portfolio-visualisation-trading
Scenarios:
- Enter AAPL, quantity 10, click Buy: cash decreases by 10 times the current price and a row with quantity 10 appears
- With an AAPL position, enter quantity 5, click Sell: cash increases and quantity drops to 5
- Quantity 999999 Buy shows an error and cash is unchanged
- Quantity 999999 Sell shows an error and position is unchanged
- Heatmap test id portfolio-heatmap contains colored rectangles; test id pnl-chart has data points
Assertions:
- Cash text changes by the expected amount after each trade
- Positions table row shows ticker AAPL and quantity 10
- Error message text is visible after each rejected trade

### ai-trading-assistant
Requirement: Chat returns structured JSON (message, trades, watchlist_changes); valid trades auto-execute with the same validation as manual trades; malformed LLM output is handled safely; LLM_MOCK=true gives deterministic responses; the chat panel renders user messages and a loading spinner while pending.
Level: unit
Test file: finally/backend/tests/test_chat.py
Bead ID: pending (future phase; no bead in bd list yet)
Phase: ai-trading-assistant
Scenarios:
- LLM_MOCK=true returns identical responses for identical inputs
- System prompt includes cash, positions, and watchlist context
- Valid structured JSON yields message plus trade and watchlist actions
- Malformed JSON falls back to a safe error message without crashing
- Trade intent with insufficient cash is reported back in the response
- Companion component test finally/frontend/components/ChatAssistant.test.tsx: user message renders after send; spinner shown only while pending
Assertions:
- Decoded response keys include message, trades, watchlist_changes
- Mock outputs are equal across two calls
- Prompt string contains the formatted cash balance and tickers
- getByText returns the user message; loading indicator present only while pending

### application-polish
Requirement: Dark terminal theme (background near #0d1117 or #1a1a2e), price-flash fade of about 500ms, professional empty states, and stable behavior under live streaming.
Level: ui
Test file: finally/test/application-polish.spec.ts
Bead ID: pending (future phase; no bead in bd list yet)
Phase: application-polish
Scenarios:
- Body background color is close to #0d1117 or #1a1a2e
- A price change applies a flash class that is removed after the transition
- Empty portfolio shows a visible empty state with total value $10,000
Assertions:
- Computed body background-color matches the dark theme palette
- Flash class present right after a price update and absent after about 600ms

### testing-release
Requirement: SSE reconnects after a disconnect; selecting a ticker updates the main chart; the MVP happy path covers load, buy, sell, watchlist add/remove, chat, and heatmap.
Level: ui
Test file: finally/test/specs/sse.spec.ts
Bead ID: pending (future phase; no bead in bd list yet)
Phase: testing-release
Scenarios:
- At least three tickers change price within 10 seconds of load
- Connection status returns to green after the SSE stream is restarted
- Clicking AAPL sets the main chart heading to AAPL; clicking MSFT switches it
- Full happy path: buy 5 AAPL, sell 3 AAPL, add PYPL, remove NFLX, chat, verify heatmap (finally/test/specs/mvp.spec.ts)
Assertions:
- Price text differs between two samples for at least three tickers
- Connection status reports the connected state
- Chart heading equals the selected ticker
- Cash and position figures change as expected after each trade

## Coverage summary
- 9 test-carrying phases covered; project-foundation and project-foundation-support share finally/backend/app/main_test.py (companion of te-ol5).
- Levels: 2 integration (foundation phases), 3 unit (market, portfolio, chat backend), 4 ui (watchlist, trading, polish, release); the chat component test is a companion unit test under ai-trading-assistant.
- Future-phase bead IDs are pending until planning creates them; active-phase bead te-ol5 is the source owner for main_test.py.

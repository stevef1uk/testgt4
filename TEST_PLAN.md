# Test Plan — FinAlly

## Requirements → tests

### project-foundation
Requirement: Root route serves the real dashboard HTML (heading, ten default tickers, $10,000 cash) and never a placeholder; health route returns HTTP 200 with status ok.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: closed
Phase: project-foundation
Scenarios:
- Root route with finally/frontend/out/index.html present returns the exported dashboard
- Root route with the export missing returns HTTP 503 with a diagnostic body
- Health route returns HTTP 200 with status ok
Assertions:
- Body contains the dashboard heading and the ten default ticker symbols
- Body contains the $10,000 cash figure
- 503 body contains "Frontend export unavailable" and no placeholder text

### core-market-infrastructure
Requirement: GBM simulator, shared price cache, and MassiveClient REST parsing behave per SPEC Section 6.
Level: unit
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: closed
Phase: core-market-infrastructure
Scenarios:
- GBM step produces a positive price matching the formula
- MarketCache update then get_latest returns the new price and retains the previous price
- MassiveClient parses a canned REST response into a price
- Concurrent cache updates do not lose writes
Assertions:
- GBM price equals expected value within tolerance
- Cache returns exact stored price and previous price
- Parsed Massive price equals fixture price field

### database-portfolio-engine
Requirement: Trades update cash, positions, and snapshots correctly; seed gives $10,000 cash and ten default tickers.
Level: unit
Test file: finally/backend/tests/test_portfolio.py
Bead ID: closed
Phase: database-portfolio-engine
Scenarios:
- Buy reduces cash and creates a position with average cost
- Sell more than owned is rejected and leaves state unchanged
- Buy with insufficient cash is rejected
- Snapshot is recorded after a trade
Assertions:
- cash_balance equals prior cash minus quantity times price
- Position quantity and avg_cost equal expected values
- Rejected trades return an error and change no cash or positions

### watchlist-market-ui
Requirement: Fresh load shows the ten default tickers with dollar-prefixed prices; adding PYPL adds a row; removing AAPL removes its row.
Level: ui
Test file: finally/test/watchlist-market-ui.spec.ts
Bead ID: closed
Phase: watchlist-market-ui
Scenarios:
- Dashboard renders the watchlist panel with ten default tickers and dollar-prefixed price cells
- Type PYPL into the add input and click add; row count goes 10 to 11
- Click remove on AAPL; row count goes 11 to 10
Assertions:
- Each default ticker symbol is visible on load
- Price cells match the pattern $[\d,.]+
- Watchlist row count is 10, then 11, then 10

### portfolio-visualisation-trading
Requirement: Buy and sell from the trade bar update cash and positions in the DOM; a rejected trade leaves cash unchanged and shows an error; heatmap and P&L chart render live portfolio data after a trade.
Level: ui
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: closed
Phase: portfolio-visualisation-trading
Scenarios:
- Buy 2 AAPL via the trade bar: cash decreases and the positions table lists AAPL with quantity 2
- Heatmap and P&L chart contain rendered content for a non-empty portfolio
Assertions:
- Cash after buy equals prior cash minus 2 times displayed AAPL price
- Positions row contains ticker AAPL and quantity 2
- Heatmap and P&L chart contain rendered elements or data points

### ai-trading-assistant
Requirement: Mock chat returns deterministic replies and trade intents; prompt and portfolio context are formatted; invalid input and LLM failure degrade safely.
Level: unit
Test file: finally/backend/tests/test_chat.py
Bead ID: te-62z
Phase: ai-trading-assistant
Scenarios:
- System prompt names "FinAlly, an AI trading assistant"
- "buy 5 msft" parses to MSFT, buy, 5.0
- Non-trade text yields no trade; empty input returns None without raising
- Non-positive quantity returns None
- A failing LiteLLM call returns the fallback reply with trade None
Assertions:
- Trade dict values match exactly
- Context string contains "1000.00", "AAPL", and "NVDA"
- Fallback reply equals "The assistant is unavailable right now." with trade None

Requirement: ChatAssistant disables send while input is empty or pending, posts to the chat endpoint, renders replies, and shows a failure message on network error.
Level: unit
Test file: finally/frontend/components/ChatAssistant.test.tsx
Bead ID: closed
Phase: ai-trading-assistant
Scenarios:
- Send is disabled until input has text
- Submit posts {"message": "buy 5 MSFT"} and renders the reply
- A rejected fetch renders the failure message
Assertions:
- fetch is called with method POST and the exact JSON body
- Reply and user message are rendered
- Failure text "Request failed. Please try again." is rendered exactly

Requirement: User sends a trade command in the chat panel and sees the assistant reply in the DOM.
Level: ui
Test file: finally/test/specs/chat.spec.ts
Bead ID: te-id0
Phase: ai-trading-assistant
Scenarios:
- Type "buy 5 msft", click Send, and the assistant reply appears
- User message appears before the assistant reply; input is cleared after send
Assertions:
- Reply "Executed buy 5 MSFT." is visible in the conversation list
- User message index is less than reply index
- Input value is empty after send

Requirement: After a buy through the trade bar, the positions table shows the bought quantity and cash is below $10,000.
Level: ui
Test file: finally/test/specs/portfolio.spec.ts
Bead ID: te-6ba
Phase: ai-trading-assistant
Scenarios:
- Fresh load, buy 10 AAPL via the trade bar, then read the positions table
Assertions:
- AAPL row contains "10" in the quantity column
- Cash figure is less than 10000
- Positions row count increases by one

### application-polish
Requirement: Dark terminal theme from SPEC Section 2 (background #0d1117, foreground #e6edf3) applies to the rendered dashboard, with real dashboard content visible.
Level: ui
Test file: finally/test/application-polish.spec.ts
Bead ID: te-dom
Phase: application-polish
Scenarios:
- Load the dashboard at the root route and read computed body background and text colour
- Dashboard shows brand, heading, watchlist and cash balance
Assertions:
- Computed body background equals rgb(13, 17, 23)
- Computed body colour equals rgb(230, 237, 243)
- Brand text, heading text, and "$10,000" are visible

### testing-release
Requirement: SSE stream endpoint is opened by the dashboard on load and delivers text/event-stream responses without page errors (SPEC Section 6 SSE Streaming; SPEC Section 13 SSE Streaming).
Level: ui
Test file: finally/test/specs/sse.spec.ts
Bead ID: te-os5
Phase: testing-release
Scenarios:
- Loading the root route triggers a response with Content-Type text/event-stream
- Loading the root route opens the stream without any uncaught page error
Assertions:
- The stream response is ok and its Content-Type contains text/event-stream
- The collected pageerror list is empty

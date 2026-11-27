# Test Plan — FinAlly

## Requirements → tests

### project-foundation
Requirement: GET api/health returns success; the root path returns the real dashboard (FinAlly heading, ten default tickers, $10,000 cash) and a 503 diagnostic when the export is missing; no placeholder page.
Level: integration
Test file: finally/backend/tests/test_health.py
Bead ID: te-sj3
Phase: project-foundation
Scenarios:
- GET api/health returns 200 with a healthy status body
- root path with export absent returns 503 with a diagnostic body, not a placeholder
- create_app wires the health route and static fallback
Assertions:
- health JSON status field equals the healthy value
- 503 body names the missing frontend/out/index.html
- response body never contains placeholder text such as "Coming soon"

### project-foundation-support
Requirement: SQLite schema is created lazily on first start; seed provides ten default tickers and $10,000 cash for user "default"; Next.js export builds to frontend/out.
Level: unit
Test file: finally/backend/tests/test_schema.py
Bead ID: pending
Phase: project-foundation-support
Scenarios:
- empty database file triggers table creation and seeding
- second startup does not duplicate seed rows
- watchlist holds exactly AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX
Assertions:
- users_profile row id "default" has cash_balance 10000.0
- watchlist count for user "default" equals 10 with the exact tickers
- UNIQUE constraint on (user_id, ticker) rejects duplicates

### core-market-infrastructure
Requirement: Market data uses one abstract interface; the GBM simulator produces valid positive prices; Massive REST parsing maps to the same PriceTick format; provider is chosen by MASSIVE_API_KEY (empty selects the simulator); the SSE stream emits a named event frame followed by a data line.
Level: unit
Test file: finally/backend/tests/test_market.py
Bead ID: te-uag
Phase: core-market-infrastructure
Scenarios:
- GBM simulator yields a positive price for every generated tick
- Massive REST payload parses into the common PriceTick record
- empty MASSIVE_API_KEY selects the simulator provider
- PriceCache update replaces the latest tick per ticker and returns it on get
- price_events yields a named "event:" frame with a "data:" line
Assertions:
- price > 0 for every generated tick
- Massive parse returns ticker and price equal to the REST payload values
- provider selection returns the simulator when the key is empty
- both implementations are subclasses of PriceSource and implement its abstract methods
- SSE frame starts with "event: " and carries a "data: " line with JSON

### database-portfolio-engine
Requirement: Buys and sells update cash and positions; selling more than owned and buying with insufficient cash are rejected; snapshots are recorded after trades.
Level: unit
Test file: finally/backend/tests/test_portfolio.py
Bead ID: closed
Phase: database-portfolio-engine
Scenarios:
- buy reduces cash and creates position with average cost
- sell reduces quantity and realises P&L against average cost
- oversell and insufficient cash raise validation errors
- snapshot recorded after an accepted trade
Assertions:
- cash_balance after buy equals prior cash minus quantity times price
- average cost recalculated correctly after second buy
- rejected trades leave cash and positions unchanged

### watchlist-market-ui
Requirement: Watchlist CRUD routes add, reject duplicates, and remove tickers; GET lists the ten seeded tickers with shape asserted.
Level: integration
Test file: finally/backend/tests/test_watchlist_api.py
Bead ID: te-8sc
Phase: watchlist-market-ui
Scenarios:
- GET api/watchlist returns the ten seeded tickers with their documented shape
- POST api/watchlist adds a ticker and a subsequent GET includes it
- duplicate ticker POST is rejected and the list is unchanged
- DELETE api/watchlist/{ticker} removes the ticker and a subsequent GET no longer includes it
Assertions:
- GET watchlist contains the added ticker after POST
- duplicate returns an error and list length is unchanged
- ticker absent from GET after DELETE

### portfolio-visualisation-trading
Requirement: Buy and sell through the trade route change cash, positions and valuation.
Level: integration
Test file: finally/backend/tests/test_trading_flow.py
Bead ID: closed
Phase: portfolio-visualisation-trading
Scenarios:
- buy via route then sell part reflects new quantity and cash
- total valuation changes as price moves
Assertions:
- cash after buy and after sell matches arithmetic on returned prices
- position quantity equals bought minus sold
- total_value equals cash plus market value of positions

### ai-trading-assistant
Requirement: Chat responses never expose raw JSON; the parser accepts reply, response, message, content, action, error and suggestion keys; trades from chat auto-execute with validation; LLM_MOCK=true is deterministic; prompts embed live prices such as AAPL ($190.50).
Level: unit
Test file: finally/backend/tests/test_llm.py
Bead ID: te-la7
Phase: ai-trading-assistant
Scenarios:
- each reply key variant parses to conversational text
- action JSON such as buy AAPL 2 becomes a confirmation string
- malformed or empty model output yields a graceful fallback
- prompt context includes watchlist prices in the AAPL ($190.50) format
- mock mode returns identical output for identical input
- ChatAssistant renders bubbles, thinking state, trade badges and unwraps stringified JSON (finally/frontend/components/ChatAssistant.test.tsx, Level unit)
Assertions:
- parsed reply is non-empty and contains no leading brace
- chat bubble text equals the unwrapped reply with no braces visible
- loading text "Copilot is thinking" is present while pending; badge text matches "Trade Fill: SIDE QTY TICKER"
- trade with insufficient cash is reported in the chat response
- prompt string contains each watchlist ticker with its live price

### testing-release
Requirement: Playwright E2E covers dashboard, trading, chat and SSE with real browser interactions and DOM state-change assertions; the backend API contract test covers every SPEC Section 8 route.
Level: ui
Test file: finally/test/e2e.spec.ts
Bead ID: te-7by, te-2iz
Phase: testing-release
Scenarios:
- root path shows the FinAlly heading, the ten default tickers and the $10,000 cash balance (e2e.spec.ts)
- Buy 5 AAPL reduces cash and adds a position row (e2e.spec.ts, real click plus DOM state change)
- Add and remove watchlist ticker updates the DOM (e2e.spec.ts)
- Send chat message shows an assistant reply (e2e.spec.ts)
- full API contract: every SPEC Section 8 route responds with the specified shape, and the root path shows the FinAlly heading, ten tickers and $10,000 (finally/backend/tests/test_api.py, Level integration, bead te-2iz)
Assertions:
- response bodies carry the documented keys and types; dashboard HTML contains real content strings, not placeholder text
- cash text decreases after Buy
- ticker text appears or disappears in the watchlist
- assistant bubble has non-empty text and no raw JSON

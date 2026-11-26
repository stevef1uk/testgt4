# Implementation plan — phase watchlist-market-ui (Watchlist & Market UI)

Scope: the 7 `required_files` for this phase only. Backend portfolio/market/schema work from database-portfolio-engine is already complete and is not re-planned. Later phases (chat, portfolio UI, PnL/heatmap, polish) are out of scope and deferred.

Phase verify (run by QA): `test -f finally/backend/app/api/routes_watchlist.py && test -f finally/frontend/components/Header.tsx && test -f finally/frontend/components/Sidebar.tsx && test -f finally/frontend/components/MarketOverview.tsx && test -f finally/frontend/components/Watchlist.tsx && test -f finally/frontend/components/PriceChart.tsx && (cd finally/backend && uv run pytest tests/test_watchlist_api.py -q) && (cd finally/frontend && npm run build)`

## Bead map

### te-421: finally/backend/app/api/routes_watchlist.py
- Scope: FastAPI router for watchlist CRUD, mounted under `/api`.
- Architecture: watchlist-market-ui phase; SPEC Section 8 watchlist routes.
- Interfaces: `GET /api/watchlist` returns the current ticker list with latest prices; `POST /api/watchlist` takes body `{ticker}` and adds it; `DELETE /api/watchlist/{ticker}` removes it.
- Depends on: finally/backend/app/db/schema.sql, finally/backend/app/db/connection.py (watchlist table, existing from earlier phase).
- Consumed by: finally/backend/app/main.py (router registration), finally/backend/tests/test_watchlist_api.py.
- Acceptance:
  - GET returns the seeded default 10 tickers in order.
  - POST with a new ticker persists it and a subsequent GET includes it.
  - POST with a duplicate ticker is rejected (no second row created, error response returned).
  - DELETE removes the ticker and a subsequent GET omits it.
  - Responses are JSON bodies with the ticker fields, not status codes alone.
- Verify: `cd finally/backend && uv run pytest tests/test_watchlist_api.py -q`

### te-8sc: finally/backend/tests/test_watchlist_api.py
- Scope: pytest coverage for the watchlist routes.
- Architecture: SPEC unit test structure; `test_watchlist_api.py` covers add, duplicate rejection, removal.
- Interfaces: uses the FastAPI test client against the app from finally/backend/app/main.py.
- Depends on: te-421 (finally/backend/app/api/routes_watchlist.py).
- Consumed by: QA phase verify.
- Acceptance:
  - Test add: after POST, GET body contains the new ticker.
  - Test duplicate rejection: second POST of same ticker returns an error and GET list length is unchanged.
  - Test removal: after DELETE, GET body no longer contains the ticker.
  - Assertions check response body content and list contents, not only status codes.
- Verify: `cd finally/backend && uv run pytest tests/test_watchlist_api.py -q`

### te-u5d: finally/frontend/components/Header.tsx
- Scope: top header bar with app title and connection status indicator.
- Architecture: SPEC Section 2 visual design; connection dot green=connected, yellow=reconnecting, red=disconnected.
- Interfaces: default export component `Header` taking a `connectionStatus` prop of `'connected' | 'reconnecting' | 'disconnected'`.
- Depends on: none within this phase (consumed by page composition in app/page.tsx).
- Consumed by: finally/frontend/app/page.tsx.
- Acceptance:
  - Renders a dot whose color matches the connection status prop for all three states.
  - Dark theme colors from the palette (no pure black backgrounds).
- Verify: `cd finally/frontend && npm run build`

### te-abf: finally/frontend/components/MarketOverview.tsx
- Scope: market overview panel showing the streamed ticker prices in a data-dense grid.
- Architecture: watchlist-market-ui phase; consumes SSE price stream.
- Interfaces: default export component `MarketOverview` taking the current prices map and returning a grid of ticker, price, change.
- Depends on: finally/frontend/components/Watchlist.tsx (shared price rows) when present.
- Consumed by: finally/frontend/app/page.tsx.
- Acceptance:
  - Each ticker in the prices map renders a row with its latest price.
  - Price changes trigger the green/red flash class that fades over about 500ms.
- Verify: `cd finally/frontend && npm run build`

### te-u08: finally/frontend/components/PriceChart.tsx
- Scope: main detailed price chart for the selected ticker.
- Architecture: SPEC Section 2, clicking a ticker shows a larger chart in the main area; sparkline data accumulated on the frontend from the SSE stream since page load.
- Interfaces: default export component `PriceChart` taking `ticker` and a `points` array of `{time, price}`.
- Depends on: SSE stream data supplied by page.tsx.
- Consumed by: finally/frontend/app/page.tsx.
- Acceptance:
  - Renders a chart for the selected ticker using the points passed in.
  - Empty points render an empty state, not a crash.
- Verify: `cd finally/frontend && npm run build`

### te-78a: finally/frontend/components/Sidebar.tsx
- Scope: left sidebar container that hosts the watchlist and navigation.
- Architecture: watchlist-market-ui phase layout; desktop-first wide-screen layout.
- Interfaces: default export component `Sidebar` taking `children`.
- Depends on: none within this phase.
- Consumed by: finally/frontend/app/page.tsx.
- Acceptance:
  - Renders its children inside a fixed-width dark panel.
- Verify: `cd finally/frontend && npm run build`

### te-1n1: finally/frontend/components/Watchlist.tsx
- Scope: watchlist grid with live prices, per-ticker sparkline, price flash, and add/remove controls.
- Architecture: SPEC Section 2, watchlist with sparklines filling in progressively; add/remove via the watchlist routes.
- Interfaces: default export component `Watchlist` taking `tickers`, `prices`, `onSelect`, `onAdd`, `onRemove`.
- Depends on: finally/backend/app/api/routes_watchlist.py (GET/POST/DELETE /api/watchlist).
- Consumed by: finally/frontend/components/Sidebar.tsx host, finally/frontend/app/page.tsx.
- Acceptance:
  - Lists the tickers passed in with their latest price.
  - Clicking a ticker calls `onSelect` with that ticker symbol.
  - Sparkline is built from accumulated stream points, not a fetched history.
  - Add and remove call their handlers with the exact ticker string.
- Verify: `cd finally/frontend && npm run build`

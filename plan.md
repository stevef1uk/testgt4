# Implementation plan — watchlist-market-ui

Phase scope: Watchlist CRUD routes, header with connection status, watchlist with sparklines and price flash, main price chart. Only the seven required_files for this phase are in scope. Later-phase files (portfolio, chat, positions, trading panel) are deferred and get their own beads.

Completion rule: te-421 (routes_watchlist.py) and te-8sc (test_watchlist_api.py) must both be implemented and closed. Backend tests are the behavioral gate for the API; `npm run build` is the compile gate for the frontend, and the frontend acceptance below adds behavioral assertions on top of it.

## Bead map

### te-421: finally/backend/app/api/routes_watchlist.py
- Scope: Watchlist CRUD HTTP routes for the default watchlist.
- Architecture: GET /api/watchlist, POST /api/watchlist with body `{ticker}`, DELETE /api/watchlist/{ticker}.
- Interfaces: router exposing the three routes above, using the watchlist repository from the database layer.
- Depends on: <none> for the route definitions; database seed (ten default tickers AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX) must already exist.
- Consumed by: te-8sc (tests) and the frontend Watchlist/Sidebar beads via HTTP.
- Acceptance: GET returns the ten seeded tickers with shape asserted by tests, not status code alone.
- Acceptance: POST adds a new ticker and a subsequent GET includes it.
- Acceptance: POST of an already-present ticker is rejected and the list is unchanged.
- Acceptance: DELETE removes the ticker and a subsequent GET no longer includes it.
- Verify: cd finally/backend && uv run pytest tests/test_watchlist_api.py -q

### te-8sc: finally/backend/tests/test_watchlist_api.py
- Scope: pytest coverage for watchlist add, duplicate rejection, and removal.
- Architecture: tests add, duplicate rejection, removal; assertions check returned values and state changes, not status codes alone.
- Interfaces: pytest test functions exercising the routes in te-421.
- Depends on: te-421.
- Consumed by: phase QA command.
- Acceptance: add test asserts the ticker appears in the GET response after POST.
- Acceptance: duplicate test asserts the list content is unchanged after a rejected POST.
- Acceptance: removal test asserts the ticker is absent from the list after DELETE.
- Verify: cd finally/backend && uv run pytest tests/test_watchlist_api.py -q

### te-u5d: finally/frontend/components/Header.tsx
- Scope: app title, connection status indicator, live cash balance.
- Architecture: title "FinAlly"; connection indicator with data-testid="connection-status"; cash balance with data-testid="cash-balance".
- Interfaces: default-exported Header component; accepts connection state (connected, reconnecting, disconnected) and cash balance as props or from the shared store.
- Depends on: <none>.
- Consumed by: page.tsx (mounted in this phase).
- Acceptance: renders a heading with accessible name "FinAlly".
- Acceptance: element with data-testid="connection-status" shows green for connected, yellow for reconnecting, red for disconnected (distinct class or aria-label per state).
- Acceptance: element with data-testid="cash-balance" renders the cash value formatted as currency.
- Verify: cd finally/frontend && npm run build

### te-78a: finally/frontend/components/Sidebar.tsx
- Scope: sidebar container hosting the watchlist and market overview regions.
- Architecture: layout container per architecture frontend section.
- Interfaces: default-exported Sidebar component wrapping Watchlist and MarketOverview children.
- Depends on: te-1n1, te-abf.
- Consumed by: page.tsx.
- Acceptance: renders both child regions in the DOM.
- Acceptance: no duplicate watchlist heading is rendered.
- Verify: cd finally/frontend && npm run build

### te-abf: finally/frontend/components/MarketOverview.tsx
- Scope: market overview panel listing ticker rows with live prices and percentage change.
- Architecture: aria-label "Market overview" on the region.
- Interfaces: default-exported MarketOverview component consuming the price stream state.
- Depends on: <none>.
- Consumed by: Sidebar.tsx, page.tsx.
- Acceptance: region has aria-label "Market overview".
- Acceptance: each row shows symbol, current price, and daily change percent.
- Acceptance: a price update from the stream changes the rendered price for that row.
- Verify: cd finally/frontend && npm run build

### te-1n1: finally/frontend/components/Watchlist.tsx
- Scope: watchlist grid with ticker rows, price flash, sparklines, and add/remove controls.
- Architecture: heading "Watchlist"; region aria-label="Watchlist"; EventSource on /api/stream/prices.
- Interfaces: default-exported Watchlist component; add posts to /api/watchlist with `{ticker}`; remove calls DELETE /api/watchlist/{ticker}.
- Depends on: te-421 (HTTP contract).
- Consumed by: Sidebar.tsx, page.tsx.
- Acceptance: each ticker row exposes symbol, price, change percent, and a sparkline SVG or canvas element.
- Acceptance: on a price tick that is higher than the previous price, the price element gains a green flash class; lower gives a red flash class; the class is removed after about 500ms.
- Acceptance: each received tick appends to that ticker's sparkline series, so the series grows with stream updates since page load and starts empty on fresh load.
- Acceptance: add control submits the ticker and the new row appears; remove control deletes the row by calling the DELETE route.
- Acceptance: duplicate add shows no second row.
- Verify: cd finally/frontend && npm run build

### te-u08: finally/frontend/components/PriceChart.tsx
- Scope: main price chart area for the selected ticker.
- Architecture: chart labelled "price chart" for accessibility.
- Interfaces: default-exported PriceChart component taking the selected ticker and its accumulated price series.
- Depends on: <none>.
- Consumed by: page.tsx.
- Acceptance: region has an accessible label matching /price chart/i.
- Acceptance: with no accumulated data the chart renders an empty state rather than crashing.
- Acceptance: with accumulated points the chart renders one plotted point per tick received.
- Verify: cd finally/frontend && npm run build

## Future considerations
- Portfolio totals, positions, trading panel, and chat belong to later phases and are not in these beads.

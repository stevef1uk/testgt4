# Implementation plan — portfolio-visualisation-trading

Active phase covers exactly six implement beads. Later phases get their own beads and are out of scope here.

Canonical phase verification (run from test4/mayor/rig):
`test -f finally/frontend/components/PortfolioSummary.tsx && test -f finally/frontend/components/TradingPanel.tsx && test -f finally/frontend/components/PositionsTable.tsx && test -f finally/frontend/components/PnlChart.tsx && test -f finally/frontend/components/PortfolioHeatmap.tsx && test -f finally/backend/tests/test_trading_flow.py && (cd finally/backend && uv run pytest tests/test_portfolio_api.py tests/test_trading_flow.py -q) && (cd finally/frontend && npm run build)`

## Portfolio HTTP contract (SPEC Section 8, exact)

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/portfolio | Current positions, cash balance, total value, unrealized P&L |
| POST | /api/portfolio/trade | Execute a trade: `{ticker, quantity, side}` |
| GET | /api/portfolio/history | Portfolio value snapshots over time (for P&L chart) |

No aliases or extra routes. Backend and tests must use these paths verbatim.

## Gate: te-733 must close

te-733 is currently in_progress. Plan acceptance is not complete until te-733 reaches closed status through implementation and QA. Planning does not close beads; QA verifies closure before plan acceptance.

## Bead map

### te-yiq: finally/frontend/components/PortfolioSummary.tsx
- Scope: Summary card showing total portfolio value, cash balance, and unrealized P&L from GET /api/portfolio.
- Architecture: architecture.md, frontend components section for portfolio visualisation.
- Interfaces: default-exported React component; consumes GET /api/portfolio response only.
- Depends on: <none> from this phase.
- Consumed by: finally/frontend/app pages that mount the portfolio view.
- Acceptance:
  - Renders total value, cash, and unrealized P&L from the GET /api/portfolio response.
  - Shows positive and negative P&L with distinct styling.
  - Handles empty portfolio without crashing.
- Verify: cd finally/frontend && npm run build

### te-2gr: finally/frontend/components/TradingPanel.tsx
- Scope: Buy/sell order entry form for a single ticker with quantity input and submit action.
- Architecture: architecture.md, trading panel section.
- Interfaces: default-exported React component; posts `{ticker, quantity, side}` to POST /api/portfolio/trade.
- Depends on: <none> from this phase.
- Consumed by: finally/frontend/app pages that mount the trading view.
- Acceptance:
  - Rejects non-positive quantities before submitting.
  - Submits buy and sell orders with ticker, side, and quantity to POST /api/portfolio/trade.
  - Displays server error messages returned by the trade endpoint.
- Verify: cd finally/frontend && npm run build

### te-350: finally/frontend/components/PositionsTable.tsx
- Scope: Table of open positions with ticker, quantity, average cost, market value, and unrealized P&L.
- Architecture: architecture.md, positions table section.
- Interfaces: default-exported React component taking positions array as props.
- Depends on: <none> from this phase.
- Consumed by: finally/frontend/app pages that mount the portfolio view.
- Acceptance:
  - One row per position with all five columns populated.
  - Shows an empty-state message when there are no positions.
- Verify: cd finally/frontend && npm run build

### te-3sl: finally/frontend/components/PnlChart.tsx
- Scope: Line chart of portfolio value over time from GET /api/portfolio/history.
- Architecture: architecture.md, P&L chart section.
- Interfaces: default-exported React component taking snapshot series as props.
- Depends on: finally/frontend/components/PortfolioSummary.tsx (shares snapshot data shape).
- Consumed by: finally/frontend/app pages that mount the portfolio view.
- Acceptance:
  - Plots one point per snapshot in chronological order.
  - Renders an empty chart placeholder when history is empty.
- Verify: cd finally/frontend && npm run build

### te-y8k: finally/frontend/components/PortfolioHeatmap.tsx
- Scope: Heatmap of positions sized by market value and coloured by P&L percentage.
- Architecture: architecture.md, portfolio heatmap section.
- Interfaces: default-exported React component taking positions array as props.
- Depends on: finally/frontend/components/PositionsTable.tsx (same positions data shape).
- Consumed by: finally/frontend/app pages that mount the portfolio view.
- Acceptance:
  - Each position appears as one tile with ticker label.
  - Colour reflects sign and magnitude of P&L percentage.
- Verify: cd finally/frontend && npm run build

### te-733: finally/backend/tests/test_trading_flow.py
- Scope: End-to-end backend test of buy then sell through POST /api/portfolio/trade, checking cash and positions via GET /api/portfolio.
- Architecture: architecture.md, testing section for trading flow.
- Interfaces: test module only; exercises the three routes in the contract table above.
- Depends on: finally/backend/tests/test_portfolio_api.py (shared fixtures, run in the same canonical pytest command).
- Consumed by: none.
- Acceptance:
  - A buy reduces cash and creates a position.
  - A full sell removes the position and restores cash.
  - Selling more than held is rejected.
- Verify: cd finally/backend && uv run pytest tests/test_portfolio_api.py tests/test_trading_flow.py -q

## Future considerations
- Any behaviour not in SPEC.md is deferred and not added to these beads.

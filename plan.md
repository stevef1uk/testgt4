# Implementation plan — portfolio-visualisation-trading

Active phase covers exactly six implement beads. Later phases get their own beads and are out of scope here.

## Bead map

### te-yiq: finally/frontend/components/PortfolioSummary.tsx
- Scope: Summary card showing total portfolio value, cash balance, and aggregate P&L from the portfolio API.
- Architecture: architecture.md, frontend components section for portfolio visualisation.
- Interfaces: default-exported React component; consumes portfolio summary data only (no new API routes).
- Depends on: <none> from this phase (reads portfolio API data shape defined in architecture.md).
- Consumed by: finally/frontend/app pages that mount the portfolio view.
- Acceptance:
  - Renders total value, cash, and unrealised P&L values from SPEC portfolio data.
  - Shows positive and negative P&L with distinct styling.
  - Handles empty portfolio without crashing.
- Verify: cd finally/frontend && npm run build

### te-2gr: finally/frontend/components/TradingPanel.tsx
- Scope: Buy/sell order entry form for a single ticker with quantity input and submit action.
- Architecture: architecture.md, trading panel section.
- Interfaces: default-exported React component; posts trade requests to the trade endpoint in SPEC.
- Depends on: <none> from this phase.
- Consumed by: finally/frontend/app pages that mount the trading view.
- Acceptance:
  - Rejects non-positive quantities before submitting.
  - Submits buy and sell orders with ticker, side, and quantity.
  - Displays server error messages returned by the trade endpoint.
- Verify: cd finally/frontend && npm run build

### te-350: finally/frontend/components/PositionsTable.tsx
- Scope: Table of open positions with ticker, quantity, average cost, market value, and unrealised P&L.
- Architecture: architecture.md, positions table section.
- Interfaces: default-exported React component taking positions array as props.
- Depends on: <none> from this phase.
- Consumed by: finally/frontend/app pages that mount the portfolio view.
- Acceptance:
  - One row per position with all five columns populated.
  - Shows an empty-state message when there are no positions.
- Verify: cd finally/frontend && npm run build

### te-3sl: finally/frontend/components/PnlChart.tsx
- Scope: Line chart of portfolio value over time from snapshot history.
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
- Scope: End-to-end backend test of buy then sell through the trade API, checking cash and positions update.
- Architecture: architecture.md, testing section for trading flow.
- Interfaces: test module only; exercises existing trade and portfolio endpoints.
- Depends on: finally/backend/tests/test_portfolio_api.py (shared fixtures, already closed).
- Consumed by: none.
- Acceptance:
  - A buy reduces cash and creates a position.
  - A full sell removes the position and restores cash.
  - Selling more than held is rejected.
- Verify: cd finally/backend && uv run pytest tests/test_trading_flow.py -q

## Future considerations
- Any behaviour not in SPEC.md is deferred and not added to these beads.

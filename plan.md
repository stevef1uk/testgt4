# Implementation plan — portfolio-visualisation-trading

Scope: Phase 5 (Portfolio Visualisation & Trading) only. Bead IDs come from `bd list --limit=0 --status=open` in this session. Paths match `required_files` in architecture.md exactly. No beads are created or deleted by this amendment.

## Bead map

### te-733: finally/backend/tests/test_trading_flow.py
- Scope: End-to-end trading flow tests through the trade route, asserting state changes in cash, positions and valuation.
- Architecture: architecture.md, "Unit tests" (test_trading_flow.py) and "Module / bead ownership" (portfolio/engine.py owns execute_trade).
- Interfaces: exercises POST /api/portfolio/trade with body `{ticker, quantity, side}` and GET /api/portfolio, GET /api/portfolio/history (SPEC Section 8).
- Depends on: finally/backend/app/portfolio/engine.py, finally/backend/app/api/routes_portfolio.py (database-portfolio-engine phase).
- Consumed by: none (test-only file).
- Acceptance:
  - Buy with sufficient cash decreases cash by quantity times the cached price and creates a position with that quantity.
  - Sell reduces the position quantity and increases cash by quantity times the price.
  - Buy with insufficient cash is rejected; cash and positions are unchanged.
  - Sell of more shares than owned is rejected; position is unchanged.
  - After each trade, GET /api/portfolio total value equals cash plus position market value.
  - Each executed trade adds a snapshot visible in GET /api/portfolio/history.
  - Assertions check returned figures, not status codes alone.
- Verify: `(cd finally/backend && uv run pytest tests/test_trading_flow.py -q)`

### te-3sl: finally/frontend/components/PnlChart.tsx
- Scope: P&L line chart of total portfolio value over time, data from portfolio_snapshots.
- Architecture: architecture.md, "Portfolio Visualisation & Trading" requirements; SPEC Section 10 (P&L chart).
- Interfaces: React component `PnlChart` rendering `data-testid="pnl-chart"`; reads GET /api/portfolio/history.
- Depends on: GET /api/portfolio/history (database-portfolio-engine).
- Consumed by: finally/frontend/app/page.tsx (application-polish phase).
- Acceptance:
  - Renders a canvas or SVG with one data point per snapshot returned by /api/portfolio/history.
  - Shows an empty state when there are no snapshots; does not render a placeholder value.
  - Updates after a trade triggers a refetch.
  - Uses the dark theme colours from SPEC Section 2 (#209dd7 line accent).
- Verify: `(cd finally/frontend && npm run build)`

### te-y8k: finally/frontend/components/PortfolioHeatmap.tsx
- Scope: Treemap heatmap; each rectangle is a position sized by portfolio weight and coloured by unrealised P&L.
- Architecture: architecture.md, "Portfolio Visualisation & Trading"; SPEC Section 10 (Portfolio heatmap).
- Interfaces: React component `PortfolioHeatmap` rendering `data-testid="portfolio-heatmap"`; reads GET /api/portfolio.
- Depends on: GET /api/portfolio (database-portfolio-engine).
- Consumed by: finally/frontend/app/page.tsx (application-polish phase).
- Acceptance:
  - One rectangle per open position, sized proportionally to market value.
  - Profitable positions are green-tinted, losing positions red-tinted.
  - Renders an explicit empty state when there are no positions.
  - Rectangles are labelled with the ticker text.
- Verify: `(cd finally/frontend && npm run build)`

### te-2gr: finally/frontend/components/TradingPanel.tsx
- Scope: Trade entry bar: ticker input, quantity input, Buy and Sell buttons, inline status and error messages.
- Architecture: architecture.md, "Portfolio Visualisation & Trading"; SPEC Section 10 (Trade bar) and Section 2 (market orders only).
- Interfaces: React component `TradingPanel` with `data-testid="trading-panel"`; calls POST /api/portfolio/trade with `{ticker, quantity, side}`.
- Depends on: POST /api/portfolio/trade (database-portfolio-engine).
- Consumed by: finally/frontend/app/page.tsx (application-polish phase).
- Acceptance:
  - Buy button submits a buy order; the cash and position figures visible on the page update afterwards.
  - Sell button submits a sell order and updates the same figures.
  - Insufficient cash or oversell responses display an error message and leave figures unchanged.
  - Quantity and ticker inputs are real controls that accept typed values.
  - Market orders only: no price or limit field.
- Verify: `(cd finally/frontend && npm run build)`

### te-350: finally/frontend/components/PositionsTable.tsx
- Scope: Table of open positions.
- Architecture: architecture.md, "Portfolio Visualisation & Trading"; SPEC Section 10 (Positions table).
- Interfaces: React component `PositionsTable` with `data-testid="positions-table"`; reads GET /api/portfolio.
- Depends on: GET /api/portfolio (database-portfolio-engine).
- Consumed by: finally/frontend/app/page.tsx (application-polish phase).
- Acceptance:
  - Columns: ticker, quantity, average cost, current price, unrealised P&L, % change.
  - Rows reflect the positions returned by GET /api/portfolio, with real numbers.
  - After a buy, the new ticker row appears with the bought quantity.
  - Shows an empty state with no rows when the portfolio is empty.
- Verify: `(cd finally/frontend && npm run build)`

### te-yiq: finally/frontend/components/PortfolioSummary.tsx
- Scope: Summary panel showing total portfolio equity, cash balance and unrealised P&L.
- Architecture: architecture.md, "Portfolio Visualisation & Trading"; SPEC Section 10 (Header portfolio value) and Section 12 (portfolio display).
- Interfaces: React component `PortfolioSummary` with `data-testid="portfolio-summary"`; reads GET /api/portfolio.
- Depends on: GET /api/portfolio (database-portfolio-engine).
- Consumed by: finally/frontend/app/page.tsx (application-polish phase).
- Acceptance:
  - Displays total value, cash and unrealised P&L from GET /api/portfolio figures (not hardcoded).
  - A fresh portfolio shows $10,000 total and $10,000 cash.
  - Figures refresh after a trade.
- Verify: `(cd finally/frontend && npm run build)`

## Phase context

Phase gate (must pass before the phase advances): `test -f finally/frontend/components/PortfolioSummary.tsx && test -f finally/frontend/components/TradingPanel.tsx && test -f finally/frontend/components/PositionsTable.tsx && test -f finally/frontend/components/PnlChart.tsx && test -f finally/frontend/components/PortfolioHeatmap.tsx && test -f finally/backend/tests/test_trading_flow.py && (cd finally/backend && uv run pytest tests/test_portfolio_api.py tests/test_trading_flow.py -q) && (cd finally/frontend && npm run build)`

Interactive requirement: every frontend component in this phase must expose at least one real control or state-changing behaviour (button, input or fetch). Static content-only components are not acceptance.

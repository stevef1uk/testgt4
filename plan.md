# Core Market Infrastructure implementation plan

This plan covers only the active `core-market-infrastructure` phase. Closed beads are retained as validated artifacts; open beads own the remaining work. No later portfolio, UI, chat, database, or entrypoint implementation is assigned here.

## Bead map

### te-d40: finally/backend/app/api/__init__.py
- Scope: Provide the API package boundary and architecture-defined FastAPI route-registration surface without a second app entrypoint.
- Architecture: `architecture.md` API module ownership and HTTP integration contract; preserve SPEC §8.
- Interfaces / Depends on / Consumed by: Export the architecture-defined registration/factory helpers; Depends on: `finally/backend/app/api/schemas.py`, `finally/backend/app/market/sse.py`; Consumed by: `finally/backend/app/main.py`.
- Acceptance: Import succeeds and registration preserves exactly `/api/stream/prices`, `/api/portfolio`, `/api/portfolio/trade`, `/api/portfolio/history`, `/api/watchlist`, `/api/watchlist/{ticker}`, `/api/chat`, and `/api/health`, using shared schemas.
- Verify: `PYTHONPATH=finally/backend python -c "import app.api"`

### te-1kp: finally/backend/app/api/schemas.py
- Scope: Preserve validated Pydantic contracts for watchlist, quotes, trades, portfolio, history, and chat.
- Architecture: Schema ownership in `architecture.md`; SPEC §8 is authoritative.
- Interfaces / Depends on / Consumed by: Export `WatchlistRequest`, `WatchlistItem`, `TradeRequest`, `TradeResponse`, `PortfolioPosition`, `PortfolioResponse`, `HistoryPoint`, `PortfolioHistory`, `ChatRequest`, `ChatAction`, and `ChatResponse`; Depends on: `<none>`; Consumed by: API registration and market tests.
- Acceptance: Enforce non-empty strings, positive quantities, buy/sell literals, non-negative prices, direction literals, list defaults, optional fields, and forbidden extras exactly as specified.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-5pa: finally/frontend/next-env.d.ts
- Scope: Supply Next.js and market runtime declarations for the TypeScript static export.
- Architecture: Frontend declaration ownership in `architecture.md`.
- Interfaces / Depends on / Consumed by: Declare `FINALLY_RUNTIME_CONFIG` with environment, marketEndpoint, reconnectDelayMs and `FINALLY_MARKET_QUOTE` with ticker, price, timestamp; Depends on: `<none>`; Consumed by: frontend compilation.
- Acceptance: Include Next/image references; environment is development/production/test; quote fields have specified types; declarations add no runtime behavior.
- Verify: `(cd finally/frontend && npm run build)`

### te-ddu: finally/backend/tests/test_market_infrastructure.py
- Scope: Test functional market infrastructure, not file existence.
- Architecture: Core-market-infrastructure requirement and test ownership in `architecture.md`; SPEC §§6 and 12.
- Interfaces / Depends on / Consumed by: Exercise GBM, Massive, cache, SSE, and schemas; Depends on: `finally/backend/app/market/gbm.py`, `finally/backend/app/market/massive.py`, `finally/backend/app/market/cache.py`, `finally/backend/app/market/sse.py`, `finally/backend/app/api/schemas.py`; Consumed by: phase QA.
- Acceptance: Assert GBM seeded repeatability/non-negative prices; Massive parsing and provider interchangeability; cache latest/previous/timestamp/all/clear/validation; SSE framing and direction fields; schema valid/invalid cases.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-9xh: finally/backend/app/market/sse.py
- Scope: Implement frontend-facing SSE framing and canonical market-event payloads.
- Architecture: SSE ownership in `architecture.md`; SPEC §6.
- Interfaces / Depends on / Consumed by: Export `encode_event(payload, *, event=None, event_id=None) -> str`, `market_event(ticker, price, previous_price=None, timestamp=None) -> dict[str, Any]`, and `stream_events(events, *, event=None) -> Iterator[str]`; Depends on: `finally/backend/app/market/cache.py`; Consumed by: API registration and tests.
- Acceptance: Emit optional id/event lines, compact JSON data, blank-line framing, ticker/price/previous_price/timestamp/change_direction, and reject empty tickers or negative prices.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-ljx: finally/backend/app/market/cache.py
- Scope: Implement the shared thread-safe latest-price cache.
- Architecture: Cache ownership in `architecture.md`; SPEC §6.
- Interfaces / Depends on / Consumed by: Export `PriceSnapshot` and `MarketCache.update`, `get`, `latest`, `previous`, `all`, `clear`; Depends on: `<none>`; Consumed by: SSE, provider coordination, and tests.
- Acceptance: Track prior prices, preserve timestamps, normalize naive timestamps, implement all/latest/previous/clear, reject invalid ticker/price, and protect access with locking.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-i12: finally/backend/app/market/gbm.py
- Scope: Implement the seeded geometric-Brownian-motion simulator/provider interface.
- Architecture: GBM ownership/provider interchangeability in `architecture.md`; SPEC §6.
- Interfaces / Depends on / Consumed by: Preserve every public GBM symbol/signature defined by architecture; Depends on: `<none>`; Consumed by: provider consumers and tests.
- Acceptance: Apply initial price, drift, volatility, timestep, and seed behavior; sequences repeat, prices remain non-negative, and the required ticker universe is supported without database or SSE formatting.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-9gi: finally/backend/app/market/massive.py
- Scope: Implement the optional Massive REST adapter using the same provider contract as GBM.
- Architecture: Massive ownership and environment selection in `architecture.md`; SPEC §§5–6.
- Interfaces / Depends on / Consumed by: Preserve every public Massive/provider and quote-normalization symbol defined by architecture; Depends on: `finally/backend/app/market/gbm.py`; Consumed by: provider selection and tests.
- Acceptance: Non-empty `MASSIVE_API_KEY` selects the adapter, empty configuration permits simulation, REST data normalizes to ticker/price/timestamp, required tickers work, and parsing is testable without live network access.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

## Phase acceptance

Run exactly:
`test -f finally/backend/app/api/__init__.py && test -f finally/backend/app/api/schemas.py && test -f finally/frontend/next-env.d.ts && test -f finally/backend/tests/test_market_infrastructure.py && PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py && (cd finally/frontend && npm run build)`

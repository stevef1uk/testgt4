# Core Market Infrastructure implementation plan

## Scope and verification

This phase owns only the eight required files below. It delivers the market provider abstraction, GBM simulator, Massive adapter, shared cache, SSE serialization/streaming, API package contracts, frontend Next type declarations, and their focused tests. Do not implement later portfolio, watchlist routes, chat, or UI behavior. Every implementation follows `architecture.md` ownership and SPEC Sections 6, 8, and 12. The phase gate is:
`test -f finally/backend/app/api/__init__.py && test -f finally/backend/app/api/schemas.py && test -f finally/frontend/next-env.d.ts && test -f finally/backend/tests/test_market_infrastructure.py && PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py && (cd finally/frontend && npm run build)`.

## Bead map

### te-a9g: finally/backend/app/api/__init__.py
- Scope: Provide the API package required by the backend layout without creating a second application entrypoint.
- Architecture: `architecture.md` Module / bead ownership and core-market-infrastructure required_files.
- Interfaces: importable `app.api` package; route-registration helpers only where required by the architecture.
- Depends on: `<none>`
- Consumed by: `finally/backend/app/api/schemas.py` and later API/main integration.
- Acceptance: the package imports successfully; it contains no placeholder route behavior, duplicate FastAPI app, or side effects; its ownership remains compatible with the canonical SPEC route table.
- Verify: `PYTHONPATH=finally/backend python -c "import app.api"`

### te-1kp: finally/backend/app/api/schemas.py
- Scope: Implement the Pydantic contracts used by watchlist, market, portfolio, history, trade, and chat APIs.
- Architecture: `architecture.md` schemas ownership; SPEC Section 8 request/response shapes.
- Interfaces: `WatchlistRequest`, `WatchlistItem`, `TradeRequest`, `TradeResponse`, `PortfolioPosition`, `PortfolioResponse`, `HistoryPoint`, `PortfolioHistory`, `ChatRequest`, `ChatAction`, and `ChatResponse`.
- Depends on: `finally/backend/app/api/__init__.py`
- Consumed by: later API handlers and `finally/backend/tests/test_market_infrastructure.py`.
- Acceptance: non-empty ticker/message validation works; trade quantity is positive; prices are non-negative; `buy`/`sell` and `up`/`down`/`unchanged` literals are enforced; extra fields are forbidden; list defaults are independent empty lists; declared datetime/string timestamps and chat action details are accepted.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-5pa: finally/frontend/next-env.d.ts
- Scope: Preserve Next.js type references and declare the architecture's runtime market configuration boundary.
- Architecture: `architecture.md` frontend type boundary; SPEC Sections 6 and 10.
- Interfaces: `FinAllyEnvironment`, `Stream`, `RuntimeConfig`, `MarketQuote`, `FINALLY_ENVIRONMENT`, `FINALLY_RUNTIME_CONFIG`, and `FINALLY_MARKET_QUOTE`.
- Depends on: `<none>`
- Consumed by: later frontend EventSource/dashboard code and the production build.
- Acceptance: Next/image references remain; environment is development/production/test; stream exposes endpoint and reconnect delay; quote exposes ticker, numeric price, and timestamp; frontend build passes.
- Verify: `(cd finally/frontend && npm run build)`

### te-pop: finally/backend/app/market/cache.py
- Scope: Implement the thread-safe shared latest-price cache.
- Architecture: `architecture.md` cache ownership; SPEC Section 6 Shared Price Cache.
- Interfaces: frozen `PriceSnapshot`; `MarketCache.update`, `get`, `latest`, `previous`, `all`, and `clear`.
- Depends on: `<none>`
- Consumed by: `finally/backend/app/market/sse.py`, provider/background integration in later main work, and the market tests.
- Acceptance: each update records ticker, current price, previous price, and timestamp; timestamps are timezone-aware; empty tickers and negative prices are rejected; missing values return `None`; `all()` is a copy; `clear()` empties the cache; concurrent access cannot corrupt values.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-dak: finally/backend/app/market/gbm.py
- Scope: Implement the simulator/provider side of the shared market-data interface using seeded GBM prices.
- Architecture: `architecture.md` GBM ownership and core-market-infrastructure requirement; SPEC Section 6 Simulator.
- Interfaces: the architecture-defined GBM provider/configuration and seeded-price generation entry points; no database or SSE formatting ownership.
- Depends on: `finally/backend/app/market/cache.py`
- Consumed by: later provider selection/background task and `finally/backend/tests/test_market_infrastructure.py`.
- Acceptance: generated prices are valid and non-negative; configured initial prices and requested tick counts are honored; equal seeds reproduce the same series and different seeds can vary it; drift/volatility parameters affect generation according to the GBM contract; invalid inputs follow the documented contract.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-ndc: finally/backend/app/market/massive.py
- Scope: Implement the optional Massive REST adapter using the same provider shape as GBM.
- Architecture: `architecture.md` Massive ownership and provider interchangeability; SPEC Sections 5 and 6.
- Interfaces: the architecture-defined Massive provider/client, response normalization, and fetch entry points; configuration remains environment-driven by `MASSIVE_API_KEY`.
- Depends on: `finally/backend/app/market/cache.py`
- Consumed by: later provider selection/background polling and the market tests.
- Acceptance: a Massive response is normalized to ticker, non-negative price, and timestamp; absent/empty key selects simulator elsewhere rather than requiring a network call; provider results fit the same interface as GBM; mocked responses and the documented unavailable-provider path are deterministic and testable.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-n1p: finally/backend/app/market/sse.py
- Scope: Implement canonical SSE event framing and market-event payload construction.
- Architecture: `architecture.md` SSE ownership; SPEC Section 6 SSE Streaming.
- Interfaces: `encode_event(payload, *, event=None, event_id=None)`, `market_event(ticker, price, previous_price=None, timestamp=None)`, and `stream_events(events, *, event=None)`.
- Depends on: `finally/backend/app/market/cache.py`
- Consumed by: later `/api/stream/prices` route wiring and the market tests.
- Acceptance: records use SSE `id`, optional `event`, and JSON `data` fields with the required blank-line terminator; market payloads contain ticker, price, previous price, timestamp, and change direction; direction is up/down/unchanged; empty tickers and negative prices are rejected; every input event is yielded in order.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-ddu: finally/backend/tests/test_market_infrastructure.py
- Scope: Write focused tests first for every active market contract and schema boundary.
- Architecture: `architecture.md` Unit tests and core-market-infrastructure requirement.
- Interfaces: pytest coverage for the GBM provider, Massive normalization/interchangeability, cache semantics, SSE framing/payloads, and Pydantic validation.
- Depends on: `finally/backend/app/api/__init__.py`, `finally/backend/app/api/schemas.py`, `finally/backend/app/market/cache.py`, `finally/backend/app/market/gbm.py`, `finally/backend/app/market/massive.py`, `finally/backend/app/market/sse.py`
- Consumed by: the phase gate and QA.
- Acceptance: tests prove reproducible/non-negative GBM output and tick count; mocked Massive parsing and provider shape; cache previous-price, timestamp, isolation, clear, and validation behavior; SSE fields, framing, order, and direction; schema constraints and forbidden extras. Tests must fail for missing behavior first, then pass with the implementation, and must not be import-only or always-pass.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

## Future considerations

Background task wiring, the canonical `/api/stream/prices` FastAPI route, frontend EventSource lifecycle, portfolio persistence, and dashboard behavior belong to later phase owners even though this phase defines their market-layer contracts.

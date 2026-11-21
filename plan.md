# Core Market Infrastructure implementation plan

This phase delivers only the eight active-phase files. The implementation must preserve the repository-relative `finally/` paths and the contracts in SPEC.md and architecture.md. Later API, database, UI, and entrypoint phases consume these primitives; do not pull their files into this phase.

## Verification gate

The active phase is accepted only when the following exact gate succeeds from the town root:
`test -f finally/backend/app/api/__init__.py && test -f finally/backend/app/api/schemas.py && test -f finally/frontend/next-env.d.ts && test -f finally/backend/tests/test_market_infrastructure.py && PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py && (cd finally/frontend && npm run build)`
The test file must assert behavior, not merely imports: provider determinism and validation, cache previous-price tracking, SSE framing/direction, and Pydantic request/response validation.

## Bead map

### te-wxs: finally/backend/app/api/__init__.py
- Scope: Implement the API package initializer and its documented package-level exports only; do not register future routes here.
- Architecture: Follow architecture.md API package layout and the SPEC schema/API boundary; keep imports compatible with the existing `backend.app` package.
- Interfaces: Preserve the package initializer contract and exports consumed by backend imports; no undocumented route aliases.
- Depends on: finally/backend/app/api/schemas.py
- Consumed by: finally/backend/app/main.py and later API route work.
- Acceptance: The package imports successfully under `PYTHONPATH=finally/backend`, exposes the architecture-defined API package symbols, and introduces no side effects that require database or server startup.

### te-1kp: finally/backend/app/api/schemas.py
- Scope: Implement the strict Pydantic contracts for watchlist, trade, portfolio, history, and chat payloads.
- Architecture: Use the schema definitions and field constraints in architecture.md, matching SPEC request/response shapes.
- Interfaces: `WatchlistRequest`, `WatchlistItem`, `TradeRequest`, `TradeResponse`, `PortfolioPosition`, `PortfolioResponse`, `HistoryPoint`, `PortfolioHistory`, `ChatRequest`, `ChatAction`, and `ChatResponse`.
- Depends on: <none>
- Consumed by: finally/backend/app/api/__init__.py and later route, engine, and chat phases.
- Acceptance: Valid payloads parse; blank watchlist tickers and chat messages, non-positive trade quantities, invalid trade sides, negative prices, and extra fields are rejected; portfolio/history/chat defaults serialize as the documented empty lists and action details.

### te-9gi: finally/backend/app/market/massive.py
- Scope: Implement the interchangeable Massive market-data provider defined by the architecture, including deterministic mock behavior and provider-facing quote operations.
- Architecture: Follow architecture.md market provider interface, SPEC’s ten-symbol seeded market and mock-mode requirements, and the documented Massive response normalization.
- Interfaces: Export the architecture-defined Massive provider class/functions and quote shape without renaming symbols; results expose ticker, price, and timestamp data usable by the cache.
- Depends on: <none>
- Consumed by: finally/backend/tests/test_market_infrastructure.py and later market/API wiring.
- Acceptance: Mock mode returns the documented symbols and stable, finite non-negative prices; repeated seeded requests are deterministic; configured live-provider responses normalize to the common quote contract; invalid/empty ticker inputs follow the documented validation.

### te-i12: finally/backend/app/market/gbm.py
- Scope: Implement the seeded geometric-Brownian-motion/mock market provider used for live-looking deterministic price changes.
- Architecture: Follow architecture.md GBM provider parameters, seed handling, and common market-provider interface.
- Interfaces: Export the architecture-defined GBM provider and its documented quote/stream methods; preserve reproducible seed behavior.
- Depends on: <none>
- Consumed by: finally/backend/tests/test_market_infrastructure.py and later market service/API wiring.
- Acceptance: The same seed and inputs produce the same sequence, successive generated prices are finite and non-negative, the initial/reference price is honored, and generated updates can be converted to the common ticker-price-timestamp contract.

### te-ljx: finally/backend/app/market/cache.py
- Scope: Implement the thread-safe latest-price cache and immutable price snapshot described in architecture.md.
- Architecture: Use the documented `PriceSnapshot` fields and `MarketCache` update/read semantics.
- Interfaces: Export `PriceSnapshot` and `MarketCache` with architecture-defined `update`, `get`/`latest`, `previous`, `all`, and `clear` behavior.
- Depends on: finally/backend/app/market/massive.py and finally/backend/app/market/gbm.py
- Consumed by: finally/backend/app/market/sse.py, later market/API routes, and tests.
- Acceptance: First updates have no previous price; later updates retain the immediately prior price; timestamps are timezone-aware; empty tickers and negative prices are rejected; reads and clear work safely and snapshots remain immutable.

### te-9xh: finally/backend/app/market/sse.py
- Scope: Implement canonical server-sent-event encoding and market-event construction.
- Architecture: Follow architecture.md SSE wire format and SPEC live-price stream requirements.
- Interfaces: Export `encode_event`, `market_event`, and `stream_events` with their documented arguments and return framing.
- Depends on: finally/backend/app/market/cache.py
- Consumed by: later API streaming routes and frontend market subscription code.
- Acceptance: Events use `id`, optional `event`, compact JSON `data`, and the required blank-line terminator; market events include ticker, price, previous price, timestamp, and `up`/`down`/`unchanged`; streams yield one correctly framed record per input and reject invalid ticker/price values.

### te-0vr: finally/frontend/next-env.d.ts
- Scope: Provide the Next.js, image, CSS-module, and environment-variable declarations required by the existing frontend build.
- Architecture: Match the canonical frontend layout and TypeScript declaration content in architecture.md; do not add application behavior.
- Interfaces: Next.js reference declarations, `*.module.css` default export, and the documented `ProcessEnv` keys.
- Depends on: <none>
- Consumed by: later frontend components and `npm run build`.
- Acceptance: TypeScript recognizes Next.js and CSS-module imports, the declared environment names are available, and the frontend production build passes.

### te-ddu: finally/backend/tests/test_market_infrastructure.py
- Scope: Add focused unit tests for every active market primitive and schema contract.
- Architecture: Implement the architecture.md test matrix for providers, cache, SSE, and Pydantic validation; tests must be deterministic and isolated.
- Interfaces: Pytest tests consume the exact exported symbols from the five backend implementation modules and schemas; no production behavior is hidden in fixtures.
- Depends on: finally/backend/app/api/__init__.py, finally/backend/app/api/schemas.py, finally/backend/app/market/massive.py, finally/backend/app/market/gbm.py, finally/backend/app/market/cache.py, finally/backend/app/market/sse.py
- Consumed by: the active phase verification gate and later regression runs.
- Acceptance: Tests prove deterministic seeded/mock prices, common quote validation, cache previous-price and clear semantics, SSE framing and direction, and rejection/acceptance of the SPEC schema cases; `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py` passes.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

## Future considerations

Database persistence, route registration, application startup, frontend market UI, trading, chat, Docker, and end-to-end tests belong to later delivery phases and are intentionally not acceptance criteria for this phase.

# Core Market Infrastructure Plan

This phase covers exactly the eight active required files. It implements the market contracts in SPEC Sections 6 and 8 without adding later portfolio, watchlist UI, chat, or application-entrypoint behavior.

## Verification

The polecat must run:
`test -f finally/backend/app/api/__init__.py && test -f finally/backend/app/api/schemas.py && test -f finally/frontend/next-env.d.ts && test -f finally/backend/tests/test_market_infrastructure.py && PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py && (cd finally/frontend && npm run build)`

## Bead map

### te-wxs: finally/backend/app/api/__init__.py
- Scope: Preserve the importable API package and route-registration/factory boundary defined by architecture.md; do not add a second application entrypoint.
- Architecture: Module/bead ownership table, API package row; canonical route ownership remains aligned with the SPEC route table.
- Interfaces: Export the API package surface specified by architecture.md and keep `app.api` importable.
- Depends on: <none>
- Consumed by: te-1kp; te-x1n; later entrypoint/API integration.
- Acceptance: `PYTHONPATH=finally/backend` imports `app.api` successfully, with no divergent routes or speculative later-phase behavior.

### te-1kp: finally/backend/app/api/schemas.py
- Scope: Implement the Pydantic request/response contracts for the canonical watchlist, portfolio, trade, history, and chat APIs.
- Architecture: Schemas ownership row and `core-market-infrastructure` requirement; field names and request shapes must match SPEC Section 8 exactly.
- Interfaces: Export the schema classes and fields specified by architecture.md for ticker, price, portfolio, trade, history, watchlist, and chat contracts.
- Depends on: te-wxs
- Consumed by: te-x1n; later API and entrypoint phases.
- Acceptance: Valid documented payloads validate and serialize with exact field names; malformed required fields and invalid negative price values are rejected; this module contains no persistence or polling.

### te-9gi: finally/backend/app/market/massive.py
- Scope: Implement the optional Massive REST adapter and its common provider-compatible quote representation.
- Architecture: Massive ownership row; environment behavior from SPEC requires selection when `MASSIVE_API_KEY` is non-empty and simulator fallback otherwise.
- Interfaces: Export the provider, quote, and parsing symbols named by architecture.md; quote data includes ticker, price, and timestamp for cache consumers.
- Depends on: te-1kp
- Consumed by: te-x1n; later provider coordination and entrypoint work.
- Acceptance: Documented Massive responses parse into the shared quote shape; the adapter conforms to the same provider interface as GBM; deterministic tests do not require network access or a live key.

### te-i12: finally/backend/app/market/gbm.py
- Scope: Implement the default geometric Brownian motion simulator with realistic seed prices and controllable randomness.
- Architecture: GBM ownership row and SPEC Section 6 simulator requirements.
- Interfaces: Export the GBM simulator/provider interface and seeded-price generation symbols specified by architecture.md, including documented seed/configuration controls.
- Depends on: te-1kp
- Consumed by: te-x1n; te-ljx; later provider coordination and entrypoint work.
- Acceptance: Equal seeds and configurations yield equal sequences; generated prices are non-negative; initial price, drift, volatility, interval, and requested step count follow the documented contract; GBM and Massive are interchangeable downstream.

### te-ljx: finally/backend/app/market/cache.py
- Scope: Implement the shared thread-safe in-memory cache of latest price, previous price, and timestamp per ticker.
- Architecture: Cache ownership row; the cache is the single source read by SSE and later market routes.
- Interfaces: Export `PriceSnapshot` and `MarketCache` with the architecture-defined update, get/latest, previous, all, and clear methods.
- Depends on: te-i12; te-9gi
- Consumed by: te-dra; te-x1n; later background provider and API integration.
- Acceptance: First update has no previous price and subsequent updates expose the prior value; snapshots preserve ticker, float price, and timestamp; all accessors and clear follow the documented semantics; empty tickers and negative prices fail; access is thread-safe.

### te-dra: finally/backend/app/market/sse.py
- Scope: Implement canonical market-event construction and Server-Sent Event wire framing.
- Architecture: SSE ownership row plus SPEC Section 6 fields and `GET /api/stream/prices` contract.
- Interfaces: Export `market_event(ticker, price, previous_price=None, timestamp=None)`, `encode_event(payload, *, event=None, event_id=None)`, and `stream_events(events, *, event=None)` with documented types.
- Depends on: te-ljx
- Consumed by: te-x1n; later `/api/stream/prices` integration.
- Acceptance: Events contain ticker, price, previous price, timestamp, and up/down/unchanged direction; optional id/event lines are correctly framed; compact JSON data ends with the required blank line; invalid empty ticker/negative price is rejected; iterable events preserve order.

### te-x1n: finally/backend/tests/test_market_infrastructure.py
- Scope: Add pytest contract coverage for all public active-phase market and schema behavior.
- Architecture: Unit-test mapping under `core-market-infrastructure`; cover provider math/parsing, interchangeability, cache, and stream serialization.
- Interfaces: Import only public symbols from te-wxs, te-1kp, te-9gi, te-i12, te-ljx, and te-dra.
- Depends on: te-wxs; te-1kp; te-9gi; te-i12; te-ljx; te-dra
- Consumed by: phase verification and QA.
- Acceptance: Tests assert schema validation, seeded/non-negative GBM output and reproducibility, Massive parsing/common shape, cache latest/previous/timestamp/clear behavior, and exact SSE fields/framing/direction. The specified pytest command passes.

### te-9jp: finally/frontend/next-env.d.ts
- Scope: Provide Next.js and image references plus the CSS-module and environment typings needed by the existing static-export frontend.
- Architecture: Frontend declaration ownership row; retain the existing TypeScript build boundary without UI behavior.
- Interfaces: Next/image reference directives, `*.module.css` default export typing, and documented `NODE_ENV` and `NEXT_PUBLIC_APP_URL` environment declarations.
- Depends on: <none>
- Consumed by: existing frontend TypeScript sources and the phase build gate.
- Acceptance: No placeholder or unresolved declarations remain; CSS modules and documented environment variables type-check; `(cd finally/frontend && npm run build)` succeeds.

## Phase boundary

Do not implement portfolio persistence, watchlist CRUD, frontend market components, chat, background lifecycle wiring, or new HTTP routes here. Those responsibilities belong to later delivery phases; this phase supplies only their documented market primitives and schema/build prerequisites.

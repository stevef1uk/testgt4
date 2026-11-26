# Implementation plan: core-market-infrastructure

## Phase scope

Active phase: `core-market-infrastructure`. Only the nine `required_files` are in scope. Each path has exactly one implement bead. No beads are created for `database-portfolio-engine`, `watchlist-market-ui`, or later phases.

Deferred finding: the secret-scanner finding on `finally/scripts/start_mac.sh` belongs to `project-foundation`, which owns that file in architecture.md. It does not block this phase. QA should route it to that phase.

## Rework amendments

- te-3v3 (`__init__.py`) and te-kre (`uv.lock`) were closed on partial evidence. Their acceptance below is restated so the phase verify is the gate, not compile-only checks.
- te-0gb (`simulator.py`) acceptance requires behavioural checks through `tests/test_market.py`, not compile-only verification.
- te-uag (`tests/test_market.py`) is the only open implementation bead that must pass before phase success.

## Bead map

### te-3v3: finally/backend/app/market/__init__.py
- Scope: package marker exporting PriceSource, PriceTick, SimulatedPriceSource, MassiveClient, PriceCache, PricePoller through lazy PEP 562 resolution.
- Architecture: `finally/backend/app/market/` in architecture.md "Planned file layout".
- Interfaces: `__all__`, `__getattr__(name)`, `__dir__()`.
- Depends on: `<none>`.
- Consumed by: finally/backend/tests/test_market.py.
- Acceptance: importing app.market does not eagerly import submodules; each `__all__` name resolves to its class; unknown names raise AttributeError.
- Verify: `(cd finally/backend && uv run python -c "import app.market")`

### te-p9f: finally/backend/app/market/base.py
- Scope: abstract PriceSource (start, stop, add_ticker, remove_ticker, get_prices) and frozen PriceTick dataclass with validation.
- Architecture: SPEC Section 6 "Two Implementations, One Interface". Naming gap recorded under Future considerations.
- Interfaces: `PriceTick(ticker: str, price: float, timestamp: datetime)`; abstract async PriceSource methods.
- Depends on: `<none>`.
- Consumed by: te-0gb, te-v6q, te-l4f, te-96m, te-ekt, te-3v3.
- Acceptance: empty ticker and negative price raise ValueError; PriceTick is frozen; PriceSource cannot be instantiated without all abstract methods.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k "tick or interface")`

### te-l4f: finally/backend/app/market/cache.py
- Scope: in-memory PriceCache holding the latest tick per ticker, guarded by asyncio.Lock.
- Architecture: SPEC Section 6 "Shared Price Cache"; no network calls.
- Interfaces: `async update(tick)`, `async get(ticker)`, `async get_all()`, `async remove(ticker)`, `async clear()`, `__len__`.
- Depends on: te-p9f.
- Consumed by: te-ekt, te-96m, te-0gb.
- Acceptance: update replaces the previous tick; get on an unknown ticker returns None; remove on an unknown ticker does not raise; get_all returns a snapshot list.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k cache)`

### te-0gb: finally/backend/app/market/simulator.py
- Scope: SimulatedPriceSource, a GBM generator with drift, volatility, correlated moves, occasional 2–5% events, and SPEC seed prices (AAPL ~190).
- Architecture: SPEC Section 6 "Simulator (Default)"; in-process, no external dependencies.
- Interfaces: implements PriceSource; writes to PriceCache.
- Depends on: te-p9f, te-l4f.
- Consumed by: te-96m, te-3v3.
- Acceptance: prices stay positive over many steps; default ticker seeds match SPEC scale; start/stop/add/remove behave correctly and leak no background tasks.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k simulator)`

### te-v6q: finally/backend/app/market/massive_client.py
- Scope: MassiveClient, a REST poller for the Massive (Polygon.io) API that parses responses into PriceTick.
- Architecture: SPEC Section 6 "Massive API (Optional)"; REST polling, not WebSocket.
- Interfaces: implements PriceSource; a parse helper for REST payloads.
- Depends on: te-p9f, te-l4f.
- Consumed by: te-96m, te-3v3.
- Acceptance: a recorded REST payload parses into the same PriceTick shape as the simulator; malformed payloads raise a clear error and do not write to the cache; unit tests make no network calls.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k massive)`

### te-96m: finally/backend/app/market/poller.py
- Scope: background loop selecting MassiveClient when MASSIVE_API_KEY is non-empty, otherwise the simulator, writing ticks to PriceCache.
- Architecture: SPEC Section 5 "Behavior" and Section 6; Massive free tier polls every 15 seconds.
- Interfaces: PricePoller with start/stop; provider selection from the environment without overwriting existing shell variables.
- Depends on: te-0gb, te-v6q, te-l4f, te-p9f.
- Consumed by: te-ekt, future app/main.py lifespan wiring.
- Acceptance: empty or absent MASSIVE_API_KEY selects the simulator; a non-empty key selects MassiveClient; stop() cancels the background task cleanly.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k poller)`

### te-ekt: finally/backend/app/market/stream.py
- Scope: SSE generator `price_events(cache, interval, max_events)` with named `prices` frames and heartbeat comments, plus format_sse, format_comment, tick_to_dict.
- Architecture: SPEC Section 6 "SSE Streaming" and the Event Dispatch Compatibility Rule.
- Interfaces: `tick_to_dict(tick) -> dict`; `format_sse(event, data) -> str`; `format_comment(text) -> str`; `async price_events(...)`.
- Depends on: te-p9f, te-l4f.
- Consumed by: future GET /api/stream/prices route in app/main.py.
- Acceptance: each frame is `event: prices` plus one compact JSON `data:` line and a blank line; heartbeat comments appear every HEARTBEAT_EVERY idle intervals; max_events bounds the generator.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k stream)`

### te-uag: finally/backend/tests/test_market.py
- Scope: unit tests for tick validation, cache replace/remove, simulator positivity, Massive parsing, SSE framing, and poller provider selection.
- Architecture: architecture.md "Unit tests" (`test_market.py`); SPEC Section 12 backend market tests.
- Interfaces: imports only the public surface from app.market.
- Depends on: te-3v3, te-p9f, te-l4f, te-0gb, te-v6q, te-96m, te-ekt.
- Consumed by: phase verify `uv run pytest tests/test_market.py -q`.
- Acceptance: every test asserts a returned value or state change (no `assert True`); all tests pass with LLM_MOCK unset.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q)`

### te-kre: finally/backend/uv.lock
- Scope: lockfile generated by `uv sync` from finally/backend/pyproject.toml, pinning this phase's dependencies.
- Architecture: architecture.md "Delivery phases" assigns uv.lock to core-market-infrastructure.
- Interfaces: none (generated artifact).
- Depends on: finally/backend/pyproject.toml (project-foundation).
- Consumed by: Dockerfile Stage 2 (`uv sync`).
- Acceptance: file exists and is non-empty; `uv sync --locked` in finally/backend succeeds.
- Verify: `test -f finally/backend/uv.lock && (cd finally/backend && uv sync --locked)`

## Phase verification

`test -f finally/backend/app/market/base.py && test -f finally/backend/app/market/simulator.py && test -f finally/backend/app/market/massive_client.py && test -f finally/backend/app/market/cache.py && test -f finally/backend/app/market/stream.py && test -f finally/backend/app/market/poller.py && test -f finally/backend/uv.lock && (cd finally/backend && uv run pytest tests/test_market.py -q)`

## Future considerations

- Naming gap: architecture.md names the base class `MarketDataSource` with `get_price`/`subscribe`; the validated code uses `PriceSource` with `get_prices`. Reconcile in architecture.md before consuming phases.
- start_mac.sh secret markers: owned by project-foundation; deferred.

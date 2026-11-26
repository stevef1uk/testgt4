# Implementation plan — core-market-infrastructure

## Phase scope

Active phase: `core-market-infrastructure` (SPEC Section 14.2, Phase 2). Only the nine `required_files` below are in scope. Each has exactly one implement bead, created or reused by planning sync. No bead is added for `database-portfolio-engine`, `watchlist-market-ui`, or any later phase.

Deferred review finding: the security finding against `finally/scripts/start_mac.sh` (API_KEY assignments from caller-exported env vars, missing `# allow-secret:` markers) belongs to `project-foundation`, which owns `finally/scripts/start_mac.sh` in architecture.md. It is out of scope for this phase and must not block `core-market-infrastructure`. QA should route it to the phase that owns that file.

Bead te-0gb (`simulator.py`) was closed on a compile-only verify. Its acceptance is strengthened below to require behavioural checks through `tests/test_market.py`, which the phase verify already runs.

## Bead map

### te-3v3: finally/backend/app/market/__init__.py
- Scope: package marker exporting the public market surface (PriceSource, PriceTick, SimulatedPriceSource, MassiveClient, PriceCache, PricePoller) with lazy resolution (PEP 562).
- Architecture: `finally/backend/app/market/` per architecture.md "Planned file layout"; provider selection per SPEC Section 5.
- Interfaces: `__all__`, `__getattr__(name)`, `__dir__()`.
- Depends on: `<none>` for import-time behaviour; resolves lazily to base, simulator, massive_client, cache, poller.
- Consumed by: `finally/backend/app/main.py` (future phases), `finally/backend/tests/test_market.py`.
- Acceptance:
  - `import app.market` does not import submodules eagerly.
  - Every name in `__all__` resolves through `getattr` and returns the class from its submodule.
  - Unknown names raise AttributeError.
- Verify: `(cd finally/backend && uv run python -c "import app.market")`

### te-p9f: finally/backend/app/market/base.py
- Scope: abstract `PriceSource` interface (start, stop, add_ticker, remove_ticker, get_prices) and frozen `PriceTick` dataclass with validation.
- Architecture: SPEC Section 6 "Two Implementations, One Interface"; architecture.md notes `MarketDataSource` with `get_price`/`subscribe`. The validated file uses `PriceSource` and `get_prices`. Treat the validated file as authoritative and record the naming gap under Future considerations.
- Interfaces: `PriceTick(ticker: str, price: float, timestamp: datetime)`; `PriceSource` abstract async methods.
- Depends on: `<none>`.
- Consumed by: te-0gb (simulator), te-v6q (massive_client), te-l4f (cache), te-96m (poller), te-ekt (stream), te-3v3 (`__init__`).
- Acceptance:
  - `PriceTick("", 1.0)` raises ValueError; a negative price raises ValueError.
  - `PriceTick` is immutable (frozen).
  - `PriceSource` cannot be instantiated without implementing all abstract methods.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k "tick or interface")`

### te-l4f: finally/backend/app/market/cache.py
- Scope: in-memory `PriceCache` holding the latest tick per ticker, guarded by an asyncio.Lock.
- Architecture: SPEC Section 6 "Shared Price Cache"; architecture.md Module ownership (`PriceCache`, no network calls).
- Interfaces: `async update(tick)`, `async get(ticker) -> PriceTick | None`, `async get_all() -> list[PriceTick]`, `async remove(ticker)`, `async clear()`, `__len__`.
- Depends on: te-p9f (`PriceTick`).
- Consumed by: te-ekt (stream), te-96m (poller), te-0gb (simulator writes).
- Acceptance:
  - `update` replaces the previous tick for the same ticker.
  - `get` on an unknown ticker returns None; `remove` on an unknown ticker does not raise.
  - `get_all` returns a snapshot list, not a live view.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k cache)`

### te-0gb: finally/backend/app/market/simulator.py
- Scope: `SimulatedPriceSource`, a GBM price generator with per-ticker drift and volatility, correlated moves, occasional 2–5% events, and realistic seed prices (e.g. AAPL ~190).
- Architecture: SPEC Section 6 "Simulator (Default)"; runs in-process with no external dependencies.
- Interfaces: implements `PriceSource` (start, stop, add_ticker, remove_ticker, get_prices); writes to `PriceCache`.
- Depends on: te-p9f, te-l4f.
- Consumed by: te-96m (poller selects the simulator when MASSIVE_API_KEY is empty), te-3v3.
- Acceptance:
  - Generated prices stay positive over many steps.
  - Seed prices for the ten default tickers match SPEC scale (AAPL ~190).
  - Start/stop/add/remove behave correctly and do not leak background tasks.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k simulator)` (replaces the compile-only verify)

### te-v6q: finally/backend/app/market/massive_client.py
- Scope: `MassiveClient`, a REST poller client for the Massive (Polygon.io) API that parses responses into `PriceTick` objects.
- Architecture: SPEC Section 6 "Massive API (Optional)"; REST polling, not WebSocket.
- Interfaces: implements `PriceSource`; `parse` helper for REST payloads.
- Depends on: te-p9f, te-l4f.
- Consumed by: te-96m (poller), te-3v3.
- Acceptance:
  - A recorded REST payload parses into the same `PriceTick` shape as the simulator.
  - Malformed payloads raise a clear error and do not write to the cache.
  - No network call is made in unit tests (fixtures only).
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k massive)`

### te-96m: finally/backend/app/market/poller.py
- Scope: background polling loop that selects the Massive client when `MASSIVE_API_KEY` is non-empty, otherwise the simulator, and writes ticks to `PriceCache`.
- Architecture: SPEC Section 5 "Behavior" and Section 6 "Shared Price Cache"; Massive free tier polls every 15 seconds.
- Interfaces: `PricePoller` with start/stop; provider selection from the environment without overwriting existing shell variables.
- Depends on: te-0gb, te-v6q, te-l4f, te-p9f.
- Consumed by: te-ekt (stream reads the cache), future `app/main.py` lifespan wiring.
- Acceptance:
  - An empty or absent MASSIVE_API_KEY selects the simulator.
  - A non-empty key selects MassiveClient.
  - stop() cancels the background task cleanly.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k poller)`

### te-ekt: finally/backend/app/market/stream.py
- Scope: SSE generator `price_events(cache, interval, max_events)` yielding named `prices` frames and heartbeat comments, plus `format_sse`, `format_comment`, and `tick_to_dict`.
- Architecture: SPEC Section 6 "SSE Streaming" and the Event Dispatch Compatibility Rule. The stream must yield both named events and standard data lines.
- Interfaces: `tick_to_dict(tick) -> dict`; `format_sse(event, data) -> str`; `format_comment(text) -> str`; `async price_events(...)`.
- Depends on: te-p9f, te-l4f.
- Consumed by: future `GET /api/stream/prices` route in `app/main.py`.
- Acceptance:
  - Each frame is `event: prices` followed by a single `data:` line of compact JSON, terminated by a blank line.
  - Heartbeat comments are emitted every HEARTBEAT_EVERY idle intervals.
  - `max_events` bounds the generator.
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q -k stream)`

### te-uag: finally/backend/tests/test_market.py
- Scope: unit tests for GBM validity, simulator and Massive parsing through one interface, PriceCache semantics, SSE framing, and the poller provider switch.
- Architecture: architecture.md "Unit tests" (`test_market.py`); SPEC Section 12 backend market tests.
- Interfaces: imports only the public surface from `app.market`.
- Depends on: te-3v3, te-p9f, te-l4f, te-0gb, te-v6q, te-96m, te-ekt.
- Consumed by: phase verify `uv run pytest tests/test_market.py -q`.
- Acceptance:
  - Each test asserts a returned value or state change; no `assert True` tests.
  - Tests cover: tick validation, cache replace/remove, simulator positivity, Massive parsing, SSE framing, poller provider selection.
  - All tests pass with `LLM_MOCK` unset (no LLM dependency in this phase).
- Verify: `(cd finally/backend && uv run pytest tests/test_market.py -q)`

### te-kre: finally/backend/uv.lock
- Scope: lockfile generated by `uv sync` from `finally/backend/pyproject.toml`, pinning the market phase's dependencies.
- Architecture: architecture.md "Delivery phases" assigns `finally/backend/uv.lock` to core-market-infrastructure.
- Interfaces: none (generated artifact).
- Depends on: `finally/backend/pyproject.toml` from project-foundation (already present).
- Consumed by: Dockerfile Stage 2 (`uv sync`).
- Acceptance:
  - File exists and is non-empty.
  - `uv sync` in `finally/backend` succeeds without changing the lockfile.
- Verify: `test -f finally/backend/uv.lock && (cd finally/backend && uv sync --locked)`

## Phase verification

`test -f finally/backend/app/market/base.py && test -f finally/backend/app/market/simulator.py && test -f finally/backend/app/market/massive_client.py && test -f finally/backend/app/market/cache.py && test -f finally/backend/app/market/stream.py && test -f finally/backend/app/market/poller.py && test -f finally/backend/uv.lock && (cd finally/backend && uv run pytest tests/test_market.py -q)`

## Future considerations

- Naming gap: architecture.md names the base class `MarketDataSource` with `get_price`/`subscribe`; the validated code uses `PriceSource` with `get_prices`. Reconcile in architecture.md before the consuming phases.
- `start_mac.sh` secret markers: owned by `project-foundation`; deferred as above.

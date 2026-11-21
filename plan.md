# Implementation plan

## Active phase

This plan covers only the `core-market-infrastructure` phase and its eight active required
files. Implement the market primitives and their focused tests without taking ownership of
later-phase routes, application startup, persistence, or UI components. Preserve the
project-foundation-support conventions already present in the repository.

## Verification contract

The active phase is accepted only when the following command succeeds:
`test -f finally/backend/app/api/__init__.py && test -f finally/backend/app/api/schemas.py && test -f finally/frontend/next-env.d.ts && test -f finally/backend/tests/test_market_infrastructure.py && PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py && (cd finally/frontend && npm run build)`
The test file must exercise the concrete market behaviors below; do not replace those
assertions with import-only or placeholder tests.

## Bead map

### te-mfw: finally/backend/app/api/__init__.py
- Scope: Implement the API package initializer at the exact path, retaining the package boundary required by the backend imports and exposing only the package-level API described by architecture.md.
- Architecture: Follow architecture.md's API package layout and the project Python package conventions; do not add routes or a server entrypoint in this phase.
- Interfaces / Depends on / Consumed by: Package import surface described in architecture.md; Depends on: `<none>`; Consumed by: `finally/backend/app/api/schemas.py` and later API modules.
- Acceptance: The path is a valid importable `app.api` package; imports used by the phase's tests resolve without side effects or speculative endpoints.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-kzl: finally/backend/app/api/schemas.py
- Scope: Implement the API data schemas specified by SPEC and architecture.md for market data, including required fields, types, validation, and serialization shape.
- Architecture: Use the schema ownership and model definitions in architecture.md; keep schema concerns separate from market transport, cache, and simulation behavior.
- Interfaces / Depends on / Consumed by: Export the schema classes and field contracts named in architecture.md; Depends on: `finally/backend/app/api/__init__.py`; Consumed by: `finally/backend/app/market/sse.py`, later API handlers, and `finally/backend/tests/test_market_infrastructure.py`.
- Acceptance: Valid market payloads construct and serialize with the SPEC field names; required fields and numeric values are enforced; the resulting JSON-compatible shape is suitable for SSE events and the tests assert the documented contract.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-s88: finally/frontend/next-env.d.ts
- Scope: Add the standard Next.js generated TypeScript environment declarations at the exact frontend path, matching the existing frontend configuration.
- Architecture: Follow architecture.md's frontend scaffold and Next.js type-check/build conventions; do not add UI behavior in this phase.
- Interfaces / Depends on / Consumed by: Provide the Next.js type references required by the frontend compiler; Depends on: `<none>`; Consumed by: the frontend TypeScript/build toolchain.
- Acceptance: The declaration file contains the required Next.js references and does not introduce application-specific globals; `npm run build` can type-check the existing frontend.
- Verify: `cd finally/frontend && npm run build`

### te-s54: finally/backend/app/market/cache.py
- Scope: Implement the in-memory market cache described by SPEC and architecture.md, including insertion/update, lookup, and the documented expiry or bounded-retention behavior.
- Architecture: Keep cache state in the market cache module and use the exact public names and data flow assigned in architecture.md; do not add persistence, retries, or feature flags.
- Interfaces / Depends on / Consumed by: Export the cache type/functions named in architecture.md; Depends on: `finally/backend/app/api/schemas.py`; Consumed by: `finally/backend/app/market/sse.py`, later market consumers, and `finally/backend/tests/test_market_infrastructure.py`.
- Acceptance: A newly stored market value is retrievable by its symbol/key; an update replaces the prior value; missing or expired entries follow the SPEC result; cache behavior is deterministic enough for the focused tests.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-5s3: finally/backend/app/market/massive.py
- Scope: Implement the Massive market-data client/adapter specified by architecture.md, including the documented request/response normalization and configuration usage.
- Architecture: Follow the Massive integration boundary and exported symbols in architecture.md; keep external access isolated from cache and simulation logic.
- Interfaces / Depends on / Consumed by: Export the Massive client/adapter symbols and methods named in architecture.md; Depends on: `finally/backend/app/api/schemas.py`; Consumed by: `finally/backend/app/market/sse.py` and `finally/backend/tests/test_market_infrastructure.py`.
- Acceptance: The adapter builds the SPEC-required market-data request, maps the documented response into the API schema shape, and supports the test's mocked/provider boundary without making live network calls.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-q1d: finally/backend/app/market/gbm.py
- Scope: Implement the geometric Brownian motion market simulator in architecture.md, with the SPEC-required parameters, deterministic/randomness control, and generated price behavior.
- Architecture: Use the GBM formula and exported function/type contract stated in architecture.md; keep simulation independent of transport and persistence.
- Interfaces / Depends on / Consumed by: Export the GBM function/type names and signatures from architecture.md; Depends on: `<none>`; Consumed by: `finally/backend/tests/test_market_infrastructure.py` and later simulation consumers.
- Acceptance: Simulation honors the requested starting price and step/count inputs, produces the documented positive price series/event values, and accepts the architecture-specified seed or RNG control so tests can assert repeatability.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-nql: finally/backend/app/market/sse.py
- Scope: Implement the market SSE stream/generator described by SPEC and architecture.md, connecting provider data to the documented event format and cache behavior.
- Architecture: Own the SSE serialization/stream boundary and use the exact exported symbols in architecture.md; keep server route registration for a later phase.
- Interfaces / Depends on / Consumed by: Export the stream/generator and event-format symbols named in architecture.md; Depends on: `finally/backend/app/api/schemas.py`, `finally/backend/app/market/cache.py`, `finally/backend/app/market/massive.py`; Consumed by: later API route modules and `finally/backend/tests/test_market_infrastructure.py`.
- Acceptance: Streamed records use the SPEC-required SSE `data` framing and serialized market fields; provider/cache values flow through the stream in the documented order; the focused test can consume a finite stream without a running server.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

### te-ddu: finally/backend/tests/test_market_infrastructure.py
- Scope: Add focused tests for every active market-infrastructure contract, including schemas, cache, Massive normalization boundary, GBM determinism/shape, and SSE framing.
- Architecture: Test the public symbols owned by the phase files, following architecture.md's test placement and pytest conventions.
- Interfaces / Depends on / Consumed by: Validate the exported interfaces from `finally/backend/app/api/schemas.py`, `finally/backend/app/market/cache.py`, `finally/backend/app/market/massive.py`, `finally/backend/app/market/gbm.py`, and `finally/backend/app/market/sse.py`; Depends on: `finally/backend/app/api/__init__.py`, `finally/backend/app/api/schemas.py`, `finally/backend/app/market/cache.py`, `finally/backend/app/market/massive.py`, `finally/backend/app/market/gbm.py`, `finally/backend/app/market/sse.py`; Consumed by: phase verification and QA.
- Acceptance: Tests assert schema validation/serialization, cache store-hit/update/miss or expiry behavior, mocked Massive mapping, seeded GBM repeatability and positive values, and exact SSE event framing. Tests must not require live services and must pass through the specified pytest command.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/tests/test_market_infrastructure.py`

## Future considerations

Later phases may wire these primitives into application routes and frontend market views. Those
files are intentionally outside this phase and must not be implemented or added to this bead map.

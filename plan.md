# Implementation plan

## Active phase: project-foundation

This plan covers exactly the ten active-phase required files. It repairs the foundation regression identified by test review: the backend must reject a missing frontend export instead of returning the old `{"message":"Polecat"}` placeholder, and the foundation test must exercise the real dashboard rather than only `/api/health`. Later market, database, portfolio, chat, and component phases are excluded.

## Verification

Run from the rig root:
`test -f finally/backend/app/main.py && test -f finally/backend/app/main_test.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py && (cd finally/frontend && npm run build)`
The frontend build must actually resolve the manifest's Next executable; an unavailable dependency is not a reason to omit the build.

## Bead map

### te-0oc: finally/backend/app/main.py
- Scope: Own the FastAPI application, `app`/`create_app(...) -> FastAPI` foundation wiring, health endpoint, static assets, and root fallback.
- Architecture: architecture.md “Module / bead ownership”, “HTTP + entrypoint integration”, and the static-serving contract; SPEC.md §§4, 8, and Phase 1 exit criteria.
- Interfaces / Depends on / Consumed by: Provides `app`, `create_app`, GET `/api/health`, and the static root route. Depends on the generated output of finally/frontend/app/page.tsx and layout.tsx. Consumed by finally/backend/app/main_test.py, finally/Dockerfile, and finally/docker-compose.yml.
- Acceptance: `/api/health` returns 200 and exactly `{"status":"ok"}`. GET `/` serves the actual `frontend/out/index.html`, including the heading `Project workspace`, `$10,000`, and SPEC's ten tickers AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX. Existing exported files/assets remain servable. If `frontend/out/index.html` is absent, return an error with diagnostic detail such as `Frontend export not found`; never return placeholder HTML or `{"message":"Polecat"}`.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py`

### te-x44: finally/backend/app/main_test.py
- Scope: Write the foundation integration tests that prove health, real root content, and missing-export behavior.
- Architecture: architecture.md “Unit tests”, foundation requirements, and static-serving contract; SPEC.md Phase 1 exit criteria.
- Interfaces / Depends on / Consumed by: Uses the exported FastAPI `app` or factory from finally/backend/app/main.py with `TestClient`; consumed by the phase verification command.
- Acceptance: Test health status and exact JSON. Make a real GET `/`, assert success, assert `Project workspace` and `$10,000`, and assert every required symbol AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX. In a separate test, patch or isolate the frontend root to an empty temporary directory, request `/`, assert the error status and `{"detail":"Frontend export not found"}` (or the documented equivalent), and assert `Polecat` is absent. These tests must fail if root content is not inspected or if only health is covered.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py`

### te-wiw: finally/frontend/package.json
- Scope: Define the private Next project, build/dev/start scripts, and pinned Next, React, React DOM, TypeScript, and type dependencies.
- Architecture: architecture.md frontend build configuration and Docker multi-stage contract.
- Interfaces / Depends on / Consumed by: Provides the `build` script and frontend dependency graph. Depends on none; consumed by te-tkz, te-x3g, the app source beads, and te-qsv.
- Acceptance: `npm run build` is defined and the declared dependencies support the Next static export used by FastAPI and the Docker builder.
- Verify: `(cd finally/frontend && npm run build)`

### te-tkz: finally/frontend/tsconfig.json
- Scope: Configure strict no-emit TypeScript and Next app inclusion.
- Architecture: architecture.md frontend configuration.
- Interfaces / Depends on / Consumed by: Depends on finally/frontend/package.json; consumed by layout.tsx, page.tsx, and the Next build.
- Acceptance: Include DOM/esnext libraries, strict and noEmit checks, ES-module interop, bundler resolution, isolated modules, preserved JSX, the Next plugin, app TS/TSX inputs, and exclusion of node_modules.
- Verify: `(cd finally/frontend && npm run build)`

### te-x3g: finally/frontend/next.config.js
- Scope: Configure the default Next static export.
- Architecture: architecture.md static export contract; SPEC.md §4.
- Interfaces / Depends on / Consumed by: Depends on finally/frontend/package.json; provides the Next config consumed by the build and te-qsv.
- Acceptance: Set `output: "export"` without a custom distDir and set `images.unoptimized: true`; a successful build produces `finally/frontend/out/index.html`.
- Verify: `(cd finally/frontend && npm run build)`

### te-2yb: finally/frontend/app/layout.tsx
- Scope: Own document metadata, HTML/body shell, children rendering, and global stylesheet import.
- Architecture: architecture.md frontend ownership table.
- Interfaces / Depends on / Consumed by: Exports `metadata` and default `RootLayout`; depends on finally/frontend/app/globals.css and te-tkz; consumed by page.tsx and Next build.
- Acceptance: Render an `en` document with children inside body, import globals.css, and identify the FinAlly/Polecat focused workspace without API or later-phase trading logic.
- Verify: `(cd finally/frontend && npm run build)`

### te-stl: finally/frontend/app/page.tsx
- Scope: Render the actual static foundation dashboard.
- Architecture: architecture.md page ownership; SPEC.md first-launch and static-serving requirements.
- Interfaces / Depends on / Consumed by: Exports default `HomePage`; depends on te-2yb and globals.css; consumed by the static export and te-0oc.
- Acceptance: Render `Project workspace`, the focused-workspace introductory content, `$10,000`, and exactly the ten SPEC default symbols AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX. Do not rely on a backend placeholder or claim later live streaming/trading features.
- Verify: `(cd finally/frontend && npm run build)`

### te-2d8: finally/frontend/app/globals.css
- Scope: Provide foundation global reset, typography, and non-black dashboard styling.
- Architecture: architecture.md styling ownership; SPEC.md visual design §2.
- Interfaces / Depends on / Consumed by: Provides the stylesheet imported by te-2yb and applied to te-stl; consumed by Next build.
- Acceptance: Define the specified background, foreground, muted, border, and accent variables; box sizing; body reset, background, color, and typography; link treatment; and inherited form/button fonts. Avoid pure-black defaults and unrelated later-phase controls.
- Verify: `(cd finally/frontend && npm run build)`

### te-qsv: finally/Dockerfile
- Scope: Build the static frontend and package it with the FastAPI runtime.
- Architecture: architecture.md Docker section and static-serving contract; SPEC.md §§4 and 11.
- Interfaces / Depends on / Consumed by: Depends on all frontend foundation files plus te-0oc; produces the runtime image consumed by te-56c.
- Acceptance: The Node stage copies frontend manifests/source, installs declared dependencies, runs `npm run build`, and leaves the default `frontend/out`. The Python stage installs FastAPI/Uvicorn, copies backend sources, copies `/frontend/out` to `/app/frontend/out` from the frontend stage, exposes 8000, and starts `uvicorn backend.app.main:app`.
- Verify: `docker build -f finally/Dockerfile finally`

### te-56c: finally/docker-compose.yml
- Scope: Define the single real application service.
- Architecture: architecture.md compose contract; SPEC.md single-container deployment.
- Interfaces / Depends on / Consumed by: Depends on te-qsv and its `backend.app.main:app` runtime; consumed by local deployment.
- Acceptance: Define service `app` with build context `finally`, Dockerfile `Dockerfile`, port mapping `8000:8000`, working directory `/app`, and the real uvicorn command. It must build/run the actual application, not a placeholder service.
- Verify: `docker compose -f finally/docker-compose.yml config`

## Dependency order

Frontend manifest and TypeScript/Next configuration precede the app source. Layout precedes page composition. The backend route and generated export precede the foundation tests. Docker consumes the complete frontend and backend foundation; compose consumes Docker. No integration-contract section is required because this phase has no `finally/cmd/.../main.go`.

## Future considerations

Market providers, SSE, SQLite schema, portfolio routes, watchlist mutation, chat, richer terminal components, and release Playwright coverage belong to later phases.

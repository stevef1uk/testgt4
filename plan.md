# Project Foundation Implementation Plan

This plan covers only the active `project-foundation` phase and its ten required
files. Later market, database, watchlist, trading, AI, polish, and release
files are excluded. The foundation must produce a real static dashboard served
by FastAPI, never placeholder HTML.

## Bead map

### te-wiw: finally/frontend/package.json
- Scope: Define the Next.js, React, TypeScript manifest and `dev`, `build`, and `start` scripts.
- Architecture: Follow architecture.md frontend and Docker deployment requirements; the production build must create `frontend/out/`.
- Interfaces / Depends on / Consumed by: Provides scripts and dependencies consumed by `finally/frontend/tsconfig.json`, `finally/frontend/next.config.js`, `finally/frontend/app/layout.tsx`, `finally/frontend/app/page.tsx`, and `finally/Dockerfile`; depends on `<none>`.
- Acceptance: Valid JSON declares compatible Next.js, React, React DOM, and TypeScript dependencies. The build script performs a production App Router build and does not invoke a placeholder command.
- Verify: `docker compose -f finally/docker-compose.yml build`.

### te-tkz: finally/frontend/tsconfig.json
- Scope: Configure TypeScript and JSX compilation for the App Router.
- Architecture: Follow architecture.md frontend TypeScript conventions.
- Interfaces / Depends on / Consumed by: Provides compiler settings consumed by `layout.tsx` and `page.tsx`; depends on `finally/frontend/package.json`; consumed by the Docker frontend build.
- Acceptance: Valid JSON includes the app TSX sources, enables valid JSX/strict-compatible compilation, and does not exclude the dashboard page.
- Verify: `docker compose -f finally/docker-compose.yml build`.

### te-x3g: finally/frontend/next.config.js
- Scope: Configure Next.js static export.
- Architecture: Follow the Static Serving Contract: set `output: "export"` and do not set `distDir`.
- Interfaces / Depends on / Consumed by: Exports configuration consumed by the frontend build and `finally/Dockerfile`; depends on `finally/frontend/package.json` and `finally/frontend/tsconfig.json`.
- Acceptance: Valid JavaScript config produces the default `frontend/out/index.html` during the production build.
- Verify: `docker compose -f finally/docker-compose.yml build`.

### te-2yb: finally/frontend/app/layout.tsx
- Scope: Implement the root HTML document, metadata, and global stylesheet import.
- Architecture: Follow architecture.md App Router ownership and the SPEC FinAlly presentation.
- Interfaces / Depends on / Consumed by: Exports the root layout consumed by `page.tsx` and Next.js; depends on `finally/frontend/app/globals.css`, `package.json`, and `tsconfig.json`.
- Acceptance: Valid TSX renders children inside `<html>` and `<body>`, imports `./globals.css`, supplies FinAlly/dashboard metadata, and preserves the page's real content in static export.
- Verify: `docker compose -f finally/docker-compose.yml build`.

### te-stl: finally/frontend/app/page.tsx
- Scope: Render the initial real Market Dashboard required by Phase 1.
- Architecture: Follow architecture.md static dashboard requirement; interactive later-phase features are out of scope.
- Interfaces / Depends on / Consumed by: Exports the App Router page consumed by `layout.tsx` and Next.js; depends on `globals.css`, `package.json`, and `tsconfig.json`.
- Acceptance: Generated HTML contains a visible “Market Dashboard” heading, the ten required symbols `AAPL`, `GOOGL`, `MSFT`, `AMZN`, `TSLA`, `NVDA`, `META`, `JPM`, `V`, and `NFLX`, price content for each, and a visible `$10,000` cash figure. It is not an empty, “Coming soon”, or fallback page.
- Verify: `docker compose -f finally/docker-compose.yml build`, then assert the running root response contains the heading, all ten symbols, and `$10,000`.

### te-2d8: finally/frontend/app/globals.css
- Scope: Provide global dark terminal styling and usable responsive dashboard layout.
- Architecture: Follow SPEC colors and visual design: dark backgrounds near `#0d1117` or `#1a1a2e`, muted borders, and desktop-first responsive behavior.
- Interfaces / Depends on / Consumed by: Provides CSS imported by `layout.tsx` and applied to `page.tsx`; depends on `<none>`.
- Acceptance: Non-empty valid CSS styles the dashboard heading, ticker grid/content, and cash figure with readable dark-theme presentation and does not hide required content.
- Verify: `docker compose -f finally/docker-compose.yml build`.

### te-svp: finally/planning/PLAN.md
- Scope: Document active-phase ownership, dependency order, concrete behavior, and verification.
- Architecture: Follow architecture.md planning boundary; this file documents contracts and implements no runtime behavior.
- Interfaces / Depends on / Consumed by: Shared contract consumed by active-phase polecats and QA; depends on `<none>`.
- Acceptance: Names all ten active paths, records static export behavior, dashboard assertions, `create_app()` and health expectations, Docker/Compose wiring, and startup verification without claiming later-phase features.
- Verify: `test -s finally/planning/PLAN.md && grep -q "Market Dashboard" finally/planning/PLAN.md && grep -q "/api/health" finally/planning/PLAN.md`.

### te-0oc: finally/backend/app/main.py
- Scope: Define `create_app(...) -> FastAPI`, module-level `app`, health route, and real static index serving.
- Architecture: Follow architecture.md module ownership. Resolve `frontend_root = Path(__file__).resolve().parents[2] / "frontend"` and read `frontend_root / "out" / "index.html"`.
- Interfaces / Depends on / Consumed by: Exports `create_app()` and `app` for uvicorn; depends on the generated frontend export and `next.config.js`; consumed by `finally/Dockerfile` and `finally/docker-compose.yml`.
- Acceptance: Import succeeds and `create_app()` returns FastAPI. `GET /api/health` returns HTTP 200 with a success response. `GET /` returns the actual generated index containing Market Dashboard, tickers, and cash. A missing export returns a diagnostic error such as 503 and never hardcoded placeholder HTML. `app` is usable as `uvicorn app.main:app`.
- Verify: `docker compose -f finally/docker-compose.yml build`, then start Compose and assert `/api/health` succeeds and `/` contains the real dashboard content.

### te-qsv: finally/Dockerfile
- Scope: Implement the two-stage Node-to-Python image.
- Architecture: Node 20 slim builds the static export; Python 3.12 slim with uv runs FastAPI. Copy `/frontend/out` to `/app/frontend/out`, expose 8000, and run uvicorn.
- Interfaces / Depends on / Consumed by: Provides the image consumed by Compose; depends on `package.json`, `next.config.js`, `page.tsx`, and `main.py`.
- Acceptance: The build uses the finally layout, copies the real export with `COPY --from=frontend /frontend/out /app/frontend/out`, includes backend runtime dependencies, exposes 8000, and uses `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`, not a sleep or placeholder server.
- Verify: `docker compose -f finally/docker-compose.yml build`.

### te-56c: finally/docker-compose.yml
- Scope: Define the single app service, build, port, environment, database volume, and healthcheck.
- Architecture: Follow architecture.md Compose contract: map 8000:8000, load `finally/.env`, persist `/app/db`, and check `/api/health`.
- Interfaces / Depends on / Consumed by: Provides the runnable service for QA; depends on `finally/Dockerfile` and `finally/backend/app/main.py`; consumed by phase verification.
- Acceptance: Compose config builds the real image, publishes port 8000, loads the environment file, persists database storage, and healthchecks `http://localhost:8000/api/health`. Once up, `/api/health` succeeds and `/` returns Market Dashboard, default ticker content, and `$10,000`.
- Verify: `docker compose -f finally/docker-compose.yml config && docker compose -f finally/docker-compose.yml build`.

## Phase verification

Run the required file/build gate:
`test -f finally/planning/PLAN.md && test -f finally/backend/app/main.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && docker compose -f finally/docker-compose.yml build`.

Then run `docker compose -f finally/docker-compose.yml up -d`, wait for readiness, and assert `curl --fail http://localhost:8000/api/health`. Assert the root response contains “Market Dashboard”, all ten default ticker symbols, and `$10,000`; finally run `docker compose -f finally/docker-compose.yml down`. Completion requires `create_app()`, successful health, and generated dashboard HTML rather than fallback HTML.

## Future considerations

SSE, database seeding, portfolio routes, watchlist CRUD, trading, AI chat, and full Playwright coverage belong to later phases.

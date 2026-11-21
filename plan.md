# Implementation plan — Project Foundation

This plan covers only the active `project-foundation` phase and its ten exact
required paths. It delivers a buildable static Next.js dashboard, FastAPI
health/root wiring, and the single-container Docker runtime. Market streaming,
portfolio persistence, watchlist CRUD, chat, and later polish remain out of
scope for this phase.

## Bead map

### te-0oc: finally/backend/app/main.py
- Scope: Implement `create_app(...) -> FastAPI`, health handling, and real
  static-export root serving.
- Architecture: architecture.md module ownership, HTTP route table, Static
  Serving Contract, and `project-foundation` requirement.
- Interfaces: `create_app(...) -> FastAPI`; `GET /api/health`; `GET /` reads
  `Path(__file__).resolve().parents[2] / "frontend" / "out" / "index.html"`.
- Depends on: finally/frontend/app/page.tsx; finally/frontend/app/layout.tsx;
  finally/frontend/package.json; finally/frontend/next.config.js.
- Consumed by: finally/backend/app/main_test.py; finally/Dockerfile;
  finally/docker-compose.yml.
- Acceptance:
  - `/api/health` returns a successful response suitable for the Docker
    healthcheck, not merely a declared route.
  - `/` returns the actual export containing the dashboard heading, dollar
    price content, AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX,
    and `$10,000`.
  - With `frontend/out/index.html` absent, `/` returns a diagnostic 5xx and
    never synthesizes `<h1>Finally</h1>`, “Coming soon”, or other placeholder.
  - API routes remain available before static handling and the implementation
    does not embed duplicate UI markup.
- Verify: `test -f finally/backend/app/main.py && test -f finally/backend/app/main_test.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py && (cd finally/frontend && npm run build)`.

### te-x44: finally/backend/app/main_test.py
- Scope: Write foundation integration tests for health, real root content, and
  missing-export safety.
- Architecture: architecture.md `project-foundation` requirement and Unit tests;
  SPEC static-serving contract and Phase 1 exit criteria.
- Interfaces: exercise `create_app(...) -> FastAPI`, `GET /api/health`, and
  `GET /` through a test client.
- Depends on: finally/backend/app/main.py; finally/frontend/app/page.tsx;
  finally/frontend/app/layout.tsx.
- Consumed by: phase verification and QA.
- Acceptance:
  - A test asserts the health request succeeds with a usable success response.
  - A root test asserts the real dashboard heading, AAPL, GOOGL, MSFT, AMZN,
    TSLA, NVDA, META, JPM, V, NFLX, a dollar-prefixed price, and `$10,000`.
  - Tests reject placeholder-only output and do not pass from status code,
    content type, visibility, or the word “Finally” alone.
  - A missing-export test asserts a diagnostic 5xx and no placeholder HTML;
    temporary fixtures are isolated from runtime database state.
- Verify: `PYTHONPATH=finally/backend python -m pytest -v finally/backend/app/main_test.py`.

### te-wiw: finally/frontend/package.json
- Scope: Define the self-contained Next.js/TypeScript project and production
  build script.
- Architecture: architecture.md frontend boundary and Docker multi-stage
  contract; SPEC static-export requirements.
- Interfaces: `npm run build` invokes Next.js and emits default
  `frontend/out/index.html`.
- Depends on: finally/frontend/tsconfig.json; finally/frontend/next.config.js.
- Consumed by: finally/Dockerfile and the foundation build gate.
- Acceptance:
  - Dependencies support the app-directory layout and page and their TypeScript
    compilation.
  - `npm run build` performs a production static build without requiring a
    committed lockfile or development server.
  - The build emits `out/index.html` containing the real heading, required
    ticker text, prices, and `$10,000`.
- Verify: `(cd finally/frontend && npm run build && test -f out/index.html)`.

### te-tkz: finally/frontend/tsconfig.json
- Scope: Configure TypeScript compilation for the Next app directory.
- Architecture: architecture.md frontend TypeScript boundary and dependency graph.
- Interfaces: include `app/**/*.tsx` and resolve imports used by layout/page.
- Depends on: finally/frontend/package.json.
- Consumed by: finally/frontend/next.config.js and the production build.
- Acceptance:
  - JSX/React, modern modules, and Next type declarations are configured;
    layout and page are included rather than excluded.
  - `npm run build` completes without invalid JSX, unresolved imports, or
    missing generated Next types.
  - Settings do not require server-only behavior incompatible with static
    `output: "export"`.
- Verify: `(cd finally/frontend && npm run build)`.

### te-x3g: finally/frontend/next.config.js
- Scope: Configure Next.js static export mode.
- Architecture: architecture.md Static Serving Contract.
- Interfaces: set `output: "export"` and preserve default `out/`; do not set
  `distDir`.
- Depends on: finally/frontend/package.json; finally/frontend/tsconfig.json.
- Consumed by: finally/Dockerfile; finally/backend/app/main.py; build output.
- Acceptance:
  - A production build creates `out/index.html` at the path expected by both
    FastAPI and Docker.
  - The export includes the real dashboard heading, ten required tickers, and
    `$10,000`, with no placeholder output or custom incompatible directory.
- Verify: `(cd finally/frontend && npm run build && test -f out/index.html)`.

### te-2yb: finally/frontend/app/layout.tsx
- Scope: Implement root document shell, metadata, and global stylesheet import.
- Architecture: architecture.md layout ownership; SPEC visual/layout contract.
- Interfaces: export the root layout, provide FinAlly title/metadata, render
  page children.
- Depends on: finally/frontend/app/globals.css; finally/frontend/next.config.js.
- Consumed by: finally/frontend/app/page.tsx and generated `index.html`.
- Acceptance:
  - The built document has a meaningful FinAlly title and valid body shell and
    renders children into the export.
  - It imports `globals.css`, enabling the required dark terminal presentation.
  - It does not replace page content with an empty shell, “Coming soon”, or
    placeholder heading.
- Verify: `(cd finally/frontend && npm run build && test -f out/index.html && grep -q 'FinAlly' out/index.html)`.

### te-stl: finally/frontend/app/page.tsx
- Scope: Implement the foundation dashboard and static seed display.
- Architecture: architecture.md page ownership and foundation dependencies; SPEC
  First Launch and Static Serving Contract.
- Interfaces: export the Next page component; render heading, cash, and ten
  default ticker rows/cards with dollar-prefixed prices.
- Depends on: finally/frontend/app/layout.tsx; finally/frontend/package.json.
- Consumed by: finally/backend/app/main_test.py; finally/Dockerfile; root route.
- Acceptance:
  - The export visibly renders “Market Dashboard” and/or the specified FinAlly
    dashboard title and a clear `$10,000` cash display.
  - It renders AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, and NFLX,
    each beside a dollar-prefixed price-like value.
  - It is real first-launch dashboard content, not an empty div, “Coming soon”,
    or placeholder page.
  - It compiles as a static export without server-only APIs that violate the
    configured output mode.
- Verify: `(cd finally/frontend && npm run build && test -f out/index.html && grep -q 'AAPL' out/index.html && grep -q '\$10,000' out/index.html)`.

### te-2d8: finally/frontend/app/globals.css
- Scope: Provide global dark terminal styling and readable foundation layout.
- Architecture: architecture.md frontend ownership; SPEC visual design/colors.
- Interfaces: global selectors/classes consumed by layout and page; no backend
  routes or persistence symbols.
- Depends on: finally/frontend/app/layout.tsx.
- Consumed by: finally/frontend/app/page.tsx, exported dashboard, and later UI.
- Acceptance:
  - Body/background uses a dark color near `#0d1117` or `#1a1a2e`, with muted
    borders and readable non-pure-black surfaces.
  - Rules create a dense but usable dashboard with visible heading, cash panel,
    and ticker cards/rows without hiding required content.
  - The stylesheet imports without syntax errors and is included in the
    production export.
- Verify: `(cd finally/frontend && npm run build && test -f out/index.html)`.

### te-qsv: finally/Dockerfile
- Scope: Implement the Node build/Python runtime image serving the real export.
- Architecture: architecture.md Docker & Deployment and Static Serving Contract.
- Interfaces: frontend emits `/frontend/out`; runtime copies it with
  `COPY --from=frontend /frontend/out /app/frontend/out`; uvicorn listens on
  `0.0.0.0:8000`.
- Depends on: finally/frontend/package.json; finally/frontend/next.config.js;
  finally/frontend/app/page.tsx; finally/backend/app/main.py.
- Consumed by: finally/docker-compose.yml and application startup.
- Acceptance:
  - It uses Node 20 slim and Python 3.12/uv stages, builds frontend, and
    copies backend sources/dependencies.
  - It copies exactly `/frontend/out` to `/app/frontend/out`, exposes 8000,
    and starts the FastAPI app on `0.0.0.0:8000`.
  - The image serves successful `/api/health` and real root HTML containing
    heading, default tickers, prices, and `$10,000`, never a placeholder.
- Verify: `docker build -f finally/Dockerfile finally`.

### te-56c: finally/docker-compose.yml
- Scope: Define the single app service, environment loading, port mapping, and
  persistent SQLite mount.
- Architecture: architecture.md Docker & Deployment; SPEC single-container and
  volume contracts.
- Interfaces: one service builds the real Dockerfile, publishes `8000:8000`,
  loads `.env`, and mounts persistent storage at `/app/db`.
- Depends on: finally/Dockerfile; finally/backend/app/main.py.
- Consumed by: one-command startup and foundation deployment verification.
- Acceptance:
  - Compose validates with one real application service built from the real
    Dockerfile and mapping host port 8000 to container port 8000.
  - It supports `OPENROUTER_API_KEY`, `MASSIVE_API_KEY`, and `LLM_MOCK` and
    persists SQLite data at `/app/db`.
  - Any healthcheck targets `/api/health`; no fake frontend or placeholder
    service bypasses FastAPI/static export.
- Verify: `docker compose -f finally/docker-compose.yml config`.

## Phase verification

Run exactly:
`test -f finally/backend/app/main.py && test -f finally/backend/app/main_test.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py && (cd finally/frontend && npm run build)`.

## Future considerations

SSE/providers, SQLite schema and portfolio routes, watchlist CRUD, interactive
charts/trading, chat, lifecycle scripts, and Playwright coverage belong to later
phases and are deliberately excluded from these ten beads.

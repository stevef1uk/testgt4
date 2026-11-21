# Implementation plan

## Active phase: project-foundation

Implement only the ten active-phase required paths. This phase must produce a
real static-export dashboard, FastAPI foundation, and single-container runtime.
Later market, portfolio, chat, and polish files remain out of scope.

## Bead map

### te-0oc: finally/backend/app/main.py
- Scope: Implement `create_app(...) -> FastAPI`, `/api/health`, and the root
  static-export route described in architecture.md.
- Architecture: The root route must read `frontend/out/index.html` using the
  specified `Path(__file__).resolve().parents[2] / "frontend"` calculation;
  missing export returns a diagnostic error, never placeholder HTML.
- Interfaces: Export `create_app` and the module-level app used by
  `uvicorn app.main:app`; register health and root behavior without inventing
  later-phase route implementations.
- Depends on: finally/frontend/app/page.tsx, finally/frontend/app/layout.tsx
- Consumed by: finally/backend/app/main_test.py, finally/Dockerfile,
  finally/docker-compose.yml
- Acceptance: `/api/health` succeeds; `GET /` serves the actual exported
  dashboard containing the heading, ten required ticker symbols, and `$10,000`;
  absent export is an error rather than a hardcoded fallback.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py`

### te-x44: finally/backend/app/main_test.py
- Scope: Write the foundation integration tests for the app factory and root.
- Architecture: Test the exported FastAPI app with the architecture-specified
  client/import arrangement.
- Interfaces: Consume `create_app`/`app` from finally/backend/app/main.py.
- Depends on: finally/backend/app/main.py
- Consumed by: phase verification
- Acceptance: Assert health success and real root content: dashboard heading,
  AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX, and `$10,000`;
  also assert missing export is not accepted as placeholder content.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py`

### te-wiw: finally/frontend/package.json
- Scope: Define the Next.js, React, and TypeScript project metadata and build
  scripts required by architecture.md.
- Architecture: Supply the production build script used for static export and
  dependencies needed by the assigned App Router files.
- Interfaces: Provide `dev`, `build`, and `start` scripts consumed by the
  workflow and Dockerfile.
- Depends on: <none>
- Consumed by: finally/frontend/tsconfig.json, finally/frontend/next.config.js,
  finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx,
  finally/Dockerfile
- Acceptance: The declared project supports the required production export and
  the exact phase verification build command succeeds.
- Verify: `(cd finally/frontend && npm run build)`

### te-tkz: finally/frontend/tsconfig.json
- Scope: Configure strict TypeScript compilation and Next generated types.
- Architecture: Match the Next App Router include/compiler settings and
  repository path conventions.
- Interfaces: Configuration is consumed by both assigned `.tsx` files and Next.
- Depends on: finally/frontend/package.json
- Consumed by: finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx
- Acceptance: The configuration includes app sources and allows the production
  build to type-check without unsupported aliases.
- Verify: `(cd finally/frontend && npm run build)`

### te-x3g: finally/frontend/next.config.js
- Scope: Export the minimal Next configuration for static deployment.
- Architecture: Set the architecture-required static export mode; do not add
  rewrites or unsupported server behavior.
- Interfaces: Export the Next configuration object consumed by the build.
- Depends on: finally/frontend/package.json
- Consumed by: finally/Dockerfile
- Acceptance: Next loads the configuration and emits `frontend/out/index.html`
  through the required production build.
- Verify: `(cd finally/frontend && npm run build)`

### te-2d8: finally/frontend/app/globals.css
- Scope: Implement the global dark terminal foundation, reset, typography,
  colors, spacing, and responsive shell used by the assigned page.
- Architecture: Follow SPEC colors and architecture visual foundation; define
  selectors used by page and layout without implementing later widgets.
- Interfaces: Global stylesheet imported by layout and consumed by page.
- Depends on: <none>
- Consumed by: finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx
- Acceptance: Build includes the stylesheet; the root page has dark themed
  readable presentation with the specified accent palette and desktop-first
  responsive baseline.
- Verify: `(cd finally/frontend && npm run build)`

### te-2yb: finally/frontend/app/layout.tsx
- Scope: Implement the App Router root layout, metadata, children shell, and
  global stylesheet import.
- Architecture: Follow the layout contract and FinAlly document metadata in
  SPEC.md; keep feature state out of the server layout.
- Interfaces: Export the default typed root layout receiving `children`.
- Depends on: finally/frontend/package.json, finally/frontend/tsconfig.json,
  finally/frontend/app/globals.css
- Consumed by: finally/frontend/app/page.tsx
- Acceptance: Layout renders children, imports globals, and produces the
  required FinAlly title/metadata in a successful static build.
- Verify: `(cd finally/frontend && npm run build)`

### te-stl: finally/frontend/app/page.tsx
- Scope: Implement the real foundation dashboard page at `/`.
- Architecture: Follow the assigned App Router page boundary and foundation
  content contract; do not import components owned by later phases.
- Interfaces: Export the default page component and render the dashboard
  heading, ten seeded ticker labels, prices, and `$10,000` cash figure.
- Depends on: finally/frontend/app/layout.tsx, finally/frontend/app/globals.css,
  finally/frontend/package.json, finally/frontend/tsconfig.json
- Consumed by: finally/backend/app/main.py, finally/Dockerfile
- Acceptance: Static output contains the actual dashboard heading, all ten
  required ticker symbols, prices with dollar formatting, and `$10,000`;
  it is not a placeholder or “coming soon” page.
- Verify: `(cd finally/frontend && npm run build)`

### te-qsv: finally/Dockerfile
- Scope: Implement the two-stage Node-build/Python-runtime image.
- Architecture: Build the Next static export, copy `/frontend/out` to the
  runtime location expected by main.py, install backend runtime requirements,
  expose 8000, and run uvicorn.
- Interfaces: Produce the real app image consumed by compose; preserve the
  static-serving contract and application command from architecture.md.
- Depends on: finally/frontend/package.json, finally/frontend/next.config.js,
  finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx,
  finally/backend/app/main.py
- Consumed by: finally/docker-compose.yml
- Acceptance: Docker build uses the repository root context, includes the real
  frontend export and backend, exposes port 8000, and starts the specified app.
- Verify: `docker build -f finally/Dockerfile -t testgt4-foundation .`

### te-56c: finally/docker-compose.yml
- Scope: Define the single app service, build context, port mapping, runtime
  environment, and persistent database volume.
- Architecture: Use the single-container deployment contract; compose must build
  the real Dockerfile, publish 8000, and mount the database path.
- Interfaces: Provide the runnable app service consumed by reviewers.
- Depends on: finally/Dockerfile
- Consumed by: phase verification
- Acceptance: Compose configuration validates, builds the real app image rather
  than a stub, maps host port 8000, and preserves the documented db volume and
  health behavior.
- Verify: `docker compose -f finally/docker-compose.yml config`

## Phase verification

Run exactly:
`test -f finally/backend/app/main.py && test -f finally/backend/app/main_test.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py && (cd finally/frontend && npm run build)`

## Future considerations

Market streaming, SQLite schema/portfolio operations, watchlist CRUD, trading,
chat, component decomposition, polish, and Playwright release coverage belong
to their later delivery phases and are intentionally not acceptance criteria
for this foundation bead set.

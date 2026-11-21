# Implementation plan — Project Foundation

This plan covers only the active `project-foundation` phase. The implementation must use the exact `finally/` paths, produce a real dashboard, and preserve the static-export contract. Later-phase API, market, portfolio, chat, and browser-test files are out of scope.

## Bead map

### te-wiw: finally/frontend/package.json
- Scope: Define the Next.js/React/TypeScript project manifest and `npm run build`.
- Architecture: `architecture.md` planned frontend layout and Docker multi-stage contract; SPEC sections 3, 4, and 11.
- Interfaces: Package scripts and dependencies consumed by the Next build.
- Depends on: <none>
- Consumed by: finally/frontend/tsconfig.json; finally/frontend/next.config.js; finally/Dockerfile
- Acceptance: The manifest supports the App Router foundation files and `npm run build` produces the default `out/` static export without unrelated features.
- Verify: `(cd finally/frontend && npm run build)`

### te-tkz: finally/frontend/tsconfig.json
- Scope: Configure strict TypeScript compilation for the foundation App Router files.
- Architecture: Frontend project configuration and typed page/layout boundary.
- Interfaces: Compiler configuration consumed by Next and the `.tsx` foundation files.
- Depends on: finally/frontend/package.json
- Consumed by: finally/frontend/next.config.js; finally/frontend/app/layout.tsx; finally/frontend/app/page.tsx
- Acceptance: Next conventions, JSX, module resolution, and app-file inclusion are configured so the production build type-checks.
- Verify: `(cd finally/frontend && npm run build)`

### te-x3g: finally/frontend/next.config.js
- Scope: Configure Next.js static export.
- Architecture: Static Serving Contract: `output: "export"` and default `out/` directory.
- Interfaces: Export Next configuration consumed by the build and Dockerfile.
- Depends on: finally/frontend/package.json; finally/frontend/tsconfig.json
- Consumed by: finally/frontend/app/layout.tsx; finally/Dockerfile
- Acceptance: Uses static export, does not set `distDir`, and builds to `finally/frontend/out/`.
- Verify: `(cd finally/frontend && npm run build)`

### te-2d8: finally/frontend/app/globals.css
- Scope: Provide global foundation dashboard styling.
- Architecture: Global stylesheet ownership; SPEC visual design and color scheme.
- Interfaces: CSS classes and global rules consumed by the layout/page.
- Depends on: <none>
- Consumed by: finally/frontend/app/layout.tsx
- Acceptance: Defines a non-black dark background near `#0d1117` or `#1a1a2e`, muted borders, readable text, and the required yellow, blue, and purple accents; includes a compact desktop-first responsive foundation layout.
- Verify: `(cd finally/frontend && npm run build)`

### te-2yb: finally/frontend/app/layout.tsx
- Scope: Implement the document shell, metadata, children rendering, and global stylesheet import.
- Architecture: `layout.tsx` ownership; SPEC title and visual requirements.
- Interfaces: Export `Metadata` and `RootLayout`; import `./globals.css`.
- Depends on: finally/frontend/next.config.js; finally/frontend/app/globals.css
- Consumed by: finally/frontend/app/page.tsx; finally/backend/app/main.py
- Acceptance: Static output has meaningful FinAlly metadata, renders children, and loads the global dark stylesheet without feature logic.
- Verify: `(cd finally/frontend && npm run build)`

### te-stl: finally/frontend/app/page.tsx
- Scope: Implement the actual statically exportable foundation dashboard.
- Architecture: Page ownership and static-serving integration; SPEC first-launch and root-content contract.
- Interfaces: Export the App Router page component rendering heading, ticker cards, cash balance, and chat-panel area.
- Depends on: finally/frontend/app/layout.tsx
- Consumed by: finally/backend/app/main.py; finally/backend/app/main_test.py; finally/Dockerfile
- Acceptance: Built HTML contains a real dashboard heading, AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX, and `$10,000`; it must not be placeholder-only HTML. Later live SSE/trading behavior remains out of this phase.
- Verify: `(cd finally/frontend && npm run build)`

### te-0oc: finally/backend/app/main.py
- Scope: Implement `create_app(...) -> FastAPI`, health behavior, and real static root serving.
- Architecture: Entrypoint ownership and HTTP integration; SPEC static serving contract.
- Interfaces: Export `create_app`; register `GET /api/health`; read `frontend_root / "out" / "index.html"` at `GET /`; return a diagnostic error when export is absent.
- Depends on: finally/frontend/app/page.tsx; finally/frontend/app/layout.tsx
- Consumed by: finally/backend/app/main_test.py; finally/Dockerfile
- Acceptance: Health succeeds; root serves the actual exported dashboard containing the heading, ten required ticker symbols, and `$10,000`; missing export is an error and never synthesized placeholder HTML.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py`

### te-x44: finally/backend/app/main_test.py
- Scope: Write foundation integration tests for health and real static content.
- Architecture: Explicit foundation test ownership and Phase 1 exit criteria.
- Interfaces: Exercise `create_app`, `GET /api/health`, and `GET /` using isolated export fixtures.
- Depends on: finally/backend/app/main.py; finally/frontend/app/page.tsx
- Consumed by: phase verification and QA
- Acceptance: Substantive pytest cases assert health success, the heading, all ten tickers, `$10,000`, and an error for missing export; no test blesses a placeholder or merely imports code.
- Verify: `PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py`

### te-qsv: finally/Dockerfile
- Scope: Implement the Node 20 frontend-build and Python 3.12 runtime stages.
- Architecture: Docker deployment and static-serving contract.
- Interfaces: Copy `/frontend/out` to `/app/frontend/out`, expose port 8000, and run `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`.
- Depends on: finally/frontend/package.json; finally/frontend/next.config.js; finally/frontend/app/page.tsx; finally/backend/app/main.py
- Consumed by: finally/docker-compose.yml
- Acceptance: Builds the real static export, copies it to the path expected by the backend, includes runtime sources/dependencies, supports `/app/db`, and contains no placeholder HTML.
- Verify: `cd finally && docker build -f Dockerfile .`

### te-56c: finally/docker-compose.yml
- Scope: Define the single application service and persistence/runtime settings.
- Architecture: Compose ownership and single-container deployment.
- Interfaces: Build the real Dockerfile, publish port 8000, load documented environment values, and persist `/app/db`.
- Depends on: finally/Dockerfile
- Consumed by: operators and later release harness
- Acceptance: `docker compose config` succeeds; there is one app service using the real image build, port 8000 is mapped, and database persistence is declared.
- Verify: `cd finally && docker compose -f docker-compose.yml config`

## Phase verification

`test -f finally/backend/app/main.py && test -f finally/backend/app/main_test.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py && (cd finally/frontend && npm run build)`

## Future considerations

Later phases own API factories and schemas, SQLite schema, market providers/SSE, portfolio/trading behavior, feature components, chat, polish, and Playwright release coverage. They must extend this foundation without changing its root static-serving contract.

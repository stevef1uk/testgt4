# Implementation plan

## Phase context

Active phase: `project-foundation`. Implement only the ten required paths in this map. The common phase
verification command is:

`test -f finally/backend/app/main.py && test -f finally/backend/app/main_test.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && PYTHONPATH=finally/backend python -m pytest finally/backend/app/main_test.py && (cd finally/frontend && npm run build)`

## Bead map

### te-0oc: finally/backend/app/main.py
- Scope: Implement the foundation HTTP app, `/api/health`, and static export root serving.
- Architecture: `architecture.md` backend foundation/static-serving section; SPEC HTTP contract.
- Interfaces: `GET /api/health` succeeds; `GET /` serves `finally/frontend/out/index.html`; missing export returns HTTP 503 with a diagnostic response.
- Depends on: finally/frontend/next.config.js, finally/frontend/app/page.tsx
- Consumed by: finally/backend/app/main_test.py, finally/Dockerfile, finally/docker-compose.yml
- Acceptance: Health succeeds. Root serves the real export, whose HTML contains the dashboard heading, AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX, and `$10,000`. If `finally/frontend/out/index.html` is missing, root returns 503 with a diagnostic and never placeholder HTML.
- Verify: the common phase verification command above.

### te-x44: finally/backend/app/main_test.py
- Scope: Add tests for the foundation HTTP contract.
- Architecture: `architecture.md` backend test section and SPEC foundation acceptance cases.
- Interfaces: Exercise `/api/health` and `/`, asserting status and response content.
- Depends on: finally/backend/app/main.py
- Consumed by: phase verification
- Acceptance: Tests assert successful `GET /api/health`; root returns real export HTML containing the dashboard heading, all ten tickers (AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX), and `$10,000`; and a missing `finally/frontend/out/index.html` returns 503 diagnostic output, never placeholder HTML.
- Verify: the common phase verification command above.

### te-drp: finally/frontend/package.json
- Scope: Define the Next.js foundation manifest, dependencies, and static-export build script.
- Architecture: `architecture.md` frontend project-manifest section.
- Interfaces: `npm run build` is the frontend build entrypoint and emits the export consumed by the backend.
- Depends on: <none>
- Consumed by: finally/frontend/tsconfig.json, finally/frontend/next.config.js, finally/Dockerfile, finally/docker-compose.yml
- Acceptance: The manifest identifies a Next.js App Router TypeScript application, supplies the required React/Next tooling, and makes `npm run build` produce `finally/frontend/out/index.html`; it adds no later-phase data/API behavior.
- Verify: the common phase verification command above.

### te-5ew: finally/frontend/tsconfig.json
- Scope: Configure strict TypeScript, JSX, module resolution, and App Router source inclusion.
- Architecture: `architecture.md` frontend TypeScript configuration section.
- Interfaces: Configuration type-checks `layout.tsx`, `page.tsx`, and their CSS import.
- Depends on: finally/frontend/package.json
- Consumed by: finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx
- Acceptance: The foundation pages compile through the project build with Next conventions and do not require later-phase modules.
- Verify: the common phase verification command above.

### te-x3g: finally/frontend/next.config.js
- Scope: Configure deterministic static export behavior.
- Architecture: `architecture.md` frontend static-export configuration section.
- Interfaces: Next configuration enables an export with `finally/frontend/out/index.html`.
- Depends on: finally/frontend/package.json
- Consumed by: finally/backend/app/main.py, finally/frontend/app/page.tsx, finally/Dockerfile
- Acceptance: The foundation build emits `out/index.html` and the root page needs no server-only runtime; configuration is limited to static-export behavior.
- Verify: the common phase verification command above.

### te-2yb: finally/frontend/app/layout.tsx
- Scope: Provide the App Router root layout, document metadata, and global stylesheet import.
- Architecture: `architecture.md` frontend root-layout section.
- Interfaces: Export the root layout component and render children in a valid HTML shell.
- Depends on: finally/frontend/tsconfig.json, finally/frontend/app/globals.css
- Consumed by: finally/frontend/app/page.tsx, finally/frontend/next.config.js
- Acceptance: Layout builds, imports global CSS, supplies meaningful dashboard metadata/title, and renders page content; it introduces no later-phase interactions.
- Verify: the common phase verification command above.

### te-stl: finally/frontend/app/page.tsx
- Scope: Implement the static foundation dashboard at `/`.
- Architecture: `architecture.md` frontend dashboard-foundation section and SPEC initial dashboard content.
- Interfaces: Export the App Router page component.
- Depends on: finally/frontend/tsconfig.json, finally/frontend/app/layout.tsx, finally/frontend/app/globals.css
- Consumed by: finally/frontend/next.config.js, finally/backend/app/main.py, finally/backend/app/main_test.py
- Acceptance: Exported root HTML has a clear dashboard heading, visibly includes AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX, and displays `$10,000`. It remains static foundation content, with no later quotes/orders/portfolio behavior.
- Verify: the common phase verification command above.

### te-2d8: finally/frontend/app/globals.css
- Scope: Supply global foundation styling imported by the root layout.
- Architecture: `architecture.md` frontend global-style section.
- Interfaces: Provide global CSS for the layout and page markup; no runtime API.
- Depends on: <none>
- Consumed by: finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx
- Acceptance: CSS loads in the build and establishes a readable baseline for the foundation page, heading, ticker content, and `$10,000`, without later-phase widgets or behavior.
- Verify: the common phase verification command above.

### te-n92: finally/Dockerfile
- Scope: Build the frontend export and package it with the backend application.
- Architecture: `architecture.md` containerization section.
- Interfaces: `finally/` is the build context; image contains backend and `frontend/out/index.html` and launches the real app.
- Depends on: finally/backend/app/main.py, finally/frontend/package.json, finally/frontend/next.config.js, finally/frontend/app/page.tsx
- Consumed by: finally/docker-compose.yml
- Acceptance: Image build produces the static export before backend startup, retains `frontend/out/index.html`, and launches the real application rather than a placeholder command; no later-phase services are added.
- Verify: the common phase verification command above.

### te-cwv: finally/docker-compose.yml
- Scope: Define the foundation service, Dockerfile build context, runtime, and application port.
- Architecture: `architecture.md` compose/deployment section.
- Interfaces: Compose builds `finally/Dockerfile`, starts the real backend with its export, and exposes `/` and `/api/health`.
- Depends on: finally/Dockerfile
- Consumed by: operator deployment and phase verification
- Acceptance: Compose uses the specified project context and Dockerfile, starts the real app with generated export available, and exposes the documented HTTP service; no fake server or later-phase service is present.
- Verify: the common phase verification command above.

## Future considerations

Later phases may add data, portfolio, trading, and richer dashboard behavior. Those features are intentionally
outside this foundation phase.

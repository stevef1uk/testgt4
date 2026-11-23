# Implementation plan

## Scope and verification

This project-foundation phase implements exactly the ten required foundation files under `finally/`. It establishes a runnable FastAPI container, a static-export Next.js dashboard, and the local compose entrypoint; later-phase trading, data, and integration work is out of scope. Acceptance is grounded in SPEC.md and architecture.md: the frontend must render the FinAlly Trading Workstation heading, the ten specified watchlist tickers, chart container, and `$10,000` portfolio summary; the backend must expose the architecture-defined FastAPI `app` and serve the foundation application; and the container/compose configuration must build and run that application on port 8000.

Phase verification:
`test -f finally/backend/app/main.py && test -f finally/frontend/package.json && test -f finally/frontend/tsconfig.json && test -f finally/frontend/next.config.js && test -f finally/frontend/next-env.d.ts && test -f finally/frontend/app/layout.tsx && test -f finally/frontend/app/page.tsx && test -f finally/frontend/app/globals.css && test -f finally/Dockerfile && test -f finally/docker-compose.yml && (cd finally/frontend && npm run build)`

## Bead map

### te-0oc: finally/backend/app/main.py
- Scope: Implement the architecture-defined FastAPI application entry module and its foundation/static-serving behavior, preserving the exported `app` consumed by Uvicorn and the container.
- Architecture: architecture.md backend application section; use the SPEC foundation API and application layout without adding later-phase trading behavior.
- Interfaces: exports `create_app(...) -> FastAPI` and application object `app`; the module is launched as `app.main:app` from `/app/backend`.
- Depends on: finally/frontend/app/page.tsx, finally/frontend/app/layout.tsx
- Consumed by: finally/Dockerfile, finally/docker-compose.yml
- Acceptance: the module imports successfully; `app` is the FastAPI entrypoint named by both container commands; the foundation response/static behavior described by SPEC is available without inventing extra routes.
- Verify: `python -c "from backend.app.main import app; print(app)"` from `finally`

### te-drp: finally/frontend/package.json
- Scope: Define the Next.js 14, React 18, and TypeScript project manifest and the `dev`, `build`, and `start` scripts required by the architecture.
- Architecture: architecture.md frontend project configuration section.
- Interfaces: scripts `dev`, `build`, `start`; dependencies `next`, `react`, `react-dom`; development dependencies for Node/React typings and TypeScript.
- Depends on: <none>
- Consumed by: finally/Dockerfile, finally/frontend/tsconfig.json
- Acceptance: the manifest is valid JSON, marks the package private, pins the architecture versions, and `npm run build` is the defined production build command.
- Verify: `cd finally/frontend && npm run build`

### te-5ew: finally/frontend/tsconfig.json
- Scope: Configure strict, no-emit TypeScript with Next.js bundler resolution, JSX preservation, Next plugin, and the architecture include/exclude sets.
- Architecture: architecture.md frontend project configuration section.
- Interfaces: compiler configuration consumed by Next.js/TypeScript; includes `next-env.d.ts`, Next generated types, and all `.ts`/`.tsx` sources.
- Depends on: finally/frontend/package.json, finally/frontend/next-env.d.ts
- Consumed by: finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx, finally/frontend/next.config.js
- Acceptance: valid JSON enables strict type checking, no emit, ESNext module resolution, JSX preserve, incremental compilation, and excludes node_modules as specified.
- Verify: `cd finally/frontend && npx tsc --noEmit`

### te-x3g: finally/frontend/next.config.js
- Scope: Configure the Next.js application for static export and strict React mode as required for the container's copied `out` directory.
- Architecture: architecture.md frontend build configuration section.
- Interfaces: exports the Next.js config object with `output: "export"` and `reactStrictMode: true`.
- Depends on: finally/frontend/package.json
- Consumed by: finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx, finally/Dockerfile
- Acceptance: Next recognizes the config, produces a static `out` directory, and the production build succeeds with the two architecture-required options.
- Verify: `cd finally/frontend && npm run build`

### te-95q: finally/frontend/next-env.d.ts
- Scope: Provide the standard generated Next.js ambient type references required by the TypeScript project.
- Architecture: architecture.md frontend type-environment section.
- Interfaces: ambient references for `next` and `next/image-types/global`; no runtime exports.
- Depends on: finally/frontend/package.json
- Consumed by: finally/frontend/tsconfig.json
- Acceptance: the file contains the standard Next.js type references, is included by tsconfig, and permits the app files to type-check without runtime code.
- Verify: `cd finally/frontend && npx tsc --noEmit`

### te-2yb: finally/frontend/app/layout.tsx
- Scope: Implement the root App Router layout, import global CSS, set the FinAlly metadata, and render the required English HTML/body shell.
- Architecture: architecture.md frontend layout section.
- Interfaces: exports `metadata` with title `FinAlly` and description `AI Trading Workstation`; default export `RootLayout({ children }: { children: React.ReactNode })`.
- Depends on: finally/frontend/tsconfig.json, finally/frontend/next-env.d.ts, finally/frontend/app/globals.css
- Consumed by: Next.js App Router and finally/frontend/app/page.tsx
- Acceptance: build succeeds; the layout imports globals.css, emits `<html lang='en'>`, and wraps children in `<body>` with the specified metadata.
- Verify: `cd finally/frontend && npm run build`

### te-stl: finally/frontend/app/page.tsx
- Scope: Implement the static dashboard foundation from SPEC: heading, watchlist, chart placeholder, and portfolio summary.
- Architecture: architecture.md dashboard page section.
- Interfaces: default export `DashboardPage`; renders IDs `watchlist-container`, `chart-container`, and `portfolio-summary`.
- Depends on: finally/frontend/tsconfig.json, finally/frontend/app/layout.tsx, finally/frontend/app/globals.css
- Consumed by: Next.js App Router
- Acceptance: rendered page contains `FinAlly Trading Workstation`; watchlist contains exactly the specified foundation tickers AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX; chart section has the required chart container; portfolio displays `$10,000`; build succeeds.
- Verify: `cd finally/frontend && npm run build`

### te-2d8: finally/frontend/app/globals.css
- Scope: Provide the global reset and dark FinAlly visual foundation used by the root layout and dashboard.
- Architecture: architecture.md frontend styling section.
- Interfaces: global CSS selectors for `html`, `body`, `#__next`, and `*`; establishes zero margin/padding, full-height layout, dark background, light text, font stack, and border-box sizing.
- Depends on: <none>
- Consumed by: finally/frontend/app/layout.tsx, finally/frontend/app/page.tsx
- Acceptance: stylesheet is importable by the layout and applies the architecture-required dark background, light foreground, full-height root, reset, and box-sizing behavior without adding unsupported UI features.
- Verify: `cd finally/frontend && npm run build`

### te-n92: finally/Dockerfile
- Scope: Build the frontend static export, assemble it with the Python backend in a slim runtime image, install the pinned FastAPI/Uvicorn runtime, expose port 8000, and launch `app.main:app`.
- Architecture: architecture.md container section.
- Interfaces: multi-stage frontend-builder output `/app/frontend/out`; runtime command `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`; exposed port 8000.
- Depends on: finally/frontend/package.json, finally/frontend/tsconfig.json, finally/frontend/next.config.js, finally/backend/app/main.py
- Consumed by: finally/docker-compose.yml
- Acceptance: Docker build runs the real `npm run build`, copies backend and static export into the runtime image, installs the architecture-pinned runtime, exposes 8000, and starts the actual FastAPI app rather than a placeholder.
- Verify: `docker build -f finally/Dockerfile finally`

### te-cwv: finally/docker-compose.yml
- Scope: Define the single `app` service that builds the real Dockerfile, maps host port 8000 to container port 8000, uses `/app/backend`, mounts the database volume, and launches the FastAPI application.
- Architecture: architecture.md compose section.
- Interfaces: service `app`; build context `.` and Dockerfile `Dockerfile`; port mapping `8000:8000`; Uvicorn command targeting `app.main:app`.
- Depends on: finally/Dockerfile, finally/backend/app/main.py
- Consumed by: local deployment and the phase verification workflow
- Acceptance: compose configuration is valid, builds the real app image, exposes port 8000, and does not substitute a mock/placeholder service or command.
- Verify: `docker compose -f finally/docker-compose.yml config`

## Future considerations

Trading data, persistence, authentication, order execution, and richer chart interactions belong to later delivery phases and must not be added to these foundation beads.

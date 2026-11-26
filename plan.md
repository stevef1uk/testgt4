# Implementation plan

Active phase: `project-foundation-support`. Only the 10 `required_files` below are in scope. Later phases get their own beads.

## Bead map

### te-0x3: finally/backend/app/db/schema.sql
- Scope: SQLite DDL for users_profile, watchlist, positions, trades, portfolio_snapshots, chat_messages, all with user_id default "default" (SPEC §7).
- Architecture: finally/backend/app/db/schema.sql (Module / bead ownership; Requirements project-foundation-support).
- Interfaces: executable SQL script; no Python symbols.
- Depends on: <none>
- Consumed by: te-wdu (finally/backend/app/db/seed.py), te-44z (finally/backend/tests/test_schema.py)
- Acceptance: creates all six tables with UNIQUE(user_id, ticker) on watchlist and positions; runs cleanly against an empty sqlite3 database.
- Verify: `cd finally/backend && uv run python -c "import sqlite3;c=sqlite3.connect(':memory:');c.executescript(open('app/db/schema.sql').read());print('ok')"`

### te-wdu: finally/backend/app/db/seed.py
- Scope: lazy initialisation helper that creates schema and seeds the ten default tickers and cash balance 10000.0 for user "default" when the DB is empty.
- Architecture: finally/backend/app/db/seed.py (SPEC §7 Default Seed Data).
- Interfaces: `seed_defaults(conn: sqlite3.Connection) -> None` (idempotent).
- Depends on: te-0x3 (finally/backend/app/db/schema.sql)
- Consumed by: te-44z (finally/backend/tests/test_schema.py)
- Acceptance: inserts users_profile row id "default" with cash_balance 10000.0; inserts watchlist rows AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX; second call adds no duplicates.
- Verify: `cd finally/backend && uv run python -c "import app.db.seed"`

### te-44z: finally/backend/tests/test_schema.py
- Scope: pytest asserting schema creation, lazy seeding, and seed content.
- Architecture: finally/backend/tests/test_schema.py (Unit tests list).
- Interfaces: test functions only.
- Depends on: te-0x3 (finally/backend/app/db/schema.sql), te-wdu (finally/backend/app/db/seed.py)
- Consumed by: <none>
- Acceptance: asserts the ten exact tickers are in the watchlist; asserts cash_balance == 10000.0 for id "default"; asserts all six tables exist; no `assert True` placeholders.
- Verify: `cd finally/backend && uv run pytest tests/test_schema.py -q`

### te-zxq: finally/frontend/package.json
- Scope: Next.js 14 project manifest with build/dev/start scripts and React 18 dependencies.
- Architecture: finally/frontend/package.json (Planned file layout, Frontend).
- Interfaces: npm scripts `build` = `next build` producing static export.
- Depends on: <none>
- Consumed by: te-emx (finally/frontend/next.config.js), te-os2, te-a6p, te-g53, te-nk5 (install side effect), te-k1h (finally/Dockerfile)
- Acceptance: `npm install --ignore-scripts` succeeds and generates finally/frontend/package-lock.json.
- Verify: `cd finally/frontend && npm install --ignore-scripts && test -f package-lock.json`

### te-nk5: finally/frontend/tsconfig.json
- Scope: strict TypeScript config for the Next.js app with the next plugin and bundler module resolution.
- Architecture: finally/frontend/tsconfig.json (Planned file layout).
- Interfaces: compiler options only.
- Depends on: te-zxq (finally/frontend/package.json)
- Consumed by: te-os2, te-a6p, te-emx (build step)
- Acceptance: `include` covers `**/*.tsx` and `next-env.d.ts`; `strict` is true.
- Verify: `cd finally/frontend && npm run build`

### te-emx: finally/frontend/next.config.js
- Scope: Next config enabling `output: 'export'` so `next build` writes static files to finally/frontend/out/ (SPEC §4 Static Serving Contract; do not set distDir).
- Architecture: finally/frontend/next.config.js (Docker & Deployment, handoff to Stage 2).
- Interfaces: default export config object with `output: 'export'`.
- Depends on: te-zxq (finally/frontend/package.json)
- Consumed by: te-k1h (finally/Dockerfile via frontend build output)
- Acceptance: after `npm run build`, finally/frontend/out/index.html exists.
- Verify: `cd finally/frontend && npm run build && test -f out/index.html`

### te-os2: finally/frontend/app/layout.tsx
- Scope: root layout with metadata title "FinAlly" and import of globals.css.
- Architecture: finally/frontend/app/layout.tsx (project-foundation-support).
- Interfaces: `export default function RootLayout({ children }: { children: React.ReactNode })`.
- Depends on: te-zxq (finally/frontend/package.json), te-nk5 (finally/frontend/tsconfig.json), te-g53 (finally/frontend/app/globals.css)
- Consumed by: te-a6p (finally/frontend/app/page.tsx), te-emx (build)
- Acceptance: html element with lang en; body wraps children; title metadata equals "FinAlly".
- Verify: `cd finally/frontend && npm run build`

### te-a6p: finally/frontend/app/page.tsx
- Scope: home page rendering the dashboard skeleton: FinAlly heading, ten default tickers, $10,000 cash figure, with at least one interactive control (ticker input plus Add button or equivalent client state).
- Architecture: finally/frontend/app/page.tsx (project-foundation-support; amended in application-polish).
- Interfaces: `export default function Page()` client component.
- Depends on: te-os2 (finally/frontend/app/layout.tsx), te-g53 (finally/frontend/app/globals.css)
- Consumed by: te-k1h (Dockerfile build output)
- Acceptance: static export contains text "FinAlly", "AAPL", "$10,000"; no placeholder text such as "Coming soon".
- Verify: `cd finally/frontend && npm run build && grep -q FinAlly out/index.html`

### te-g53: finally/frontend/app/globals.css
- Scope: dark terminal theme variables and base styles using accent colours from SPEC §2.
- Architecture: finally/frontend/app/globals.css (project-foundation-support).
- Interfaces: CSS custom properties --bg-primary, --accent-yellow, --accent-blue, --accent-purple, --up, --down.
- Depends on: <none>
- Consumed by: te-os2 (finally/frontend/app/layout.tsx), te-a6p (finally/frontend/app/page.tsx)
- Acceptance: body background is #0d1117 or similar dark value; defines price-up and price-down classes.
- Verify: `cd finally/frontend && npm run build`

### te-k1h: finally/Dockerfile
- Scope: multi-stage build: Stage 1 node:20-slim runs `npm install --ignore-scripts && npm run build`; Stage 2 python:3.12-slim installs fastapi/uvicorn, copies backend and `COPY --from=frontend-builder /app/frontend/out ./frontend/out`, EXPOSE 8010, CMD uvicorn backend.app.main:app.
- Architecture: finally/Dockerfile (Docker & Deployment).
- Interfaces: image entrypoint uvicorn on port 8010.
- Depends on: te-zxq (finally/frontend/package.json), te-nk5 (finally/frontend/tsconfig.json), te-emx (finally/frontend/next.config.js), te-os2 (finally/frontend/app/layout.tsx), te-a6p (finally/frontend/app/page.tsx), te-g53 (finally/frontend/app/globals.css)
- Consumed by: phase gate (docker build)
- Acceptance: `docker build` succeeds; the export at finally/frontend/out exists in the Stage 1 image before Stage 2 COPY runs.
- Verify: `cd finally && docker build -f Dockerfile -t finally-foundation-check .`

## Integration contract

Not required for this phase (no cmd/.../main entrypoint in required_files).

## Phase context

Active phase `project-foundation-support`. Frontend build must produce finally/frontend/out/index.html before the Dockerfile COPY succeeds, so te-emx (next.config.js with output export) must land before te-k1h.

## Future considerations

- None for this phase.

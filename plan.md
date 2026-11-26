# Implementation plan

Active phase: `application-polish` (Application Polish). Covers only the six `required_files` for this phase. Later phases get their own beads.

## Bead map

### te-70n: finally/scripts/start_windows.ps1
- Scope: Windows start script for the application stack, per the deployment section of architecture.md (root and deployment files, alongside `start_mac.sh`).
- Architecture: `finally/scripts/start_windows.ps1` in the root and deployment file list; compose file is `finally/docker-compose.yml`.
- Interfaces: PowerShell script, no exported symbols.
- Depends on: `<none>` (script only invokes the compose file and env file that exist in the rig).
- Consumed by: `finally/scripts/stop_windows.ps1` (shares the same compose project).
- Acceptance:
  - Script runs `docker compose up -d --build` from `finally/` against `finally/docker-compose.yml`, so it is not a stub.
  - Script fails with a non-zero exit code and a clear message when `docker` is not on PATH.
  - Script prints the application URL on success, matching the port the compose file exposes.
  - Mirrors the behavior of `finally/scripts/start_mac.sh` except for Windows shell syntax.
- Verify: `test -f finally/scripts/start_windows.ps1 && grep -q 'docker compose' finally/scripts/start_windows.ps1`
- Bead `te-70n` is closed only after verification passes.

### te-mv3: finally/scripts/stop_windows.ps1
- Scope: Windows stop script, per the deployment section of architecture.md.
- Architecture: `finally/scripts/stop_windows.ps1` in the root and deployment file list.
- Interfaces: PowerShell script, no exported symbols.
- Depends on: `finally/scripts/start_windows.ps1` (same compose project and file).
- Consumed by: operators only; nothing imports it.
- Acceptance:
  - Script runs `docker compose down` from `finally/` against `finally/docker-compose.yml`.
  - Script is idempotent: running it when the stack is already stopped exits 0.
  - Mirrors the behavior of `finally/scripts/stop_mac.sh` except for Windows shell syntax.
- Verify: `test -f finally/scripts/stop_windows.ps1 && grep -q 'docker compose' finally/scripts/stop_windows.ps1`
- Bead `te-mv3` is closed only after verification passes.

### te-kpe: finally/.gitignore
- Scope: ignore rules for the rig, per the root file list in architecture.md.
- Architecture: `finally/.gitignore` in the root and deployment list. Owned by this phase.
- Interfaces: none.
- Depends on: `<none>`.
- Consumed by: git only.
- Acceptance:
  - Ignores `finally/frontend/node_modules/` and `finally/frontend/.next/` and `finally/frontend/out/` (generated Next.js output, per architecture generated-outputs section).
  - Ignores `finally/backend/.venv/` and Python cache directories (`__pycache__/`).
  - Does not ignore tracked source files under `finally/frontend/app/` or `finally/frontend/components/`.
- Verify: `test -f finally/.gitignore && grep -q 'node_modules' finally/.gitignore`
- Bead `te-kpe` is closed only after verification passes.

### te-i6d: finally/frontend/next-env.d.ts
- Scope: Next.js generated TypeScript environment declaration, per the generated-outputs section of architecture.md.
- Architecture: `finally/frontend/next-env.d.ts` is a generated tool output owned by this phase.
- Interfaces: none (ambient type reference only).
- Depends on: `finally/frontend/tsconfig.json` (project-foundation).
- Consumed by: `finally/frontend/app/page.tsx` and all components through the TypeScript build.
- Acceptance:
  - File exists and contains the standard Next.js reference directive for `next/types/global`.
  - `npm run build` in `finally/frontend` succeeds with this file present.
- Verify: `test -f finally/frontend/next-env.d.ts && (cd finally/frontend && npm run build)`
- Bead `te-i6d` is closed only after verification passes.

### te-627: finally/frontend/app/polish.css
- Scope: dark terminal styling, animations, loading and empty states, and accessibility, per the application-polish phase description in architecture.md.
- Architecture: `finally/frontend/app/polish.css` is in the frontend file list. Imported alongside `finally/frontend/app/globals.css` from `finally/frontend/app/layout.tsx`.
- Interfaces: CSS class names used by the components listed in `finally/frontend/app/page.tsx` (Header, Watchlist, MarketOverview, PriceChart, PortfolioSummary, PositionsTable, TradingPanel, ChatAssistant). Names must match what those components render.
- Depends on: `finally/frontend/app/globals.css`.
- Consumed by: `finally/frontend/app/layout.tsx`.
- Acceptance:
  - Defines a dark terminal color scheme and does not override `globals.css` base resets without reason.
  - Defines at least one CSS animation (keyframes) used by a loading state.
  - Defines visible focus styles for buttons and inputs (accessibility).
  - Defines empty-state styling for tables and lists (no positions, no watchlist items).
  - No placeholder rules; every selector targets a class used by a rendered component.
- Verify: `test -f finally/frontend/app/polish.css && (cd finally/frontend && npm run build)`
- Bead `te-627` is closed only after verification passes.

### te-5b4: finally/frontend/app/page.tsx
- Scope: amend the project-foundation skeleton so the dashboard mounts all eight components together, per the application-polish phase description in architecture.md.
- Architecture: `finally/frontend/app/page.tsx` imports Header, Watchlist, MarketOverview, PriceChart, PortfolioSummary, PositionsTable, TradingPanel, and ChatAssistant from `finally/frontend/components/`.
- Interfaces: default export page component at `/` (static export to `finally/frontend/out/`).
- Depends on: `finally/frontend/components/Header.tsx`, `finally/frontend/components/Watchlist.tsx`, `finally/frontend/components/MarketOverview.tsx`, `finally/frontend/components/PriceChart.tsx`, `finally/frontend/components/PortfolioSummary.tsx`, `finally/frontend/components/PositionsTable.tsx`, `finally/frontend/components/TradingPanel.tsx`, `finally/frontend/components/ChatAssistant.tsx`.
- Consumed by: `finally/frontend/app/layout.tsx` (wraps the page); the static build output.
- Acceptance:
  - Renders all eight components above on GET `/`.
  - Each imported component is a real import, not a placeholder element.
  - Contains at least one user-triggerable control whose handler runs (for example a TradingPanel submit or a Watchlist selection) so the screen is not static content-only.
  - `npm run build` in `finally/frontend` succeeds and produces `finally/frontend/out/`.
- Verify: `test -f finally/frontend/app/page.tsx && (cd finally/frontend && npm run build)`
- QA must confirm the rendered screen performs at least one user action from this bead's acceptance before reporting all_passed.
- Bead `te-5b4` is closed only after verification passes.

## Phase context

Active delivery phase `application-polish` only.

- Phase verification: `test -f finally/scripts/start_windows.ps1 && test -f finally/scripts/stop_windows.ps1 && test -f finally/.gitignore && test -f finally/frontend/next-env.d.ts && (cd finally/frontend && npm run build)`
- Later phases start automatically after QA `all_passed`.

## Future considerations

- None for this phase. Items outside SPEC.md are not added to beads.

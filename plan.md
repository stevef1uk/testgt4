# Implementation plan: project-foundation

Active phase only. Scope is the 9 required paths below. Later phases (routes, market, portfolio, llm, frontend, e2e, and the project-foundation-support Dockerfile) are deferred and get their own beads.

## Bead map

### te-0cp: finally/backend/pyproject.toml
- Scope: uv project manifest for the FastAPI backend, Python >= 3.11.
- Architecture: Backend (uv project) in architecture.md.
- Interfaces: project name and dependencies (fastapi, uvicorn; pytest in dev group). No runtime code.
- Depends on: <none>
- Consumed by: finally/backend/app/api/__init__.py, finally/backend/app/main.py, finally/backend/tests/test_health.py
- Acceptance:
  - `uv sync` in finally/backend succeeds with no resolver errors.
  - pyproject declares fastapi and uvicorn as runtime dependencies and pytest as a dev dependency.
- Verify: `cd finally/backend && uv sync`

### te-kza: finally/backend/app/api/__init__.py
- Scope: package marker that exposes the API router used by main.py. Portfolio, watchlist, and chat route modules are deferred.
- Architecture: Backend layout; HTTP routes section.
- Interfaces: `router: APIRouter` containing GET /api/health only.
- Depends on: finally/backend/pyproject.toml
- Consumed by: finally/backend/app/main.py
- Acceptance:
  - Module imports without side effects beyond building the router.
  - Router exposes GET /api/health only in this phase.
- Verify: `cd finally/backend && uv run python -c "import app.api"`

### te-7sm: finally/backend/app/main.py
- Scope: application factory `def create_app(...) -> FastAPI` with lifespan wiring. No route bodies, no SQL.
- Architecture: Module ownership table; entrypoint order in HTTP + entrypoint integration.
- Interfaces: `create_app() -> FastAPI`; module-level `app = create_app()` for uvicorn.
- Depends on: finally/backend/app/api/__init__.py, finally/backend/pyproject.toml
- Consumed by: finally/backend/tests/test_health.py
- Acceptance:
  - `import app.main` from finally/backend succeeds without starting a server.
  - `create_app()` returns a FastAPI instance that includes the api router.
  - Lifespan context manager starts and stops cleanly with no background tasks yet.
- Verify: `cd finally/backend && uv run python -c "import app.main"`

### te-sj3: finally/backend/tests/test_health.py
- Scope: unit tests for GET /api/health only.
- Architecture: SPEC Section 8 health endpoint; test layout in architecture.md.
- Interfaces: pytest tests using fastapi.testclient against create_app().
- Depends on: finally/backend/app/main.py, finally/backend/app/api/__init__.py
- Consumed by: <none>
- Acceptance:
  - Test asserts GET /api/health returns HTTP 200.
  - Test asserts the JSON body reports status "ok".
  - Test asserts an unknown path such as /api/does-not-exist returns 404.
  - No assert True placeholders and no import-only tests.
- Verify: `cd finally/backend && uv run pytest tests/test_health.py -q`

### te-15s: finally/.env
- Scope: environment file with defaults from SPEC: LLM_MOCK=true, MASSIVE_API_KEY empty (simulator mode), OpenRouter key placeholder.
- Architecture: configuration section; SPEC Section 5.
- Interfaces: variable names exactly as SPEC lists them.
- Depends on: <none>
- Consumed by: finally/docker-compose.yml
- Acceptance:
  - File exists at finally/.env.
  - MASSIVE_API_KEY is present and empty by default.
  - LLM_MOCK is present and set to true.
- Verify: `test -f finally/.env && grep -q '^LLM_MOCK=' finally/.env`

### te-dy4: finally/docker-compose.yml
- Scope: single service `app` on port 8010 with a volume mount for finally/db and env_file .env.
- Architecture: Single container, single port; deployment section.
- Interfaces: service `app`, port mapping 8010:8010, volume ./db:/app/db.
- Depends on: finally/.env
- Consumed by: finally/scripts/start_mac.sh, finally/scripts/stop_mac.sh
- Acceptance:
  - Compose file parses with `docker compose config`.
  - Port 8010 is published and the db volume is declared.
- Verify: `cd finally && docker compose -f docker-compose.yml config`

### te-acq: finally/scripts/start_mac.sh
- Scope: start script that runs the compose service on macOS, then opens http://localhost:8010.
- Architecture: deployment scripts section.
- Interfaces: executable bash, no arguments required.
- Depends on: finally/docker-compose.yml
- Consumed by: finally/scripts/stop_mac.sh
- Acceptance:
  - Script has a bash shebang and passes syntax check.
  - Script is executable (mode 755).
- Verify: `bash -n finally/scripts/start_mac.sh`

### te-h2q: finally/scripts/stop_mac.sh
- Scope: stop script that brings the compose service down without deleting the db volume.
- Architecture: deployment scripts section.
- Interfaces: executable bash, no arguments required.
- Depends on: finally/docker-compose.yml, finally/scripts/start_mac.sh
- Consumed by: <none>
- Acceptance:
  - Script has a bash shebang and passes syntax check.
  - Script does not remove volumes or finally/db contents.
- Verify: `bash -n finally/scripts/stop_mac.sh`

### te-ajb: finally/db/.gitkeep
- Scope: placeholder that keeps the db directory in git so the SQLite volume mount exists.
- Architecture: SQLite at finally/db/finally.db, volume-mounted.
- Interfaces: none.
- Depends on: <none>
- Consumed by: finally/docker-compose.yml
- Acceptance:
  - File exists at finally/db/.gitkeep.
  - No finally.db is committed by this bead.
- Verify: `test -f finally/db/.gitkeep`

## Integration contract

Not required this phase. No cmd/.../main entrypoint is in the required paths. The FastAPI entrypoint is finally/backend/app/main.py, which exposes only create_app and GET /api/health.

## Future considerations

- Routes for portfolio, watchlist, chat, and SSE stream belong to later phases.
- Dockerfile and the GET / static dashboard belong to project-foundation-support and the frontend phase.

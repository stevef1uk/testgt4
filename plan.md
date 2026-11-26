# Implementation plan

Phase: project-foundation. Scope is limited to the 10 paths in `required_files`. Later phases (routes, market, portfolio, llm, frontend) get their own beads and are out of scope here.

## Phase verification

Run from `test4/mayor/rig`. All of these must pass before the phase is marked complete:

`test -f finally/backend/app/main.py && test -f finally/backend/app/api/__init__.py && test -f finally/backend/tests/test_health.py && test -f finally/Dockerfile && test -f finally/docker-compose.yml && test -f finally/.env && test -f finally/scripts/start_mac.sh && test -f finally/scripts/stop_mac.sh && test -f finally/db/.gitkeep && (cd finally/backend && uv sync && uv run python -c "import app.main") && (cd finally/backend && uv run pytest tests/test_health.py -q)`

## Bead map

### te-0cp: finally/backend/pyproject.toml
- Scope: uv project for the `stockpilot-backend` package, pinned dependencies from architecture.md, setuptools build backend, packages `app*` only.
- Architecture: Backend (uv project) section of architecture.md.
- Acceptance: `uv sync` in `finally/backend` succeeds with no resolver errors.
- Acceptance: pytest configured with `asyncio_mode = "auto"`.
- Verify: `cd finally/backend && uv sync`

### te-7sm: finally/backend/app/main.py
- Scope: FastAPI app object with title "StockPilot" and version "0.1.0"; exposes `GET /api/health` returning `{"status": "ok"}`. Later phases register routers here.
- Architecture: `app/main.py` in the Backend section; SPEC single origin on port 8010.
- Acceptance: `import app.main` succeeds from `finally/backend`.
- Acceptance: `app` is a module-level FastAPI instance (no factory required for this phase).
- Verify: `cd finally/backend && uv run python -c "import app.main"`

### te-kza: finally/backend/app/api/__init__.py
- Scope: package marker for the API layer. Docstring only; no route registration in this phase.
- Architecture: `app/api/__init__.py` in the Backend section.
- Acceptance: the package imports cleanly as `app.api`.
- Verify: `cd finally/backend && uv run python -c "import app.api"`

### te-sj3: finally/backend/tests/test_health.py
- Scope: smoke test that `GET /api/health` returns 200 with `{"status": "ok"}` using FastAPI TestClient.
- Architecture: tests section of the Backend layout in architecture.md.
- Acceptance: `uv run pytest tests/test_health.py -q` passes.
- Verify: `cd finally/backend && uv run pytest tests/test_health.py -q`

### te-wbv: finally/Dockerfile
- Scope: multi-stage build. Stage one builds the Next.js static export to `frontend/out`. Stage two is python:3.12-slim, copies backend and frontend output, exposes 8010, and runs uvicorn on 0.0.0.0:8010.
- Architecture: Root and deployment section; single container, single origin.
- Acceptance: file exists at `finally/Dockerfile` and names port 8010 in EXPOSE and CMD.
- Verify: `test -f finally/Dockerfile && grep -q 8010 finally/Dockerfile`

### te-dy4: finally/docker-compose.yml
- Scope: test-harness compose file only. The application server runs on the host, not in this compose service.
- Architecture: Root and deployment section.
- Acceptance: file exists and parses as YAML.
- Verify: `test -f finally/docker-compose.yml`

### te-15s: finally/.env
- Scope: local configuration with BACKEND_HOST=127.0.0.1, BACKEND_PORT=8010, OPENROUTER_API_KEY placeholder, LLM_MOCK=true, MASSIVE_API_KEY empty.
- Architecture: Root and deployment section.
- Acceptance: defines BACKEND_PORT=8010 and LLM_MOCK.
- Verify: `test -f finally/.env`

### te-acq: finally/scripts/start_mac.sh
- Scope: loads `.env`, builds frontend export if missing, prefers backend venv python, execs uvicorn on BACKEND_HOST and BACKEND_PORT.
- Architecture: Root and deployment section.
- Acceptance: script passes `bash -n`.
- Verify: `bash -n finally/scripts/start_mac.sh`

### te-h2q: finally/scripts/stop_mac.sh
- Scope: loads `.env`, finds the listener on BACKEND_PORT (default 8010) and kills it.
- Architecture: Root and deployment section.
- Acceptance: script passes `bash -n`.
- Verify: `bash -n finally/scripts/stop_mac.sh`

### te-ajb: finally/db/.gitkeep
- Scope: keeps the `finally/db/` directory in git so the SQLite volume mount target exists.
- Architecture: database location `finally/db/finally.db`.
- Acceptance: file exists at `finally/db/.gitkeep`.
- Verify: `test -f finally/db/.gitkeep`

## Future considerations

- Phase-specific acceptance for routes, market simulator, portfolio, and LLM belongs to their own phases.

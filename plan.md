# Implementation plan

Phase: project-foundation (Project Foundation). This plan covers only the 10 `required_files` for this phase. Later phases get their own beads.

## Bead map

### te-0cp: finally/backend/pyproject.toml
- Scope: Create the backend Python project manifest per architecture.md.
- Architecture: architecture.md, backend project layout section.
- Verify: `test -f finally/backend/pyproject.toml`
- Acceptance:
  - File exists at `finally/backend/pyproject.toml`.
  - Declares the project metadata and dependencies named in architecture.md, with no placeholder content.
  - Bead `te-0cp` is closed only after its Verify line passes.

### te-kza: finally/backend/app/api/__init__.py
- Scope: Create the API package initializer per architecture.md.
- Architecture: architecture.md, backend API package section.
- Verify: `test -f finally/backend/app/api/__init__.py`
- Acceptance:
  - File exists at `finally/backend/app/api/__init__.py`.
  - Makes `app.api` importable as a package, with no placeholder content.
  - Bead `te-kza` is closed only after its Verify line passes.

### te-7sm: finally/backend/app/main.py
- Scope: Create the FastAPI application entry module per architecture.md.
- Architecture: architecture.md, backend entrypoint section.
- Verify: `test -f finally/backend/app/main.py`
- Acceptance:
  - File exists at `finally/backend/app/main.py`.
  - Defines the application object named in architecture.md so `import app.main` succeeds.
  - Bead `te-7sm` is closed only after its Verify line passes.

### te-wbv: finally/Dockerfile
- Scope: Create the container build file per architecture.md.
- Architecture: architecture.md, container section.
- Verify: `test -f finally/Dockerfile`
- Acceptance:
  - File exists at `finally/Dockerfile`.
  - Build steps match the backend layout in architecture.md.
  - Bead `te-wbv` is closed only after its Verify line passes.

### te-dy4: finally/docker-compose.yml
- Scope: Create the compose definition per architecture.md.
- Architecture: architecture.md, compose section.
- Verify: `test -f finally/docker-compose.yml`
- Acceptance:
  - File exists at `finally/docker-compose.yml`.
  - Service and volume names match architecture.md.
  - Bead `te-dy4` is closed only after its Verify line passes.

### te-15s: finally/.env
- Scope: Create the environment template per architecture.md.
- Architecture: architecture.md, configuration section.
- Verify: `test -f finally/.env`
- Acceptance:
  - File exists at `finally/.env`.
  - Lists only the variables named in SPEC.md and architecture.md.
  - Bead `te-15s` is closed only after its Verify line passes.

### te-dwh: finally/.gitignore
- Scope: Create the ignore rules per architecture.md.
- Architecture: architecture.md, repository hygiene section.
- Verify: `test -f finally/.gitignore`
- Acceptance:
  - File exists at `finally/.gitignore`.
  - Ignores generated and local-only artifacts listed in architecture.md.
  - Bead `te-dwh` is closed only after its Verify line passes.

### te-ajb: finally/db/.gitkeep
- Scope: Create the empty database directory marker per architecture.md.
- Architecture: architecture.md, data directory section.
- Verify: `test -f finally/db/.gitkeep`
- Acceptance:
  - File exists at `finally/db/.gitkeep`.
  - Keeps the `finally/db/` directory tracked in git.
  - Bead `te-ajb` is closed only after its Verify line passes.

### te-acq: finally/scripts/start_mac.sh
- Scope: Create the macOS start script per architecture.md.
- Architecture: architecture.md, scripts section.
- Verify: `bash -n finally/scripts/start_mac.sh`
- Acceptance:
  - File exists at `finally/scripts/start_mac.sh` and parses under `bash -n`.
  - Starts the services described in architecture.md and nothing beyond them.
  - Bead `te-acq` is closed only after its Verify line passes.

### te-h2q: finally/scripts/stop_mac.sh
- Scope: Create the macOS stop script per architecture.md.
- Architecture: architecture.md, scripts section.
- Verify: `bash -n finally/scripts/stop_mac.sh`
- Acceptance:
  - File exists at `finally/scripts/stop_mac.sh` and parses under `bash -n`.
  - Stops the services started by `start_mac.sh`.
  - Bead `te-h2q` is closed only after its Verify line passes.

## Phase gate

The phase gate runs once all 10 beads are closed. It is owned by QA, not by individual beads:

`test -f finally/backend/app/main.py && test -f finally/scripts/start_mac.sh && (cd finally/backend && uv sync && uv run python -c "import app.main")`

## Future considerations

Features outside this phase (chat, portfolio, market data, frontend) are deferred to their own phases.

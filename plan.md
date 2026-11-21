# Implementation plan

## Active phase

This plan covers only the `project-foundation-support` phase and its ten required
paths. The implementation must preserve the repository-relative `finally/`
prefixes. Later backend, frontend, and application phases are out of scope.

## Bead map

### te-t6p: finally/planning/PLAN.md
- Scope: Add the checked-in project planning document at the path required by the
  phase; describe the phased delivery, project layout, and the foundation
  support files without adding implementation code.
- Architecture: `architecture.md` project-foundation-support planning artifact
  and the project layout/phase contract.
- Interfaces: Markdown artifact consumed by maintainers and the delivery
  workflow; it must identify the `finally/` tree and the active phase.
- Depends on: `<none>`
- Consumed by: `<none>`
- Acceptance: `finally/planning/PLAN.md` exists, is readable Markdown, names the
  active project-foundation-support scope, and does not claim later-phase source
  files are part of this phase.
- Verify: `test -f finally/planning/PLAN.md`

### te-nat: finally/scripts/start_mac.sh
- Scope: Implement the macOS startup helper using the repository's documented
  project commands and paths; make it executable and keep it suitable for
  invocation from the project root.
- Architecture: `architecture.md` platform script conventions and macOS
  start/stop support.
- Interfaces: shell entrypoint `finally/scripts/start_mac.sh`; it is invoked
  by a developer on macOS and must start the foundation's local services in
  the prescribed order.
- Depends on: finally/.env
- Consumed by: finally/scripts/stop_mac.sh
- Acceptance: the file exists, has a shell shebang, uses the `finally/` layout
  rather than obsolete root paths, and starts the services specified by SPEC
  without embedding secrets or inventing additional services.
- Verify: `test -x finally/scripts/start_mac.sh` and `sh -n finally/scripts/start_mac.sh`

### te-3m4: finally/scripts/stop_mac.sh
- Scope: Implement the matching macOS shutdown helper, addressing the services
  started by the macOS start helper and returning a useful non-success status
  when its prescribed command fails.
- Architecture: `architecture.md` platform script conventions and macOS
  start/stop pairing.
- Interfaces: shell entrypoint `finally/scripts/stop_mac.sh`; it is the
  operator-facing inverse of `start_mac.sh`.
- Depends on: finally/scripts/start_mac.sh
- Consumed by: `<none>`
- Acceptance: the file exists, is executable, has valid shell syntax, uses the
  same project/service names as the start helper, and stops only the services
  required by SPEC.
- Verify: `test -x finally/scripts/stop_mac.sh` and `sh -n finally/scripts/stop_mac.sh`

### te-bzh: finally/scripts/start_windows.ps1
- Scope: Implement the Windows PowerShell startup helper with the same service
  behavior and repository-relative paths as the macOS helper.
- Architecture: `architecture.md` Windows platform script conventions and
  cross-platform start/stop parity.
- Interfaces: PowerShell entrypoint `finally/scripts/start_windows.ps1`.
- Depends on: finally/.env
- Consumed by: finally/scripts/stop_windows.ps1
- Acceptance: the script exists, is valid PowerShell text, starts the SPEC
  services using the documented commands, and does not add unrelated service
  orchestration or hard-coded credentials.
- Verify: `test -f finally/scripts/start_windows.ps1`

### te-e5f: finally/scripts/stop_windows.ps1
- Scope: Implement the Windows PowerShell shutdown counterpart for the services
  started by `start_windows.ps1`.
- Architecture: `architecture.md` Windows platform script conventions and
  start/stop pairing.
- Interfaces: PowerShell entrypoint `finally/scripts/stop_windows.ps1`.
- Depends on: finally/scripts/start_windows.ps1
- Consumed by: `<none>`
- Acceptance: the script exists, uses the same documented service identifiers
  as the Windows start helper, and stops the phase's services without adding
  configuration knobs not present in SPEC.
- Verify: `test -f finally/scripts/stop_windows.ps1`

### te-zy3: finally/.env
- Scope: Add the checked-in environment template/defaults required by the
  foundation support tooling. Values must be non-secret placeholders or the
  exact defaults specified by SPEC.
- Architecture: `architecture.md` environment/configuration contract.
- Interfaces: dotenv file consumed by local scripts and CI; variable names must
  be the names specified by SPEC/architecture.
- Depends on: `<none>`
- Consumed by: finally/scripts/start_mac.sh, finally/scripts/start_windows.ps1,
  finally/.github/workflows/ci.yml, finally/backend/db/schema.py
- Acceptance: `finally/.env` exists at the exact path, contains the required
  keys with valid dotenv syntax, contains no real credentials, and does not
  introduce unspecified options.
- Verify: `test -f finally/.env`

### te-joj: finally/.gitignore
- Scope: Add ignore rules for generated local state, databases, environment
  secrets, caches, and platform artifacts required by the architecture.
- Architecture: `architecture.md` repository hygiene and generated-state rules.
- Interfaces: Git ignore configuration governing the whole `finally/` tree.
- Depends on: `<none>`
- Consumed by: finally/.env, finally/db/.gitkeep, finally/backend/db/schema.py
- Acceptance: the file exists at the repository root, ignores generated/runtime
  artifacts called out by SPEC, does not ignore tracked source or the required
  database placeholder, and does not replace the required `.env` template.
- Verify: `test -f finally/.gitignore`

### te-bn9: finally/.github/workflows/ci.yml
- Scope: Add the CI workflow described by SPEC. It must run from the repository
  layout in architecture, install only declared dependencies, and execute the
  phase's required checks.
- Architecture: `architecture.md` CI workflow contract and supported runtime.
- Interfaces: GitHub Actions workflow triggered by the SPEC-required events;
  workflow steps provide the repository verification gate.
- Depends on: finally/.gitignore, finally/backend/db/schema.py
- Consumed by: `<none>`
- Acceptance: the workflow is valid YAML, uses the required trigger and runtime,
  checks out the repository, runs the documented backend/schema checks, and
  does not reference future-phase files or unavailable services.
- Verify: `test -f finally/.github/workflows/ci.yml`

### te-86r: finally/db/.gitkeep
- Scope: Preserve the empty database directory in version control without
  storing a generated database.
- Architecture: `architecture.md` database layout and generated-artifact rules.
- Interfaces: empty placeholder at `finally/db/.gitkeep`; the schema/runtime
  uses `finally/db/` as its database location.
- Depends on: finally/.gitignore
- Consumed by: finally/backend/db/schema.py
- Acceptance: the exact file exists, is empty (or contains only the conventional
  placeholder content), and keeps `finally/db/` present without committing a
  runtime database.
- Verify: `test -f finally/db/.gitkeep`

### te-s2x: finally/backend/db/schema.py
- Scope: Implement the initial database schema module at the architecture's
  backend database path, including the required database location and schema
  definitions only.
- Architecture: `architecture.md` backend database/schema section; follow the
  SPEC data model and initialization contract exactly.
- Interfaces: Python module `finally/backend/db/schema.py`; expose only the
  schema/database symbols specified by SPEC and architecture, and use the
  `finally/db/` location rather than a root-level database.
- Depends on: finally/db/.gitkeep, finally/.env
- Consumed by: finally/.github/workflows/ci.yml
- Acceptance: the module exists, compiles, creates the SPEC-required schema
  idempotently at the documented location, uses the specified table/column
  definitions and constraints, and contains no API/server features assigned to
  later phases.
- Verify: `test -f finally/backend/db/schema.py && python3 -m py_compile finally/backend/db/schema.py`

## Phase verification

Run the active-phase verification exactly as specified:
`test -f finally/planning/PLAN.md && test -f finally/scripts/start_mac.sh && test -f finally/scripts/stop_mac.sh && test -f finally/scripts/start_windows.ps1 && test -f finally/scripts/stop_windows.ps1 && test -f finally/.env && test -f finally/.gitignore && test -f finally/.github/workflows/ci.yml && test -f finally/db/.gitkeep && test -f finally/backend/db/schema.py`

## Future considerations

Later phases may add application routes, frontend behavior, and their tests.
Those files are intentionally not acceptance criteria for this phase.

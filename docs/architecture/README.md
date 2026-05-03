# Architecture

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

This document defines the architecture rules that Codex must follow when changing this repository. The rules favor predictable boundaries, small files, explicit validation, and machine-checkable structure.

## System Shape

```text
apps/web
  Vue UI, client state, API client, browser-only validation

services/api
  FastAPI routes, request validation, application services, integrations, repositories

postgres:18
  local and production-compatible relational persistence

docs
  source of record for product, architecture, execution plans, references, generated facts

tools, lint-rules, scripts
  mechanical enforcement for Codex and CI
```

## Dependency Direction

Allowed direction:

```text
UI -> API client -> backend HTTP contract
backend routes -> schemas -> services -> repositories/integrations
tools -> repository files
docs -> may reference all layers
```

Forbidden direction:

```text
backend -> apps/web
frontend -> backend internals
routes -> database driver directly
domain service -> FastAPI request/response objects
repository -> UI concepts
```

## Backend Layers

- `services/api/app/main.py`: FastAPI app creation and route registration only.
- `services/api/app/routes/`: HTTP endpoints; thin orchestration only.
- `services/api/app/schemas/`: Pydantic request/response models.
- `services/api/app/services/`: business/application logic.
- `services/api/app/repositories/`: persistence access once a database is introduced.
- `services/api/app/integrations/`: external sources such as Product Hunt, PitchWall, BetaList.
- `services/api/app/core/`: settings, logging, errors, observability.

PostgreSQL access must enter through repository modules. API routes and services cannot contain raw SQL once persistence is introduced.

## Frontend Layers

- `apps/web/src/main.ts`: app bootstrapping only.
- `apps/web/src/App.vue`: shell composition only.
- `apps/web/src/pages/`: routed screens.
- `apps/web/src/components/`: reusable UI components with no data fetching unless named `*Container`.
- `apps/web/src/features/`: domain feature modules.
- `apps/web/src/api/`: typed HTTP clients.
- `apps/web/src/stores/`: client state.
- `apps/web/src/types/`: shared frontend types.

## Cross-Cutting Concerns

- Logging enters through `services/api/app/core/logging.py`.
- Configuration enters through `services/api/app/core/settings.py`.
- Errors use explicit typed exceptions and stable error codes.
- Validation lives at system boundaries: Pydantic for backend input/output, form/schema validation for frontend input.
- Metrics and traces are created in boundary middleware or service-level instrumentation, not scattered ad hoc.

## Machine-Checkable Rules

The following rules must be enforced by CI over time:

1. Required root docs must exist and contain `Last reviewed:`.
2. `AGENTS.md` must stay under 180 lines.
3. Backend route files must not import database drivers directly.
4. Frontend files must not import from `services/api`.
5. Files under `apps/web/src/components` must not call `fetch` directly.
6. New external integrations must have a doc entry under `docs/references/`.
7. Exec plans in `active/` must include status, verification, rollback, and decision log sections.
8. Completed plans must move to `completed/` and include outcome and follow-up items.
9. Every new API route must have a schema and at least one test or documented test gap.
10. Shared utilities must include a comment explaining the second caller or a link to the exec plan that created them.

## Add Feature Change Scope

For a normal feature, Codex may change:

- one feature module under `apps/web/src/features/`
- one route/service/schema slice under `services/api/app/`
- focused tests
- relevant docs and exec plan

Codex should create a plan before touching broad cross-cutting areas such as auth, database schema, logging format, CI, or architecture rules.

## Runtime Baseline

- Local runtime is Docker Compose.
- PostgreSQL version is 18.
- Node version is 22.
- Backend containers run Python 3.12+.
- Local tests that require runtime services should run through `scripts/agent-task.sh docker-test`.

## Forbidden Patterns

- route handlers containing product recommendation logic directly
- UI components containing source-scraping logic
- test snapshots replacing behavior assertions
- silent `except Exception`
- logging secrets or raw user prompts without redaction
- adding generated files without a source command in `docs/generated/README.md`
- using external source claims without date and source notes

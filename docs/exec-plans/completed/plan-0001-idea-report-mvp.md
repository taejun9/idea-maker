# PLAN-0001 Idea Report MVP

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Completed: 2026-05-03
Related docs: `docs/product-specs/index.md`, `docs/architecture/README.md`, `docs/architecture/backend.md`, `docs/architecture/frontend.md`
Branch: `codex/plan-0001-idea-report-mvp`
Worktree: `.worktrees/plan-0001-idea-report-mvp`

## Goal

Build the first vertical slice for generating an idea report from a short user prompt.

## Non-Goals

- real account system
- paid report export
- production scraping infrastructure
- authoritative market sizing

## Assumptions

- Backend starts with deterministic placeholder recommendation data until source integrations are implemented.
- Product Hunt, PitchWall, and BetaList facts must be fetched only when a current-data task explicitly requires it.
- Domestic and overseas competitors are separate report sections.

## Constraints

- Keep route handlers thin.
- Keep frontend API calls inside `apps/web/src/api/`.
- All report output must include source confidence fields even if placeholder data is used.
- Do not introduce a database in this plan.
- Local runtime tests use Docker Compose.
- PostgreSQL 18 is available even if persistence is not introduced in this plan.

## Task Breakdown

- [x] Define `IdeaReportRequest` and `IdeaReportResponse` schemas.
- [x] Implement report service with deterministic sample output.
- [x] Add `POST /api/idea-reports`.
- [x] Add frontend form and report result view.
- [x] Add backend tests for validation and response shape.
- [x] Add frontend unit test for report rendering.
- [x] Update generated API contract docs.
- [x] Run `scripts/agent-task.sh verify`.

## Verification

- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- Manual or Codex browser verification of the report workflow

## Rollback Strategy

- Revert route registration and frontend page wiring.
- Keep schemas if harmless and documented; otherwise remove the full vertical slice.
- Restore previous generated docs.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Start with deterministic source placeholders | Keeps MVP testable before external integrations. |
| 2026-05-03 | Separate domestic and overseas competitors in schema | Matches product value and report readability. |

## Progress

2026-05-03: Resumed implementation. Backend schema/service/route exists; remaining work is frontend API integration, report rendering, generated API contract docs, verification, and completion move.

## Outcome

- Added a typed frontend API client under `apps/web/src/api/`.
- Added the idea report feature view with form submission, loading/error states, and structured report rendering.
- Added local CORS support for the Docker Compose web origin.
- Added backend validation/CORS tests and frontend API rendering tests.
- Added generated API contract documentation.
- Added `npm run docker:up` as a root script for the Docker Compose runtime.

## Verification Evidence

- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- `npm run docker:up`
- `curl http://127.0.0.1:8000/health`
- `curl -X POST http://127.0.0.1:8000/api/idea-reports`
- Playwright browser verification at `http://127.0.0.1:5173`: submitted the default idea and saw overview, domestic/overseas competitors, source references, and validation steps render.

## Definition of Done

- A user can enter an idea and receive a structured report.
- Backend and frontend tests pass.
- Report schema includes source and confidence metadata.
- Product spec and generated API docs are updated.

## Follow-Up Cleanup

- Added real source collector plan as `docs/exec-plans/active/plan-0005-source-collector.md`.
- Add database persistence plan.
- Add export/share plan.

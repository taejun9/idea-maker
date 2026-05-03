# PLAN-0020 Report History Pages

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/architecture/README.md, docs/architecture/frontend.md, docs/architecture/backend.md, docs/product-specs/index.md, docs/operations/security.md, docs/generated/api-contract.md, docs/generated/db-schema.md, docs/observability/README.md, docs/exec-plans/tech-debt-tracker.md
Roles: trail-guide, frontend-crafter, api-crafter, doc-keeper, quality-auditor

## Goal

Add pages that let users view reports they previously looked up and reopen a detailed report.

## Non-Goals

- Change the report generation workflow.
- Add authentication, ownership, or multi-user permissions.
- Change external research integrations or source collection behavior.
- Introduce broad persistence architecture beyond what this feature requires.

## Assumptions

- "Previously looked up reports" means report records created by the report API and saved for later lookup.
- The Docker runtime should persist report history in PostgreSQL 18; local unit tests can use an in-memory repository when `DATABASE_URL` is absent.
- The frontend should route users to a report list and a report detail page without importing backend internals.

## Constraints

- Keep frontend data access in `apps/web/src/api/`.
- Keep route handlers thin and use backend schemas/services/repositories.
- Use Docker-based verification when frontend or backend behavior changes.
- Keep documentation updates in the same branch.

## Task Breakdown

- [x] Inspect existing report data model, API routes, frontend report flow, and tests.
- [x] Add or reuse backend report list/detail API support through existing boundaries.
- [x] Add frontend routes and pages for report history list and report detail.
- [x] Add focused tests for new API/client/page behavior.
- [x] Update product or architecture docs if the user-facing report navigation changes.
- [x] Run required verification, complete the plan, commit, merge to `main`, push, and clean up the worktree.

## Verification

- `scripts/agent-task.sh doctor`
- Focused backend and frontend tests relevant to report history/detail.
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test` if runtime behavior changes and Docker is available.

Evidence:

- `scripts/agent-task.sh doctor`: passed.
- `scripts/agent-task.sh docker-test`: passed backend pytest, Ruff, frontend build, and frontend Vitest.
- `scripts/agent-task.sh verify`: passed repository gates; local backend/frontend steps skipped because local dependencies are not installed, covered by Docker tests.
- Playwright browser check on Docker Compose ports `WEB_PORT=25174`, `API_PORT=28001`: generated a report, opened its detail page, and viewed it from the report history list.

## Rollback Strategy

Revert the feature commit to remove the new report history API/page changes. If persistence changes are introduced, revert the schema/repository changes with the same commit and keep existing report generation endpoints intact.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Use `PLAN-0020` for report history pages. | Existing completed plans end at `PLAN-0019`, and active plans are empty. |
| 2026-05-03 | Treat report history as a user-facing navigation feature, not a generation-flow rewrite. | The request asks for list and detail pages for already looked-up reports. |
| 2026-05-03 | Add PostgreSQL-backed report persistence with an in-memory repository fallback for tests. | Report history must survive refresh and Docker runtime API process usage, while routine unit tests should not require a non-Docker database. |
| 2026-05-03 | Use hash routes for frontend history pages instead of adding `vue-router`. | The current app has no router dependency, and hash routes support direct list/detail navigation with minimal surface area. |

## Progress

- 2026-05-03: Request-intake meeting completed and dedicated worktree branch created.
- 2026-05-03: Implemented report identity fields, repository persistence, list/detail API routes, history pages, and focused tests.
- 2026-05-03: Updated product, API contract, DB schema, security, observability, and debt docs.
- 2026-05-03: Local quick tests were blocked by missing local pytest/Vitest dependencies; Docker verification remains required.
- 2026-05-03: Docker verification, repository `verify`, and Playwright UI flow checks passed.

## Outcome

Added saved report history support:

- `POST /api/idea-reports` now returns and stores report identity metadata.
- `GET /api/idea-reports` returns newest-first report summaries.
- `GET /api/idea-reports/{report_id}` returns saved report detail or a stable not-found error.
- Docker runtime persists reports in PostgreSQL 18; tests use an in-memory repository override.
- Frontend users can navigate to `#/reports` and `#/reports/:id` for list/detail views.

## Definition of Done

- Users can open a report history list page.
- Users can open a detail page for a selected report.
- New frontend/backend behavior is covered by focused tests or documented test gaps.
- Required repository verification passes.
- The active plan is completed and moved to `docs/exec-plans/completed/`.

## Follow-Up Cleanup

- DEBT-0008 tracks replacing repository-managed startup DDL with versioned migrations before broader persistence work.

# PLAN-0022 Idea Intake Answer Persistence

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/product-specs/index.md, docs/architecture/README.md, docs/architecture/frontend.md, docs/architecture/backend.md, docs/generated/api-contract.md, docs/generated/db-schema.md
Roles: trail-guide, api-crafter, frontend-crafter, doc-keeper, quality-auditor

## Goal

Let users enter Q1-Q5 idea intake answers, persist those answers with the saved report in PostgreSQL, and delete saved reports from the report history list.

## Non-Goals

- Do not implement photo file upload or drag-and-drop image placement.
- Do not split report JSON into new relational answer tables.
- Do not add authentication or per-user ownership.
- Do not change external research adapters or source collector behavior.

## Assumptions

- Persisting Q1-Q5 answers inside the existing `idea_reports.report` JSONB payload satisfies the DB storage requirement for this task.
- The list delete button should remove the saved report record and update the visible list without navigating away.
- Delete remains an anonymous MVP operation because report history currently has no auth or ownership layer.

## Constraints

- Keep frontend data access in `apps/web/src/api/`.
- Keep backend routes thin and place persistence operations behind repository/service boundaries.
- Backend validation remains authoritative; frontend validation is for UX only.
- Update product/API docs when report behavior and contract change.

## Task Breakdown

- [x] Inspect current report schema, repository, list UI, and tests.
- [x] Add backend answer request/response models and persist them in report JSON.
- [x] Add report deletion service/repository/API support.
- [x] Add frontend Q1-Q5 answer inputs and render saved answers in reports.
- [x] Add delete button to the report history list and update local state after delete.
- [x] Update focused backend/frontend tests.
- [x] Update product/API docs and DB schema notes.
- [x] Run required verification while the plan is active.
- [x] Complete and move this plan after verification.

## Outcome

Added Q1-Q5 answer input support to the report creation flow. Submitted answers are validated by the API, embedded in the saved `IdeaReportResponse.idea_intake_questions` payload, persisted in PostgreSQL through the existing `idea_reports.report` JSONB column, and rendered on generated and saved report detail views. Added a report history delete button backed by `DELETE /api/idea-reports/{report_id}`.

## Verification

- `scripts/agent-task.sh doctor`
- Focused backend/frontend Docker tests for answer persistence and deletion.
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- Browser check for entering Q1-Q5, seeing saved answers, and deleting from list.

Evidence:

- `scripts/agent-task.sh doctor`: passed.
- Focused backend Docker test `docker compose run --rm api python -m pytest services/api/tests/test_idea_reports.py`: passed 17 tests.
- Focused frontend Docker test `docker compose run --rm --no-deps web npm run --workspace apps/web test -- app.spec.ts`: passed 10 tests.
- Focused frontend Docker build `docker compose run --rm --no-deps web npm run --workspace apps/web build`: passed.
- `scripts/agent-task.sh verify`: passed repository gates; local backend/frontend steps skipped because local dependencies are not installed, covered by Docker tests.
- `scripts/agent-task.sh docker-test`: passed backend pytest, Ruff, frontend build, and frontend Vitest.
- Playwright browser check on Docker Compose ports `WEB_PORT=25176`, `API_PORT=28003`: entered Q1-Q5 answers, generated a report, opened the saved detail page and confirmed persisted answers, deleted from the history list, then confirmed the deleted report returned HTTP 404.

## Rollback Strategy

Revert the schema, service, repository, route, frontend, tests, and docs changes. Existing report generation and history lookup should continue to work because the new answer fields are optional and saved in the report JSON payload.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Store Q1-Q5 answers in the saved report JSONB payload. | Current persistence model already stores full report detail JSON and avoids premature relational schema design. |
| 2026-05-03 | Add delete as a backend repository/service operation with frontend list control. | The user explicitly requested deletion from the list, and persistence must remove the DB record. |

## Progress

- 2026-05-03: Request intake meeting completed; scope updated to include list deletion.
- 2026-05-03: Implemented answer persistence, report deletion, frontend controls, tests, and docs.
- 2026-05-03: Required verification and browser checks passed; plan completed.

## Definition of Done

- Users can enter Q1-Q5 answers before report generation.
- Saved report detail includes the submitted Q1-Q5 answers after reload.
- Report history list includes a delete button that removes the DB record and updates the list.
- Tests and docs cover the new contract and behavior.
- Required verification passes.
- Plan is completed and moved to `docs/exec-plans/completed/`.

## Follow-Up Cleanup

- Track photo upload/drag-and-drop implementation separately if needed.

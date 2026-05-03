# PLAN-0021 Report Input Questions

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/product-specs/index.md, docs/architecture/README.md, docs/architecture/frontend.md, docs/architecture/backend.md, docs/generated/api-contract.md
Roles: trail-guide, api-crafter, frontend-crafter, doc-keeper, quality-auditor

## Goal

Add the requested Q1-Q5 idea intake questions and business-field options to the report content generated or displayed by the product.

## Non-Goals

- Do not redesign the intake form.
- Do not add a new image upload or drag-and-drop image placement implementation unless the existing report contract already supports it.
- Do not change external research source behavior.

## Assumptions

- "보고서 내용" refers to the report output surfaced by the existing API/UI, not a separate document artifact.
- The requested image guidance should be represented as report content/copy unless existing image data structures require a deeper contract change.
- The business-field option list is fixed copy for this task.

## Constraints

- Keep frontend and backend boundaries intact.
- Backend route handlers must stay thin; report generation logic remains in service modules.
- Update product docs when the report's user-facing content changes.
- Use Docker-oriented verification commands required by the repository where feasible.

## Task Breakdown

- [x] Locate report generation and display paths.
- [x] Add Q1-Q5 content in the smallest existing report/content boundary.
- [x] Update focused tests for the changed report content.
- [x] Update product docs for the new report content.
- [x] Run required verification while the plan is active.
- [x] Complete and move this plan after verification.

## Outcome

Added a dedicated `idea_intake_questions` report response section containing the requested Q1-Q5 prompts, required-state copy, Q2-Q4 photo placement guidance, and Q5 business-field options. The frontend now renders this section in both newly generated reports and saved report detail pages. Product and generated API contract docs were updated with the new report content.

## Verification

- `scripts/agent-task.sh doctor`
- Focused backend/frontend tests for changed behavior.
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test` if runtime behavior is affected and Docker is available.

Evidence:

- `scripts/agent-task.sh doctor`: passed.
- Focused backend Docker test `docker compose run --rm api python -m pytest services/api/tests/test_idea_reports.py`: passed 11 tests before the backfill test, then covered by full Docker test after adding the backfill test.
- Focused frontend Docker test `docker compose run --rm --no-deps web npm run --workspace apps/web test -- app.spec.ts`: passed 9 tests.
- `scripts/agent-task.sh verify`: passed repository gates; local backend/frontend steps skipped because local dependencies are not installed, covered by Docker tests.
- `scripts/agent-task.sh docker-test`: passed backend pytest, Ruff, frontend build, and frontend Vitest.
- Playwright browser check on Docker Compose ports `WEB_PORT=25175`, `API_PORT=28002`: generated a report and confirmed the Q1-Q5 section on both the generated report and saved detail page.

## Rollback Strategy

Revert the report content/schema/template changes and restore this plan to active or remove the branch before merge if verification fails.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Add Q1-Q5 as report content in the existing report boundary. | User requested report content addition, not a new intake workflow. |

## Progress

- 2026-05-03: Request intake meeting completed and active plan created.
- 2026-05-03: Added report response content, frontend section, focused tests, and docs.
- 2026-05-03: Required verification and browser checks passed; plan completed.

## Definition of Done

- Report content includes all requested Q1-Q5 copy and business-field options.
- Relevant tests and docs reflect the new content.
- Required verification passes.
- Plan is completed and moved to `docs/exec-plans/completed/`.

## Follow-Up Cleanup

- None known.

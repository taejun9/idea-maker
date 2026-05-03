# PLAN-0026 Report List Q5

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/product-specs/index.md, docs/architecture/frontend.md, docs/architecture/backend.md
Roles: frontend-crafter, api-crafter, trail-guide, doc-keeper, quality-auditor

## Goal

Show each report's Q5 business field in the report history list so users can scan saved reports by business field before opening a detail page.

## Non-Goals

- Do not change the Q1-Q4 display model in the history list.
- Do not change report generation or Q5 inference behavior.
- Do not add new filtering or sorting controls.

## Assumptions

- The saved report payload already contains `idea_intake_questions`; the Q5 answer can be derived from that payload for summaries.
- Older saved reports may have an empty Q5 answer, so the summary must tolerate a missing value.
- The list API contract should carry Q5 explicitly rather than making the frontend parse nested report payloads.

## Constraints

- Backend summary creation stays in service/schema boundaries, not route logic.
- Frontend list rendering uses typed API data from `apps/web/src/types`.
- Product docs must reflect the list contract change.
- Verification must run through the repository task harness and Docker tests.

## Task Breakdown

- [x] Inspect current report list API, repository mapping, frontend list UI, and tests.
- [x] Add Q5 business field to report list summary schema/service output.
- [x] Update frontend types and history list rendering.
- [x] Add backend and frontend tests for Q5 in list summaries.
- [x] Update product docs.
- [x] Complete verification.

## Verification

- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh doctor`
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- Browser or Playwright check for the report history list if Docker Compose starts cleanly.

## Rollback Strategy

Revert the report summary schema/service addition, frontend list rendering, tests, and product docs. Existing detail report payloads remain unchanged.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Add Q5 as a first-class report summary field. | It keeps the frontend typed and avoids parsing `idea_intake_questions` in the list page. |

## Progress

- 2026-05-03: Request intake completed and task id corrected from `PLAN-0025` to `PLAN-0026` because `PLAN-0025` already exists.
- 2026-05-03: Added `business_field` to report summaries and rendered it as a Q5 badge in the history list.
- 2026-05-03: Added a missing `## Outcome` section to completed `PLAN-0025` because the existing file blocked `exec_plan_guard`.
- 2026-05-03: `scripts/agent-task.sh verify` passed after the completed-plan format fix.
- 2026-05-03: `WEB_PORT=25181 API_PORT=28009 POSTGRES_PORT=55443 scripts/agent-task.sh docker-test` passed after default `POSTGRES_PORT=55432` was occupied.
- 2026-05-03: Playwright verified `#/reports` displays `Q5 교육` for a generated report.

## Outcome

Report history summaries now include `business_field`, derived from the saved Q5
idea intake answer. The history list renders that value as a Q5 badge on each
report card, and older blank values fall back to `분야 미정`.

## Definition of Done

- Report history API summaries include a Q5 business field value.
- Report history UI shows the Q5 value for each saved report, with a tolerable fallback for old data.
- Tests and docs cover the new list behavior.
- Required verification commands pass or blockers are documented.

## Follow-Up Cleanup

- Consider report-history filters by Q5 business field if users need larger history navigation.

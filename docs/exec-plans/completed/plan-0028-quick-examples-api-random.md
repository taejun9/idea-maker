# PLAN-0028 Quick Examples API Random

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/product-specs/index.md, docs/architecture/backend.md, docs/architecture/frontend.md
Roles: api-crafter, frontend-crafter, doc-keeper, quality-auditor

## Goal

Change quick examples from static frontend mock data to backend-generated examples.
The backend should return five examples per request, selected randomly and aligned
to supported business fields.

## Non-Goals

- Do not add external AI, Gemini, Gemma, or third-party calls for quick examples.
- Do not persist quick examples in PostgreSQL.
- Do not redesign the report creation page beyond the data source change.

## Assumptions

- "Generated each time" means deterministic-code random sampling inside the API
  request path, not model-generated text.
- Quick examples should remain fast and available without credentials.
- The frontend can show a backend failure fallback state instead of silently using
  the old local mock list.

## Constraints

- Routes stay thin; generation logic belongs in backend services with schemas at
  the API boundary.
- Frontend API calls stay under `apps/web/src/api/`.
- Existing supported Q5 business fields remain the source taxonomy, excluding
  `기타` for examples unless the existing product behavior requires it.
- Verification must run through the repository harness while this plan is active.

## Task Breakdown

- [x] Inspect current quick example frontend mock data and backend API patterns.
- [x] Add backend schema, service, route, and tests for five random quick examples.
- [x] Replace frontend local quick example sampling with the backend API client.
- [x] Update product docs to describe backend-generated random examples.
- [x] Run doctor, focused tests, full verify, and Docker checks required by changed areas.
- [x] Complete and move this plan after verification.

## Verification

- `scripts/agent-task.sh doctor`
- Focused backend tests for quick example API behavior.
- Focused frontend tests for quick example loading behavior if existing tests cover the page.
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test` because both API and web runtime behavior change.

Verification evidence:

- `scripts/agent-task.sh doctor` passed.
- Docker focused backend test passed: `19 passed`.
- Docker focused frontend test passed: `12 passed`.
- `scripts/agent-task.sh verify` passed.
- `POSTGRES_PORT=56432 scripts/agent-task.sh docker-test` passed: backend
  tests `30 passed`, Ruff passed, frontend build passed, frontend tests `12 passed`.
- Playwright browser check on `http://127.0.0.1:25028` confirmed five quick
  examples render and clicking an example fills the idea plus Q5 field.

## Outcome

Quick examples now come from `GET /api/quick-idea-examples`. The backend returns
five randomly generated examples aligned to supported business fields except
`기타`, and the frontend loads those examples on page entry instead of sampling
local mock example text.

## Rollback Strategy

Revert this plan's branch before merge, or revert the merge commit after merge.
The old frontend-only examples can be restored by removing the quick examples API
client call and route/service/schema additions.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Generate examples in backend without external AI calls. | Keeps refresh fast, credential-free, and aligned with current data-handling rules. |

## Progress

- 2026-05-04: Request intake completed and active plan created.
- 2026-05-04: Added quick examples API, backend generator, frontend API loading,
  tests, and product spec updates.
- 2026-05-04: Docker focused backend test passed (`19 passed`) and Docker
  focused frontend test passed (`12 passed`).
- 2026-05-04: `scripts/agent-task.sh verify` passed.
- 2026-05-04: `POSTGRES_PORT=56432 scripts/agent-task.sh docker-test` passed
  with backend tests (`30 passed`), Ruff, frontend build, and frontend tests
  (`12 passed`).
- 2026-05-04: Playwright browser check on `http://127.0.0.1:25028` confirmed
  five quick examples render and clicking an example fills the idea plus Q5 field.

## Definition of Done

- Backend returns exactly five quick examples per request.
- Returned examples are aligned to business fields and vary across requests.
- Frontend quick examples come from the backend instead of static local mock data.
- Product docs and plan reflect the new behavior.
- Required verification commands pass or any failure is documented with a concrete blocker.

## Follow-Up Cleanup

- None planned.

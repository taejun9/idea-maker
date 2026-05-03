# PLAN-0019 Frontend Fetch Error

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/architecture/frontend.md, docs/architecture/backend.md, docs/references/codex-git-workflow.md, docs/quality/quality-score.md
Roles: frontend-crafter, api-crafter, quality-auditor, platform-smith, doc-keeper

## Goal

Reproduce and fix the frontend `Failed to fetch` error seen from the Codex in-app browser when using the report flow.

## Non-Goals

- Do not redesign the UI.
- Do not change report-generation domain behavior unless the fetch failure proves a backend contract bug.
- Do not weaken tests, lint, or verification gates.

## Assumptions

- The previous frontend test missed the API-submitting path.
- The visible failure is likely caused by frontend API base URL configuration, runtime port mismatch, CORS, or API service availability.
- Docker Compose remains the local runtime source of truth.

## Constraints

- Work on `codex/plan-0019-frontend-fetch-error`, not directly on `main`.
- Keep code changes minimal and boundary-safe.
- Reproduce the failure before choosing a fix.

## Task Breakdown

- [x] Record the request-intake planning meeting.
- [x] Create the task worktree and branch.
- [x] Create this active execution plan.
- [x] Run `scripts/agent-task.sh doctor`.
- [x] Inspect current runtime and browser failure evidence.
- [x] Identify root cause and implement the smallest fix.
- [x] Add or update regression coverage.
- [x] Verify with Docker tests and Codex browser report flow.
- [x] Complete plan, merge, push, and clean up.

## Verification

- `scripts/agent-task.sh doctor`: passed.
- `scripts/agent-task.sh verify`: passed.
- `API_PORT=28000 WEB_PORT=25173 POSTGRES_PORT=25432 docker compose run --rm --no-deps web npm run --workspace apps/web test`: passed with 7 tests.
- `API_PORT=28000 WEB_PORT=25173 POSTGRES_PORT=25432 scripts/agent-task.sh docker-test`: passed with backend pytest 19 passed, Ruff passed, frontend build passed, and Vitest 7 passed.
- Codex browser verification exercised a real API-submitting path from `http://localhost:25173`, rendered `report-summary`, showed `report-error` count 0, and had browser console errors 0.
- `scripts/agent-task.sh ci`: passed after moving this plan to completed.

## Rollback Strategy

If the fix is wrong, revert this branch or the merge commit. Runtime-only diagnostic containers can be stopped with `docker compose down` using the same port environment used to start them.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Use PLAN-0019 for the fetch failure. | `PLAN-0018` verified only initial UI state and missed the API path. |

## Progress

- 2026-05-03: Request-intake planning meeting completed.
- 2026-05-03: Created `codex/plan-0019-frontend-fetch-error` worktree.
- 2026-05-03: Added active execution plan.
- 2026-05-03: `scripts/agent-task.sh doctor` passed.
- 2026-05-03: Current `http://localhost:25173` tab reproduced `Failed to fetch` when submitting because the prior `25173/28000` verification stack had been stopped.
- 2026-05-03: Existing `http://localhost:5173` served a different app (`Pencil Space`), so it was not valid evidence for this repository.
- 2026-05-03: Restarted this repository's Compose stack with `WEB_PORT=25173`, `API_PORT=28000`, and `POSTGRES_PORT=25432`.
- 2026-05-03: `GET http://localhost:28000/health` and `HEAD http://localhost:25173` both returned 200.
- 2026-05-03: Codex browser exercised the recommendation and report API path from `http://localhost:25173`; no `report-error` was present and browser console errors were `0`.
- 2026-05-03: API logs showed successful CORS preflight and POST requests for `/api/idea-recommendations` and `/api/idea-reports`.
- 2026-05-03: Existing frontend unit tests already cover recommendation fetch and selected recommendation report fetch with mocked `fetch`; no code change was needed because the root cause was the stopped temporary runtime.
- 2026-05-03: `API_PORT=28000 WEB_PORT=25173 POSTGRES_PORT=25432 scripts/agent-task.sh docker-test` initially failed in frontend Vitest because tests hardcoded `http://127.0.0.1:8000` while the runtime env correctly used `http://127.0.0.1:28000`.
- 2026-05-03: Updated frontend tests to derive expected API URLs from `VITE_API_BASE_URL`, preserving the default `8000` fallback while covering port override verification.
- 2026-05-03: `API_PORT=28000 WEB_PORT=25173 POSTGRES_PORT=25432 docker compose run --rm --no-deps web npm run --workspace apps/web test` passed with 7 tests.
- 2026-05-03: `API_PORT=28000 WEB_PORT=25173 POSTGRES_PORT=25432 scripts/agent-task.sh docker-test` passed: backend pytest 19 passed, Ruff passed, frontend build passed, and Vitest 7 passed.
- 2026-05-03: Codex browser reloaded `http://localhost:25173`, submitted a longer idea directly to the report API path, rendered `report-summary`, had `report-error` count 0, and browser console errors 0.
- 2026-05-03: `scripts/agent-task.sh verify` passed after the test update.
- 2026-05-03: Completed this plan after verification.
- 2026-05-03: `scripts/agent-task.sh ci` passed after moving this plan to completed.

## Outcome

The `Failed to fetch` error was reproduced on the stale `http://localhost:25173` tab because the temporary `25173/28000` verification stack from the previous task had been stopped. Restarting this repository's stack on the same ports made both recommendation and report API paths succeed. Frontend tests now respect `VITE_API_BASE_URL`, so port override verification no longer fails due to hardcoded `8000` expectations.

## Definition of Done

- The `Failed to fetch` path is reproduced or convincingly explained.
- A regression test covers the root cause when code changes are made.
- Docker verification passes.
- Codex browser confirms the report flow no longer shows `Failed to fetch`.

## Follow-Up Cleanup

- None planned unless diagnosis reveals a broader runtime configuration gap.

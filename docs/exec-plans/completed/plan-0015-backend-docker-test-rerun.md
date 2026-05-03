# PLAN-0015 Backend Docker Test Rerun

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/architecture/backend.md, docs/references/codex-git-workflow.md
Roles: platform-smith, api-crafter, quality-auditor

## Goal

Rerun backend tests inside the Docker Compose API environment and capture any failure evidence related to the reported backend 400 error.

## Non-Goals

- Do not change backend application behavior unless the test rerun exposes a small, clearly required test harness issue.
- Do not broaden scope to frontend build or UI verification unless the backend test command requires it.
- Do not merge or push changes for this diagnostic-only test run unless code or documentation changes become necessary and verification passes.

## Assumptions

- The user's reported 400 error happened while running the project in Docker.
- Backend test rerun means API-container pytest first, followed by ruff if pytest passes or if lint evidence is needed.
- Docker Compose is available locally.

## Constraints

- Local runtime verification must use Docker Compose.
- Keep changes limited to the execution plan unless a concrete backend/test failure requires a fix.
- Preserve existing user changes and do not commit directly on main.

## Task Breakdown

- [x] Create the task worktree and branch.
- [x] Record request intake and create the active plan.
- [x] Run `scripts/agent-task.sh doctor`.
- [x] Run backend pytest in the API Docker container.
- [x] Inspect failure output if tests fail.
- [x] Report verification result, failure evidence, and next action.

## Verification

```bash
scripts/agent-task.sh doctor
docker compose run --rm api python -m pytest services/api/tests tests
docker compose run --rm api python -m ruff check services/api tests tools
```

## Rollback Strategy

If no code changes are needed, remove the diagnostic worktree after reporting. If a fix is required later, keep the worktree and continue under this plan or create a follow-up plan if scope expands.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Use PLAN-0015 for backend Docker test rerun. | Existing completed plans reached PLAN-0014 and no active plan existed for this request. |
| 2026-05-03 | Run API-container pytest before any code edits. | The request is to rerun backend tests and diagnose the reported 400 error, not to implement a fix yet. |

## Progress

- 2026-05-03: Created `codex/plan-0015-backend-docker-test-rerun` worktree.
- 2026-05-03: Added active execution plan.
- 2026-05-03: First Docker pytest run failed because this plan used an unsupported `Related docs` metadata format; API tests passed before the harness guard failure.
- 2026-05-03: `scripts/agent-task.sh doctor` passed.
- 2026-05-03: `docker compose run --rm api python -m pytest services/api/tests tests` passed with 14 tests.
- 2026-05-03: `docker compose run --rm api python -m ruff check services/api tests tools` passed.
- 2026-05-03: `scripts/agent-task.sh verify` passed; local backend/frontend checks skipped because local dependencies are not installed.

## Outcome

Backend Docker pytest and Ruff both passed in the API container. The reported runtime 400 error was not reproduced by the existing backend test suite.

## Definition of Done

- Doctor check has been run.
- Backend Docker pytest result is reported.
- Ruff result is reported when reached.
- Any failure is summarized with the failing test, error, and likely next investigation target.

## Follow-Up Cleanup

- Investigate the specific Docker request path, payload, and API logs that produced the runtime 400 error if it still occurs outside the test suite.

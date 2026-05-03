# PLAN-0007 Project Hygiene Improvements

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: `docs/architecture/frontend.md`, `docs/references/codex-git-workflow.md`
Branch: `codex/plan-0007-project-hygiene-improvements`
Worktree: `.worktrees/plan-0007-project-hygiene-improvements`
Roles: `platform-smith`, `frontend-crafter`, `quality-auditor`, `doc-keeper`

## Goal

Find and fix a small, concrete project hygiene issue that reduces future Codex churn.

## Non-Goals

- Redesigning the frontend.
- Changing runtime behavior.
- Broad dependency upgrades.

## Assumptions

- `apps/web/dist/` is a generated Vite build output and should not be tracked.
- The existing `.gitignore` already declares `apps/web/dist/` ignored.
- Removing tracked build output should not affect Docker-based build/test flows.

## Constraints

- Keep the change focused.
- Preserve source files and tests.
- Verify with the standard scripts after the cleanup.

## Task Breakdown

- [x] Confirm tracked generated files.
- [x] Remove tracked generated frontend build artifacts.
- [x] Document the hygiene decision.
- [x] Run `scripts/agent-task.sh verify` and `scripts/agent-task.sh docker-test`.

## Verification

- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- `git ls-files apps/web/dist` returns no tracked files.

## Rollback Strategy

- Restore the removed tracked build outputs from the parent commit if a deployment
  dependency on committed `dist` is discovered.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Remove tracked `apps/web/dist` files | They are ignored generated output and were dirtied by routine Docker frontend builds. |

## Progress

Removed tracked Vite build artifacts under an ignored path and documented the rule in
the frontend architecture notes. Verification passed.

## Outcome

- Removed tracked `apps/web/dist` build artifacts.
- Confirmed `git ls-files apps/web/dist` returns no tracked files.
- Documented that Vite build output is generated and should not be committed.

## Verification Evidence

- `scripts/agent-task.sh verify`: passed; backend/frontend local checks skipped as
  expected because local dependencies are not installed.
- `scripts/agent-task.sh docker-test`: first run was blocked by the previous compose
  project holding `POSTGRES_PORT=55432`; after stopping stale compose containers, rerun
  passed with backend pytest 11 tests, Ruff, web build, and web Vitest 2 tests.

## Definition of Done

- Generated frontend build output is no longer tracked.
- Docker frontend build/test still passes.
- The decision is recorded in repository docs or this completed plan.

## Follow-Up Cleanup

- Review whether other ignored paths have tracked files.

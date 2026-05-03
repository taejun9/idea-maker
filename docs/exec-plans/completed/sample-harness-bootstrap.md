# PLAN-0000 Harness Bootstrap

Status: completed
Owner: Codex
Created: 2026-05-03
Completed: 2026-05-03
Related docs: `docs/HARNESS_SYSTEM.md`, `AGENTS.md`

## Goal

Bootstrap a Codex-first harness system for this repository.

## Outcome

Created the initial source-of-record docs, architecture rules, verification scripts, CI template, observability notes, eval scenarios, and starter frontend/backend skeletons.

## Verification

- Structure guard available through `scripts/agent-task.sh doctor`.
- Full local verification available through `scripts/agent-task.sh verify`.

## Decisions

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Codex-only workflow | User clarified this project will run only in Codex. |
| 2026-05-03 | Keep `AGENTS.md` short | Prevent instruction drift and route to docs. |
| 2026-05-03 | Team id is `ant-legion`, Korean name is 개미군단 | User selected team name and naming convention. |
| 2026-05-03 | Local runtime is Docker Compose with PostgreSQL 18 and Node 22 | User selected runtime baseline. |

## Follow-Up Cleanup

- Tighten CI gates after dependencies are installed.
- Add real app implementation under `PLAN-0001`.
- Move future implementation work into worktree branches before committing.

# PLAN-0010 Planning Meeting Gate

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: `AGENTS.md`, `RTK.md`, `docs/exec-plans/README.md`, `docs/references/codex-git-workflow.md`, `docs/references/codex-prompt-pack.md`, `docs/HARNESS_SYSTEM.md`, `docs/quality/quality-score.md`
Roles: `doc-keeper`, `reliability-warden`

## Goal

Change the Codex workflow so a task request starts with a short planning meeting that produces or updates the active execution plan before any task work begins.

## Non-Goals

- Do not change product runtime behavior.
- Do not relax the active-plan verification gate.
- Do not change Docker, frontend, backend, or database behavior.

## Assumptions

- The user wants Codex to stop creating plans at handoff time and instead create plans immediately after request intake.
- Lightweight tasks may use a lightweight meeting record and plan, but the plan must still exist before implementation, documentation, test, or tooling edits.

## Constraints

- Keep the active-plan gate mechanically intact for task branches.
- Keep `main` free of direct commits.
- Update all high-visibility Codex workflow references so future sessions receive the same instruction.

## Task Breakdown

- [x] Open a worktree branch for the workflow change.
- [x] Create this active execution plan before editing workflow docs.
- [x] Replace "create or request a plan" language with a request-intake planning meeting requirement.
- [x] Update prompt pack and harness summary language.
- [x] Run required verification while the plan is active.
- [x] Complete and move this plan to `docs/exec-plans/completed/`.

## Verification

- `scripts/agent-task.sh doctor`: passed
- `scripts/agent-task.sh start-report plan-0010-planning-meeting-gate "Require request-intake planning meetings"`: passed
- `scripts/agent-task.sh verify`: passed while this plan was active
- `scripts/agent-task.sh ci`: passed after move to completed

## Rollback Strategy

Revert the documentation-only workflow changes from this branch before merge, or revert the merge commit if the updated plan intake policy causes future harness confusion.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Require a request-intake planning meeting before active plan creation | User reported the previous "no plan, no work" rule caused plans to appear at the end instead of before work. |

## Progress

- 2026-05-03: Created worktree branch and active execution plan.
- 2026-05-03: Updated Codex workflow docs and harness script messages to require request-intake planning meetings before active plan creation.
- 2026-05-03: `scripts/agent-task.sh verify` passed while this plan was active.
- 2026-05-03: Moved this plan to completed and `scripts/agent-task.sh ci` passed with `active=0, completed=9`.

## Outcome

Codex workflow docs now require a request-intake planning meeting before an active execution plan is created or updated. The harness start-report command now prints a planning-meeting template, and the active-plan failure message points Codex to run that meeting before task work. Docs also explicitly forbid backfilling a missing plan at finish-report time.

## Definition of Done

- Workflow docs say Codex must hold a short planning meeting after each task request.
- The planning meeting output includes goal, scope, assumptions, roles, changed areas, verification, and whether a new or existing plan will be used.
- Docs clearly forbid creating the execution plan only at completion or handoff.
- Required verification passes.

## Follow-Up Cleanup

- None planned.

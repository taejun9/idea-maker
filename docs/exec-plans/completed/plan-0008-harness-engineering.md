# PLAN-0008 Harness Engineering Improvements

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Completed: 2026-05-03
Related docs: `AGENTS.md`, `docs/HARNESS_SYSTEM.md`, `docs/references/codex-extensions.md`, `docs/references/codex-git-workflow.md`, `scripts/agent-task.sh`
Roles: `platform-smith`, `doc-keeper`, `quality-auditor`

## Goal

Review the repository's Codex harness engineering structure, including agent entry rules, skills, MCP/plugin guidance, execution-plan gates, and verification scripts. Implement a small set of improvements that makes future Codex runs more repeatable and easier to audit.

## Non-Goals

- Do not change product behavior.
- Do not add deployment infrastructure.
- Do not install new skills or MCP servers unless a repeated workflow already exists.
- Do not weaken existing lint, docs, or architecture gates.

## Assumptions

- Harness decisions must be represented in repository docs or scripts, not only in operator memory.
- The current task may reveal stale references or missing directories because active plans are mandatory but no active directory exists in the starting tree.
- Improvements should favor lightweight mechanical checks over longer prose when feasible.

## Constraints

- Work must happen on `codex/plan-0008-harness-engineering`, not directly on `main`.
- Docker Compose remains the only supported local runtime for project services.
- Final verification must include `scripts/agent-task.sh verify`.
- Any deferred improvement must be recorded in `docs/exec-plans/tech-debt-tracker.md`.

## Task Breakdown

- [x] Create active execution plan and worktree branch.
- [x] Run initial harness diagnostics.
- [x] Inspect Codex-facing docs, extension guidance, Git workflow, and agent task script.
- [x] Identify and implement the highest-value harness improvements.
- [x] Update quality/debt docs if gates, risks, or deferred work change.
- [x] Run required verification.
- [x] Complete and move this plan to `docs/exec-plans/completed/`.

## Verification

- `scripts/agent-task.sh doctor`
- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh verify`

## Rollback Strategy

Revert this plan's documentation and script changes from the feature branch before merge. Since this task should not touch runtime product code, rollback should not require database or service state changes.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Use `PLAN-0008` for harness improvements | The highest completed plan is `PLAN-0007`. |
| 2026-05-03 | Split `verify` and `ci` commands | Task branches need the active-plan gate, but clean `main` and CI should pass after plans move to `completed/`. |
| 2026-05-03 | Add execution-plan guard | Plan section rules were documented but not mechanically enforced. |

## Progress

- 2026-05-03: Started from clean `main`, created worktree branch, and opened this active plan.
- 2026-05-03: Added RTK routing file, persistent active-plan directory, execution-plan guard, CI-safe verification command, and refreshed skill/plugin guidance.
- 2026-05-03: Verification passed, including Docker backend/frontend tests.

## Outcome

- Added `RTK.md` so `@RTK.md` session includes resolve to a tracked source-of-record router.
- Kept `docs/exec-plans/active/` present with `.gitkeep`.
- Added `tools/exec_plan_guard.py` and wired it into `scripts/agent-task.sh verify` and `ci`.
- Split task-branch `verify` from main/CI-safe `ci` so clean `main` can pass after active plans move to `completed/`.
- Refreshed skill/plugin guidance and clarified that role ids are plan/report ownership labels, not implicit sub-agent delegation.
- Updated quality score and resolved the worktree migration debt item.

## Verification Evidence

- `scripts/agent-task.sh active-plan`: passed.
- `scripts/agent-task.sh doctor`: passed.
- `scripts/agent-task.sh verify`: passed; local backend/frontend dependency checks skipped as expected.
- `scripts/agent-task.sh ci`: passed before and after moving this plan; post-move guard reported `active=0, completed=7`.
- `scripts/agent-task.sh docker-test`: passed; backend pytest 13 tests, Ruff, web build, and web Vitest 2 tests.
- `scripts/agent-task.sh docker-down`: cleaned up Compose verification resources.

## Definition of Done

- Harness docs and/or scripts contain concrete improvements discovered during review.
- Verification commands pass or any failures are explained with actionable follow-up.
- Plan is marked completed and moved to `docs/exec-plans/completed/`.
- Branch is ready for `main` merge and push after verification succeeds.

## Follow-Up Cleanup

- No new deferred work from this plan.

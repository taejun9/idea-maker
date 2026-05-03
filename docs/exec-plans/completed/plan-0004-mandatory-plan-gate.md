# PLAN-0004 Mandatory Plan Gate

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Completed: 2026-05-03
Related docs: `AGENTS.md`, `docs/exec-plans/README.md`, `docs/references/codex-git-workflow.md`, `docs/references/codex-prompt-pack.md`
Branch: `codex/plan-0004-mandatory-plan-gate`
Worktree: `.worktrees/plan-0004-mandatory-plan-gate`

## Goal

Require an active execution plan before any Codex task work starts.

## Non-Goals

- Changing product behavior.
- Changing frontend or backend runtime behavior.
- Creating a full task management system.

## Assumptions

- Worktree setup and start reporting may happen before implementation edits.
- The active plan gate is satisfied only by at least one `docs/exec-plans/active/plan-*.md` file.
- Each task should create or update a relevant plan before changing task files.

## Constraints

- Keep the rule easy to check from shell scripts.
- Preserve completed-plan movement rules.
- Do not weaken existing verification gates.

## Task Breakdown

- [x] Add an active-plan guard command to `scripts/agent-task.sh`.
- [x] Run the guard before `doctor` and `verify`.
- [x] Document the mandatory active-plan rule in `AGENTS.md`.
- [x] Update execution-plan and Git workflow references.
- [x] Update commit message format to `<action>(plan-NNNN): <task>`.
- [x] Complete this plan and move it to `completed/`.
- [x] Run `scripts/agent-task.sh verify`.

## Verification

- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh verify`

## Rollback Strategy

- Revert the guard command and documentation changes.
- Move this plan back to active if the policy is rolled back before completion.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Require active plans for all work | User explicitly set this as a universal Codex workflow rule. |

## Progress

Completed mandatory active-plan policy, script guard, and commit-format update.

## Outcome

- `scripts/agent-task.sh active-plan` checks for at least one active `plan-NNNN-*.md`.
- `doctor` and `verify` now fail when the active-plan gate is not satisfied.
- Workflow docs require every task to create or update an active plan before task work.
- Commit messages now use `<action>(plan-NNNN): <task>`.

## Verification Evidence

- `scripts/agent-task.sh active-plan`
- `bash -n scripts/agent-task.sh`
- `scripts/agent-task.sh verify`

## Definition of Done

- The repository documents that all work requires an active plan first.
- Verification fails when no `docs/exec-plans/active/plan-*.md` exists.
- This completed policy-change plan is moved to `docs/exec-plans/completed/`.

## Follow-Up Cleanup

- Consider adding a dedicated lint test for plan naming and placement.

# Execution Plans

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

Execution plans make complex Codex work repeatable. A plan records the goal, constraints, steps, verification, rollback, decisions, and completion status.

## Mandatory Plan Gate

Every Codex task requires an active execution plan before task work starts. The plan must come from a short request-intake planning meeting, not from a retroactive handoff cleanup.

If `docs/exec-plans/active/` has no `plan-NNNN-<task-slug>.md` file, Codex must stop before implementation, documentation, test, or tooling changes and run the planning meeting first. The meeting output can be brief, but it must record goal, scope, non-goals, assumptions or open questions, role ids, expected changed areas, verification, and the selected plan id. If that information is not clear enough, Codex asks the user the blocking questions and waits.

Small tasks still need a lightweight plan. Large tasks need a fuller plan with explicit constraints, verification, rollback, and definition of done.

Run `scripts/agent-task.sh active-plan` before task work to check the gate.
The `active/` directory is tracked with `.gitkeep`; only `plan-NNNN-*.md` files
count as active plans.

`scripts/agent-task.sh verify` is for task branches and enforces the active-plan
gate. `scripts/agent-task.sh ci` is for CI and clean `main`, where completed
plans have normally moved out of `active/`.

## Plan Template

Plan filenames must use `plan-NNNN-<task-slug>.md`.

- `NNNN` must match the plan id in the document title, for example `PLAN-0001`.
- `<task-slug>` must be lowercase kebab-case and describe the work.
- Active plans live in `docs/exec-plans/active/`.
- Completed plans live in `docs/exec-plans/completed/` as soon as their status changes to `completed`.

```markdown
# [PLAN_ID] [Title]

Status: active
Owner: Codex
Created: YYYY-MM-DD
Last updated: YYYY-MM-DD
Related docs:
Roles:

## Goal

## Non-Goals

## Assumptions

## Constraints

## Task Breakdown

- [ ] Step 1
- [ ] Step 2

## Verification

## Rollback Strategy

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |

## Progress

## Definition of Done

## Follow-Up Cleanup
```

## Completion Rules

When complete:

1. Run `scripts/agent-task.sh verify` while the plan is still active.
2. Update status to `completed`.
3. Add outcome and verification evidence.
4. Immediately move the file from `active/` to `completed/`.
5. Add deferred work to `tech-debt-tracker.md`.
6. Update `docs/quality/quality-score.md` if gates or risk changed.
7. Run `scripts/agent-task.sh ci` after the move when a no-active-plan check is needed.

## Mechanical Checks

`tools/exec_plan_guard.py` verifies:

- `docs/exec-plans/active/.gitkeep` exists.
- active plan files use `plan-NNNN-<task>.md`, `Status: active`, `Roles:`, verification, rollback, and decision log sections.
- completed plan files use `Status: completed` and keep outcome, verification, and follow-up cleanup sections.

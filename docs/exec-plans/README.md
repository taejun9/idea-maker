# Execution Plans

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

Execution plans make complex Codex work repeatable. A plan records the goal, constraints, steps, verification, rollback, decisions, and completion status.

## Mandatory Plan Gate

Every Codex task requires an active execution plan before task work starts. If `docs/exec-plans/active/` has no `plan-NNNN-<task-slug>.md` file, Codex must stop and create or request an active plan before making implementation, documentation, test, or tooling changes.

Small tasks still need a lightweight plan. Large tasks need a fuller plan with explicit constraints, verification, rollback, and definition of done.

Run `scripts/agent-task.sh active-plan` before task work to check the gate.

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

1. Update status to `completed`.
2. Add outcome and verification evidence.
3. Immediately move the file from `active/` to `completed/`.
4. Add deferred work to `tech-debt-tracker.md`.
5. Update `docs/quality/quality-score.md` if gates or risk changed.

# Execution Plans

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

Execution plans make complex Codex work repeatable. A plan records the goal, constraints, steps, verification, rollback, decisions, and completion status.

## When To Create A Plan

Create an active plan for:

- changes touching frontend and backend together
- architecture or CI changes
- external source integration
- database schema changes
- reliability/security behavior changes
- refactors spanning more than one module

Small typo fixes, focused tests, and single-file docs edits do not need a plan.

## Plan Template

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
3. Move file from `active/` to `completed/`.
4. Add deferred work to `tech-debt-tracker.md`.
5. Update `docs/quality/quality-score.md` if gates or risk changed.

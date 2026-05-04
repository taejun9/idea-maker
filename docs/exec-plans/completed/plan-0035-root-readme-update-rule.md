# PLAN-0035 Root README Update Rule

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: AGENTS.md, README.md, docs/exec-plans/README.md
Roles: doc-keeper, system-architect, quality-auditor

## Goal

Make root `README.md` updates mandatory whenever product functionality is added
or changed, and update the current root README so it reflects the implemented
product flow more accurately.

## Non-Goals

- Do not change application runtime behavior.
- Do not add new product features.
- Do not change verification gates beyond the documentation rule requested.

## Assumptions

- The user's request is a repository operating-rule change plus an immediate
  documentation update.
- `README.md` should remain a concise Korean project overview, not duplicate the
  full product spec.
- `AGENTS.md` is the right Codex-facing enforcement point for the rule.

## Constraints

- Keep `AGENTS.md` short and map-like.
- Use a worktree branch and do not commit directly on `main`.
- Complete the plan before final handoff and move it to `completed/`.

## Task Breakdown

- [x] Add a README update requirement to Codex operating rules.
- [x] Update root `README.md` for the current feature set and explicit rule.
- [x] Run documentation and structure verification.
- [x] Complete this execution plan and move it to `completed/`.

## Verification

- `scripts/agent-task.sh doctor`
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh ci` after completing the plan

## Rollback Strategy

Revert the documentation-only commit to restore the previous README and Codex
rules.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Add the rule to `AGENTS.md` and mirror it in `README.md`. | Codex reads `AGENTS.md` first, while README communicates the rule to repository readers. |

## Progress

- Request-intake meeting completed.
- Worktree branch created: `codex/plan-0035-root-readme-update-rule`.
- Active execution plan created.
- Added README-update requirement to `AGENTS.md`.
- Updated root `README.md` product flow and documentation rule.
- `scripts/agent-task.sh verify` passed.

## Outcome

Root `README.md` updates are now mandatory for every feature addition or feature
change, and the README itself now reflects the current recommendation, Q1-Q5,
research adapter, report persistence, and document operation behavior.

## Definition of Done

- `AGENTS.md` explicitly requires root README updates for feature additions or
  changes.
- Root `README.md` is updated in this change.
- Verification passes.
- Completed plan is moved to `docs/exec-plans/completed/`.

## Follow-Up Cleanup

- None planned.

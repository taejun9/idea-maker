# PLAN-0011 Agent Report Format

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: AGENTS.md, RTK.md, docs/references/codex-git-workflow.md, docs/team/roster.md, docs/operations/reliability.md, docs/quality/quality-score.md
Roles: doc-keeper, platform-smith, quality-auditor

## Goal

Require agents to report task starts and task completion using a worker-name prefix:

- `<작업자명>: <작업내용>` when starting work
- `<작업자명>: <보고내용>` when completing work

## Non-Goals

- Do not change application runtime behavior.
- Do not add a new agent orchestration system.
- Do not weaken existing plan, worktree, verification, merge, or push rules.

## Assumptions

- "작업자명" maps to the active role name or explicit worker name visible in the task.
- The requested format applies to start and finish reports, including delegated agent reports when sub-agents are explicitly used.
- Existing required report details remain required; the new rule only constrains the report line prefix and shape.

## Constraints

- Keep source-of-record docs concise and avoid duplicating long process text.
- Preserve the mandatory active-plan gate.
- Keep `AGENTS.md` under the architecture rule limit.

## Task Breakdown

- [x] Confirm relevant reporting docs and current workflow.
- [x] Update runtime and project instructions to require the worker-name report format.
- [x] Update workflow/team/quality docs if the report gate changes.
- [x] Add harness test coverage for worker-prefixed report templates.
- [x] Run required verification.
- [x] Complete and move the execution plan.

## Verification

- `scripts/agent-task.sh doctor`: passed.
- `scripts/agent-task.sh verify`: passed. Local backend/frontend checks were skipped by the harness because local dev dependencies are not installed.
- `scripts/agent-task.sh docker-test`: passed. Backend pytest reported 14 passed, Ruff reported all checks passed, Vue build passed, and Vitest reported 2 passed.
- `python3 -m pytest tests/test_harness.py`: not used as final evidence because local Python lacks `pytest`; Docker test covered the same harness test path.
- `scripts/agent-task.sh ci`: passed after plan completion with `active=0, completed=10`. Local backend/frontend checks were skipped by the harness because local dev dependencies are not installed; Docker test passed those paths.

Docker tests were run because the change adds harness test coverage and local Python does not have `pytest` installed.

## Rollback Strategy

Revert the documentation commit that introduces the report format requirement.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Use the active role or explicit worker name as `<작업자명>`. | The team roster already defines role names and ids for reports. |
| 2026-05-03 | Keep existing report content requirements and add only the required prefix shape. | This preserves the current start/finish report evidence while satisfying the requested format. |

## Progress

- 2026-05-03: Request-intake planning meeting completed and plan created.
- 2026-05-03: Updated report format docs, script templates, and harness test coverage.
- 2026-05-03: Required task-branch verification and Docker tests passed.
- 2026-05-03: Moved this plan to completed and `scripts/agent-task.sh ci` passed.

## Outcome

Worker-prefixed task start and finish reporting is now documented in runtime, workflow, team, reliability, harness, and prompt-pack references. `scripts/agent-task.sh start-report` and `finish-report` now print the required first-line format, and `tests/test_harness.py` verifies those templates.

## Definition of Done

- Reporting format requirement appears in the runtime/project workflow docs.
- Quality docs reflect the workflow-gate clarification if applicable.
- Required verification passes.
- Plan is completed and moved to `docs/exec-plans/completed/`.

## Follow-Up Cleanup

- None planned.

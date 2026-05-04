# PLAN-0043 Full Test Run

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/quality/quality-score.md, docs/exec-plans/README.md, docs/references/codex-git-workflow.md
Roles: quality-auditor, platform-smith

## Goal

Run the repository's full verification suite from a task branch and report the
current pass/fail status.

## Non-Goals

- Do not change application code.
- Do not weaken tests, lint rules, docs checks, or architecture guards.
- Do not debug or fix failures beyond collecting enough output to identify the
  failing area.

## Assumptions

- "Full test" means the Codex harness verification plus Docker-based backend and
  frontend checks.
- The local Docker runtime may already be running in the root worktree; this
  task can use an isolated worktree Compose project for test containers.
- Local host Python and Node dependencies may be incomplete, so Docker results
  are the authoritative backend/frontend test signal.

## Constraints

- Work runs on `codex/plan-0043-full-test-run`, not directly on `main`.
- Local PostgreSQL remains Docker Compose PostgreSQL 18.
- Verification output must distinguish skipped local dependency checks from
  Docker test results.

## Task Breakdown

- [x] Run active-plan and doctor checks.
- [x] Run `scripts/agent-task.sh verify` while this plan is active.
- [x] Run `scripts/agent-task.sh docker-test`.
- [x] Complete this plan with evidence and run `scripts/agent-task.sh ci`.
- [x] Report pass/fail results to the user.

## Verification

- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh doctor`
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- `scripts/agent-task.sh ci`

## Rollback Strategy

- No code rollback is needed for a test-only task.
- Remove the task worktree and branch after recording the test result.
- If Docker test containers or volumes are created for the task worktree, remove
  that Compose project after the run.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Use an isolated task worktree for full test execution. | Repository rules require active plans and avoid direct task work on `main`. |

## Progress

- Request-intake meeting completed.
- Plan id selected: `PLAN-0043`.
- Created branch/worktree `codex/plan-0043-full-test-run`.
- `scripts/agent-task.sh active-plan` passed.
- `scripts/agent-task.sh doctor` passed.
- `scripts/agent-task.sh verify` passed while this plan was active. Backend and
  frontend host-local dependency checks were skipped because host dependencies
  are incomplete; Docker checks below are authoritative.
- `scripts/agent-task.sh docker-test` passed:
  - backend pytest: 55 passed
  - Ruff: passed
  - frontend build: passed
  - frontend Vitest: 13 passed
  - npm audit reported 5 moderate vulnerabilities during `npm install`; this did
    not fail the configured test gate.

## Outcome

The full configured repository verification suite passed. The only warning was
the existing npm audit output for 5 moderate vulnerabilities during the Docker
frontend install step.

## Definition of Done

- Harness verification result is recorded.
- Docker backend/frontend test result is recorded.
- Any skipped checks or warnings are explicitly called out.

## Follow-Up Cleanup

- If tests fail, create a follow-up fix plan instead of editing code in this
  test-only plan.

# Runtime Task Kernel

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Purpose

`RTK.md` is the thin runtime contract for Codex sessions that include `@RTK.md`
before the project-specific `AGENTS.md` body. It must stay short and route to
source-of-record docs instead of duplicating them.

## Source Of Record

- Start with `AGENTS.md`.
- Use `docs/HARNESS_SYSTEM.md` for the full harness model.
- Use `docs/team/roster.md` for role ids and ownership.
- Use `docs/references/codex-extensions.md` for skills, MCP, and plugin policy.
- Use `docs/references/codex-git-workflow.md` for worktree, merge, push, and cleanup.
- Use `docs/exec-plans/README.md` for execution plan rules.

## Runtime Rules

- Every task report includes goal, scope, branch/worktree, active role ids, expected changed areas, and verification plan.
- Every task starts with a short request-intake planning meeting that records goal, scope, non-goals, assumptions or open questions, role ids, expected changed areas, verification, and the selected plan id.
- Every task uses an active plan created or updated from that meeting before implementation, documentation, test, or tooling changes.
- If the plan is missing or ambiguous, ask the user the blocking planning questions and stop; do not backfill a plan at finish-report time.
- `scripts/agent-task.sh verify` is the task-branch verification command and enforces the active-plan gate.
- `scripts/agent-task.sh ci` is the main/CI-safe verification command and does not require an active task plan.
- Completed plans move to `docs/exec-plans/completed/`; `docs/exec-plans/active/.gitkeep` keeps the active plan directory present in fresh checkouts.

## Skills And Agents

- Use a skill only when the user names it or the task clearly matches its trigger.
- Read the skill's `SKILL.md` before applying it.
- Do not install new skills, MCP servers, or plugins unless the workflow is repeated and the installation is recorded in `docs/references/codex-extensions.md`.
- Treat role ids in `docs/team/roster.md` as ownership labels for plans and reports, not as permission to spawn sub-agents.
- Spawn sub-agents only when the user explicitly asks for delegated or parallel agent work.

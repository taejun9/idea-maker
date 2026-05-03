# Codex Prompt Pack

Last reviewed: 2026-05-03
Owner: Platform / Codex

## System Prompt

You are Codex working in this repository for team 개미군단 (`ant-legion`). Follow `AGENTS.md` first. Treat repository docs as the source of record. Report at task start and task finish. Do not commit directly on `main`; use a worktree branch. For non-trivial changes, create or update an execution plan under `docs/exec-plans/active/`. Implement the smallest coherent change, update docs in the same PR, and run `scripts/agent-task.sh verify` plus Docker checks when runtime behavior changed.

## Task Start Prompt

Read `AGENTS.md`, `docs/architecture/README.md`, and the docs relevant to this task. Send a start report with goal, scope, branch/worktree, and verification plan. State assumptions, identify whether an exec plan is needed, then implement. Do not stop at a proposal unless blocked.

## Bug Fix Prompt

Reproduce the bug with a failing Docker test or local harness command. Identify the responsible layer using `docs/architecture/README.md`. Patch the smallest layer, add a regression test, update docs if behavior changed, run `scripts/agent-task.sh verify`, then send a finish report.

## New Feature Prompt

Create an active exec plan. Update `docs/product-specs/index.md` if the user-facing behavior changes. Implement backend schema/service/API and frontend feature slices within existing boundaries. Add tests and UI verification notes. Complete or update the exec plan before handoff.

## Documentation Gardening Prompt

Run docs freshness and link checks. Update stale `Last reviewed:` dates only after reading the file. Remove duplicates, update indexes, move completed plans, and record deferred work in `docs/exec-plans/tech-debt-tracker.md`.

## Architecture Violation Fix Prompt

Run `tools/architecture_scan.py`. For each violation, move logic to the correct layer without changing behavior. Add or preserve tests. If the rule is wrong, update `docs/architecture/README.md`, `lint-rules/architecture_rules.yml`, and `docs/quality/quality-score.md` with the rationale.

## PR Review Prompt

Review as a code reviewer. Findings first, ordered by severity, with file and line references. Prioritize bugs, regressions, missing tests, security risks, and architecture drift. Keep summaries brief.

## Drift Cleanup Prompt

Inspect active plans, completed plans, tech debt, quality score, and stale docs. Propose or implement the smallest cleanup PRs. Promote repeated manual preferences into docs, scripts, or lint rules.

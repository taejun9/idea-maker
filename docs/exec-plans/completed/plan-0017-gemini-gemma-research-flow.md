# PLAN-0017 Gemini Gemma Research Flow

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/product-specs/index.md, docs/architecture/backend.md, docs/architecture/frontend.md, docs/operations/security.md, docs/operations/reliability.md
Roles: system-architect, api-crafter, frontend-crafter, reliability-warden, security-gatekeeper, quality-auditor

## Goal

Extend the recommendation flow so a word or short sentence first produces related item recommendations, then the selected item can run Gemini CLI-backed source search and local Gemma4-backed organization before generating the report.

## Non-Goals

- Do not install or authenticate Gemini CLI automatically.
- Do not download, start, or tune a local Gemma model automatically.
- Do not require external tools for deterministic tests or CI.
- Do not persist research history in PostgreSQL.
- Do not send hidden secrets, local files, or backend internals to external search prompts.

## Assumptions

- A short idea means a trimmed input with at most 5 whitespace-delimited tokens or at most 40 characters.
- Gemini CLI can be called in headless mode when installed and authenticated.
- Local Gemma4 is exposed by llama.cpp at `http://localhost:8089` with OpenAI-compatible `/v1/chat/completions`.
- If either external adapter is unavailable, the backend returns a structured fallback report using deterministic collectors.
- Existing multi-word longer idea input can still generate reports directly.

## Constraints

- `services/api` owns integration, orchestration, validation, and fallback behavior.
- `apps/web` owns UI and client state only.
- Routes stay thin and do not embed subprocess, HTTP, or business logic.
- External search output is untrusted input and must be normalized before report use.
- All new integration behavior must be testable without Gemini CLI or a live Gemma server.

## Task Breakdown

- [x] Create task branch/worktree and active plan.
- [x] Run `scripts/agent-task.sh doctor`.
- [x] Inspect current recommendation/report flow and local external tool availability.
- [x] Add backend schemas for research status and organized research evidence.
- [x] Add Gemini CLI search adapter with timeout, JSON parsing, and deterministic fallback.
- [x] Add local Gemma organizer adapter with timeout, schema validation, and deterministic fallback.
- [x] Update report orchestration so selected recommendations can request research before report generation.
- [x] Update frontend to route word/short-sentence input through recommendation and research flow.
- [x] Update tests and documentation.
- [x] Run Docker verification and browser smoke check.
- [x] Complete plan, merge, push, and clean worktree.

## Verification

```bash
scripts/agent-task.sh doctor
docker compose run --rm api python -m pytest services/api/tests tests
docker compose run --rm api python -m ruff check services/api tests tools
docker compose run --rm --no-deps web npm install
docker compose run --rm --no-deps web npm run --workspace apps/web build
docker compose run --rm --no-deps web npm run --workspace apps/web test
scripts/agent-task.sh verify
```

When available locally:

```bash
gemini --version
curl http://localhost:8089/health
curl http://localhost:8089/v1/chat/completions
```

## Rollback Strategy

Revert this branch to return to deterministic recommendation and report generation. Since no persistence is added, rollback is limited to code, tests, and documentation.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Use `PLAN-0017` for Gemini CLI search and Gemma organization. | `PLAN-0016` completed the first recommendation flow and this is a separate integration step. |
| 2026-05-03 | Keep external adapters optional and fallback-safe. | CI and local Docker tests must pass without Gemini authentication or a running local model. |

## Progress

- 2026-05-03: Created `codex/plan-0017-gemini-gemma-research-flow` worktree.
- 2026-05-03: Added active execution plan.
- 2026-05-03: `scripts/agent-task.sh doctor` passed.
- 2026-05-03: Host Gemini CLI is installed at version 0.40.0; local Gemma health endpoint at `localhost:8089` returned ok, but a short chat completion timed out after 3 seconds.
- 2026-05-03: Added optional Gemini CLI search and local Gemma organization adapters with fallback status.
- 2026-05-03: Updated frontend so word or short-sentence input recommends first and selected recommendations request researched reports.
- 2026-05-03: Backend Ruff passed, backend pytest passed with 19 tests, web build passed, web Vitest passed with 7 tests.
- 2026-05-03: `scripts/agent-task.sh docker-test` passed, including API Ruff, backend pytest, web build, and web Vitest.
- 2026-05-03: `scripts/agent-task.sh verify` passed.
- 2026-05-03: Browser smoke on Docker preview confirmed short sentence recommendation, selected-item researched report generation, and visible Gemini/Gemma fallback status.

## Outcome

Word or short-sentence input now recommends concrete related items first. Selecting a recommendation requests the research pipeline, where Gemini CLI search and local Gemma4 organization run when available and otherwise return a structured fallback status with deterministic report content.

## Definition of Done

- Word or short-sentence input shows recommendations before research.
- Selecting a recommendation can run the search and organization pipeline before report generation.
- Reports expose whether research used Gemini CLI, Gemma4, fallback, or a partial mix.
- External adapter failures produce actionable status rather than uncaught 500s.
- Docker backend/frontend tests and standard verification pass.
- Product, backend, reliability, and security docs describe the new behavior and constraints.

## Follow-Up Cleanup

- Consider a persistent research cache and richer source ranking after the adapter contracts stabilize.

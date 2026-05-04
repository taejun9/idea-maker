# PLAN-0033 AI Item Recommendations

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/product-specs/index.md, docs/architecture/backend.md, docs/architecture/frontend.md, docs/operations/reliability.md, docs/operations/security.md
Roles: trail-guide, system-architect, api-crafter, frontend-crafter, reliability-warden, security-gatekeeper, doc-keeper, quality-auditor

## Goal

Generate varied, actually implementable recommended item ideas from a user-entered
word or short sentence by preferring the existing local Gemma/OpenAI-compatible AI
boundary and falling back to deterministic recommendations when AI is unavailable.

## Non-Goals

- Do not add a new third-party AI provider or require cloud AI credentials.
- Do not require a running local model for routine verification.
- Do not persist recommendation candidates in PostgreSQL.
- Do not redesign the full report-generation or report-history workflow.
- Do not send secrets, local files, or backend internals to the AI adapter.

## Assumptions

- The existing `/api/idea-recommendations` contract should stay backward
  compatible unless tests show a necessary extension.
- The approved AI path is the repository's local Gemma/OpenAI-compatible adapter
  pattern already used for quick examples and business contexts.
- The user input itself may be sent to the local AI adapter because the requested
  feature is to generate recommendations from that input; logs must still avoid
  storing raw prompts.
- Deterministic fallback should remain available so the product does not regress
  when the model is unavailable, times out, or returns invalid JSON.

## Constraints

- `apps/web` handles UI and client state only.
- `services/api` owns API schemas, orchestration, recommendation logic, and AI
  integration boundaries.
- Routes stay thin and do not call subprocesses or HTTP adapters directly.
- AI output must be parsed, validated, and normalized before entering response
  schemas.
- Runtime behavior changes need Docker-backed verification.

## Task Breakdown

- [x] Create task branch/worktree and active plan.
- [x] Run `scripts/agent-task.sh doctor`.
- [x] Inspect the current recommendation route, service, adapter patterns, and UI flow.
- [x] Add an AI item recommendation adapter through the existing local Gemma boundary.
- [x] Wire the recommendation service to prefer validated AI candidates and use deterministic fallback.
- [x] Add focused backend tests for AI success, invalid output, timeout/error fallback, and input specificity.
- [x] Update frontend only if the API contract or user-facing status needs adjustment.
- [x] Update product, backend, reliability, and security docs for AI recommendation behavior.
- [x] Run required verification and complete this plan before merge/push cleanup.

## Verification

- `scripts/agent-task.sh doctor`
- Focused backend tests for recommendation generation.
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test` because runtime recommendation behavior changes.
- `scripts/agent-task.sh ci` after moving the completed plan, if required by the merge flow.

Verification evidence:

- `scripts/agent-task.sh doctor` passed.
- `POSTGRES_PORT=56433 docker compose run --rm api python -m ruff check services/api tests tools` passed.
- `POSTGRES_PORT=56435 COMPOSE_PROJECT_NAME=idea-maker-plan0033-focus docker compose run --rm api python -m pytest services/api/tests/test_idea_reports.py services/api/tests/test_research_adapters.py -q` passed with `33 passed`.
- `scripts/agent-task.sh verify` passed.
- `POSTGRES_PORT=56433 API_PORT=58033 WEB_PORT=55133 scripts/agent-task.sh docker-test` passed with backend tests `44 passed`, Ruff, frontend build, and frontend tests `12 passed`.
- Direct local Gemma smoke check for `반려동물 산책` returned `provider='gemma4'`, `status='success'`, and four generated recommendations when using a 180 second timeout.

## Rollback Strategy

Revert this branch or merge commit to restore deterministic recommendation
behavior. Keep deterministic fallback in place during implementation so a partial
AI outage does not require rollback.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Use `PLAN-0033` for AI-generated item recommendations. | The current recommendation flow exists but produces repetitive candidates, and no active plan exists. |
| 2026-05-04 | Prefer the existing local Gemma/OpenAI-compatible boundary with deterministic fallback. | This follows the repository's AI adapter policy and keeps routine verification independent of live model availability. |

## Progress

- 2026-05-04: Request intake completed and worktree branch `codex/plan-0033-ai-item-recommendations` created.
- 2026-05-04: Active execution plan created from the request-intake meeting.
- 2026-05-04: `scripts/agent-task.sh doctor` passed.
- 2026-05-04: Added local Gemma item recommendation adapter, service wiring,
  improved deterministic fallback, focused backend tests, runtime config, and docs.
- 2026-05-04: Focused Docker backend tests passed (`33 passed`) and Ruff passed.
- 2026-05-04: Added `chat_template_kwargs.enable_thinking=false` for the item
  recommendation request so the local Gemma endpoint returns JSON content instead
  of spending the full token budget on reasoning output.
- 2026-05-04: `scripts/agent-task.sh verify`, `scripts/agent-task.sh docker-test`,
  and direct local Gemma smoke check passed.

## Outcome

`POST /api/idea-recommendations` now prefers local Gemma4/OpenAI-compatible
generation for four varied, implementation-ready recommendations from the user's
word or short sentence. AI output is validated for JSON shape, uniqueness, and
connection to the input before entering the response. When the model is
unavailable, times out, or returns invalid output, the endpoint returns improved
field-aware deterministic fallback recommendations instead of the same four
generic templates for every input.

## Definition of Done

- Word or short-sentence recommendation requests prefer AI-generated, varied,
  implementable item ideas tied to the user's input.
- AI failures fall back without uncaught request errors.
- Backend tests cover AI success and fallback behavior.
- User-facing behavior and AI data-handling rules are documented.
- Required verification passes.

## Follow-Up Cleanup

- None yet.

# PLAN-0029 AI Business Contexts

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/product-specs/index.md, docs/architecture/backend.md, docs/operations/security.md, docs/operations/reliability.md
Roles: api-crafter, reliability-warden, security-gatekeeper, doc-keeper, quality-auditor

## Goal

Generate business-field report contexts with an AI adapter for IT, 교육, 금융,
라이프스타일, 마케팅/PR, and 미디어/엔터테인먼트 instead of relying only on the
static `BUSINESS_FIELD_REPORT_CONTEXTS` map for those fields.

## Non-Goals

- Do not require external AI credentials or a running model for routine tests.
- Do not persist generated contexts in PostgreSQL.
- Do not change frontend layout or report history behavior.
- Do not send arbitrary local files or backend internals to AI.

## Assumptions

- "진짜 AI" means using the repository's existing local Gemma/OpenAI-compatible
  model boundary when available.
- If the AI adapter is unavailable, invalid, or times out, report generation must
  still complete through deterministic fallback behavior.
- AI context generation is scoped to the six requested fields.

## Constraints

- Routes stay thin; AI HTTP logic belongs in service/integration boundaries.
- AI outputs must be parsed and validated before entering report generation.
- Routine verification must not depend on third-party availability.
- Prompt content must avoid secrets and avoid raw local data.

## Task Breakdown

- [x] Inspect current context usage and existing AI adapter patterns.
- [x] Add AI-generated business context adapter and validated parsing.
- [x] Wire report/quick-example context lookup to use AI for the requested fields.
- [x] Add focused tests for AI success, fallback, and field scoping.
- [x] Update docs to describe AI context generation and fallback.
- [x] Run required verification and complete this plan.

## Verification

- `scripts/agent-task.sh doctor`
- Focused backend tests for AI context generation behavior.
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- `scripts/agent-task.sh ci` after moving the completed plan.

Verification evidence:

- `scripts/agent-task.sh doctor` passed.
- `POSTGRES_PORT=56434 docker compose run --rm api python -m pytest services/api/tests/test_idea_reports.py services/api/tests/test_research_adapters.py -q` passed with `25 passed`.
- `POSTGRES_PORT=56434 docker compose run --rm api python -m ruff check services/api tests tools` passed.
- `scripts/agent-task.sh verify` passed.
- `POSTGRES_PORT=56434 scripts/agent-task.sh docker-test` passed with backend
  tests `36 passed`, Ruff, frontend build, and frontend tests `12 passed`.

## Outcome

The backend now attempts local Gemma4/OpenAI-compatible generation for
business-field context when Q5 is IT, 교육, 금융, 라이프스타일, 마케팅/PR, or
미디어/엔터테인먼트. AI output is parsed through a Pydantic schema and converted
to the report context shape. Other fields continue to use deterministic context,
and AI failures fall back without failing the request.

## Rollback Strategy

Revert this branch before merge, or revert the merge commit after merge. The old
deterministic context map remains as fallback, so rollback can also disable the
AI context adapter wiring and keep existing report behavior.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Use local Gemma/OpenAI-compatible context generation with deterministic fallback. | Matches existing AI boundary and keeps routine verification credential-free. |

## Progress

- 2026-05-04: Request intake completed and active plan created.
- 2026-05-04: Added local Gemma business-context generator, service wiring,
  focused tests, runtime config, and docs.
- 2026-05-04: Focused Docker backend tests passed (`25 passed`) and Ruff passed.
- 2026-05-04: `scripts/agent-task.sh verify` passed.
- 2026-05-04: `POSTGRES_PORT=56434 scripts/agent-task.sh docker-test` passed
  with backend tests (`36 passed`), Ruff, frontend build, and frontend tests
  (`12 passed`).

## Definition of Done

- The six requested fields attempt AI context generation through a validated adapter.
- Non-requested fields continue to use deterministic context lookup.
- AI failures fall back without uncaught request errors.
- Tests and docs cover the new behavior.

## Follow-Up Cleanup

- None planned.

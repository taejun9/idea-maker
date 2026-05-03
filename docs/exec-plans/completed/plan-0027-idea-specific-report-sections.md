# PLAN-0027 Idea Specific Report Sections

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/product-specs/index.md, docs/architecture/backend.md
Roles: api-crafter, trail-guide, quality-auditor, doc-keeper

## Goal

Generate Q2-Q4 intake answers, target users, core use cases, strengths,
weaknesses, differentiation opportunities, key risks, recommended MVP scope,
and next validation steps from the submitted idea and Q5 business field instead
of returning generic section text.

## Non-Goals

- Do not add a new LLM dependency or external API call.
- Do not change competitor/source collection behavior.
- Do not change frontend report rendering unless the response contract requires it.

## Assumptions

- Deterministic backend generation can produce more idea-specific report sections
  by using the idea text, inferred/submitted Q5, generated Q1-Q4 answers, and
  optional research organization output.
- Existing optional Gemini/Gemma research flow remains scoped to selected
  recommendations and should still degrade to fallback output.

## Constraints

- Route handlers must remain thin; report composition belongs in service logic.
- Output must preserve the existing `IdeaReportResponse` schema.
- Tests must assert that the affected sections are tied to the input idea and
  business field.
- Docker-based verification is required because backend behavior changes.

## Task Breakdown

- [x] Inspect current report section generation and tests.
- [x] Add an idea-context builder for Q2-Q4 and the affected report sections.
- [x] Preserve research organization enrichment where available.
- [x] Update backend tests for idea-specific sections and regression coverage.
- [x] Update product docs.
- [x] Run verification.

## Verification

- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh doctor`
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- Optional API smoke request through Docker Compose if useful.

## Rollback Strategy

Revert the report section generation helpers, test expectations, and product doc
updates. Existing stored reports remain readable because the response schema is
unchanged.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Improve deterministic section generation instead of adding LLM calls. | It directly satisfies the request while keeping routine verification independent from credentials and external services. |

## Progress

- 2026-05-03: Request intake completed and worktree created.
- 2026-05-03: User expanded scope to include Q2, Q3, and Q4 intake answers.
- 2026-05-03: Added Q5-aware deterministic report section contexts and wired them into Q2-Q4 plus report sections.
- 2026-05-03: Smoke-tested Docker API response for a marketing/PR review-analysis idea and tuned Q2/Q3 wording.
- 2026-05-03: `scripts/agent-task.sh verify` passed.
- 2026-05-03: `WEB_PORT=25182 API_PORT=28010 POSTGRES_PORT=55444 scripts/agent-task.sh docker-test` passed; first run caught formatting and an existing frontend expectation mismatch that were fixed before rerun.
- 2026-05-03: `scripts/agent-task.sh ci` passed after moving the completed plan.

## Outcome

Report generation now derives Q2-Q4, target users, core use cases, strengths,
weaknesses, differentiation opportunities, key risks, recommended MVP scope, and
next validation steps from the submitted idea and selected Q5 business field.
Successful Gemma organization output still supplies research-specific target
users, use cases, opportunities, risks, and MVP scope when available.

## Definition of Done

- Q2-Q4 and the affected report sections include idea-specific and Q5-aware content.
- Existing research enrichment still participates when available.
- Backend and any impacted frontend tests pass in Docker.
- Docs and completed execution plan capture the behavior change.

## Follow-Up Cleanup

- Consider model-backed report copy refinement only after latency, cost, fallback,
  and source-of-truth behavior are specified.

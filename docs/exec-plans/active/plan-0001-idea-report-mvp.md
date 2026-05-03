# PLAN-0001 Idea Report MVP

Status: active
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: `docs/product-specs/index.md`, `docs/architecture/README.md`, `docs/architecture/backend.md`, `docs/architecture/frontend.md`
Branch: `codex/plan-0001-idea-report-mvp`
Worktree: `.worktrees/plan-0001-idea-report-mvp`

## Goal

Build the first vertical slice for generating an idea report from a short user prompt.

## Non-Goals

- real account system
- paid report export
- production scraping infrastructure
- authoritative market sizing

## Assumptions

- Backend starts with deterministic placeholder recommendation data until source integrations are implemented.
- Product Hunt, PitchWall, and BetaList facts must be fetched only when a current-data task explicitly requires it.
- Domestic and overseas competitors are separate report sections.

## Constraints

- Keep route handlers thin.
- Keep frontend API calls inside `apps/web/src/api/`.
- All report output must include source confidence fields even if placeholder data is used.
- Do not introduce a database in this plan.
- Local runtime tests use Docker Compose.
- PostgreSQL 18 is available even if persistence is not introduced in this plan.

## Task Breakdown

- [ ] Define `IdeaReportRequest` and `IdeaReportResponse` schemas.
- [ ] Implement report service with deterministic sample output.
- [ ] Add `POST /api/idea-reports`.
- [ ] Add frontend form and report result view.
- [ ] Add backend tests for validation and response shape.
- [ ] Add frontend unit test for report rendering.
- [ ] Update generated API contract docs.
- [ ] Run `scripts/agent-task.sh verify`.

## Verification

- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- Manual or Codex browser verification of the report workflow

## Rollback Strategy

- Revert route registration and frontend page wiring.
- Keep schemas if harmless and documented; otherwise remove the full vertical slice.
- Restore previous generated docs.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Start with deterministic source placeholders | Keeps MVP testable before external integrations. |
| 2026-05-03 | Separate domestic and overseas competitors in schema | Matches product value and report readability. |

## Progress

Initial plan created with harness.

## Definition of Done

- A user can enter an idea and receive a structured report.
- Backend and frontend tests pass.
- Report schema includes source and confidence metadata.
- Product spec and generated API docs are updated.

## Follow-Up Cleanup

- Add real source collector plan.
- Add database persistence plan.
- Add export/share plan.

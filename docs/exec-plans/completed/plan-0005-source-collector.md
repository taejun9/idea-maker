# PLAN-0005 Source Collector

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Completed: 2026-05-03
Related docs: `docs/product-specs/index.md`, `docs/architecture/backend.md`, `docs/references/README.md`, `docs/exec-plans/completed/plan-0001-idea-report-mvp.md`
Branch: `codex/plan-0005-source-collector`
Worktree: `.worktrees/plan-0005-source-collector`

## Goal

Replace deterministic placeholder source data with normalized source collector boundaries for public launch and competitor references.

## Non-Goals

- Scraping behind login walls.
- Persisting reports in PostgreSQL.
- Claiming source facts are current without observed dates.

## Assumptions

- Product Hunt, PitchWall, and BetaList require current-data verification before factual claims are surfaced.
- Domestic and overseas competitor records should share the same normalized source shape.
- The first collector implementation can keep deterministic tests by isolating network access behind integration boundaries.

## Constraints

- Keep FastAPI routes thin.
- Put external source logic under `services/api/app/integrations/`.
- Include source URL, observed date, and confidence for every source-derived record.
- Do not add secrets or paid API credentials without updating security docs.

## Task Breakdown

- [x] Define normalized source collector interfaces.
- [x] Add deterministic collector tests with fixture data.
- [x] Add Product Hunt, PitchWall, and BetaList collector stubs or approved integrations.
- [x] Add domestic/overseas competitor normalization.
- [x] Update API contract docs if response fields change.
- [x] Update tech debt tracker when placeholder-only data is removed.
- [x] Run `scripts/agent-task.sh verify` and `scripts/agent-task.sh docker-test`.

## Verification

- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- Source records include URL, observed date, and confidence.

## Rollback Strategy

- Revert collector wiring to the deterministic placeholder service.
- Keep schema additions only if backward compatible and documented.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Create source collector plan after MVP completion | PLAN-0001 intentionally shipped placeholder source data. |

## Progress

Completed fixture-backed source collector boundary and report service wiring.

## Outcome

- Added normalized source collector records under `services/api/app/integrations/`.
- Added deterministic fixture collectors for Korean competitor research, Product Hunt, PitchWall, and BetaList.
- Wired the report service to convert collector records into domestic/overseas competitors and source references.
- Added collector normalization tests and strengthened API response tests.
- Documented collector fixture limitations in `docs/references/source-collectors.md`.
- Resolved DEBT-0001 by replacing placeholder-only report source data.

## Verification Evidence

- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`

## Definition of Done

- Placeholder-only competitor/source records are replaced by collector-backed normalized records or documented fixture-backed stubs.
- Source confidence metadata remains present in every report section.
- Tests cover collector normalization and API response shape.

## Follow-Up Cleanup

- Added live source integration follow-up as `docs/exec-plans/active/plan-0006-live-source-integrations.md`.
- Add report persistence plan.
- Add export/share plan.

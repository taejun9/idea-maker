# PLAN-0006 Live Source Integrations

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: `docs/references/source-collectors.md`, `docs/architecture/backend.md`, `docs/exec-plans/completed/plan-0005-source-collector.md`
Branch: `codex/plan-0006-live-source-integrations`
Worktree: `.worktrees/plan-0006-live-source-integrations`

## Goal

Replace fixture-backed source collector stubs with approved live or browsed source integrations where current public facts are required.

## Non-Goals

- Scraping behind login walls.
- Adding paid API credentials without a security review.
- Persisting generated reports.

## Assumptions

- Current Product Hunt, PitchWall, and BetaList facts require browsing or approved source access.
- The fixture collector boundary from PLAN-0005 remains the compatibility layer.

## Constraints

- Update `docs/references/source-collectors.md` before exposing live facts.
- Preserve source URL, observed date, confidence, and source name for every record.
- Keep network access isolated under `services/api/app/integrations/`.

## Task Breakdown

- [x] Decide approved access method for each public source.
- [x] Implement live or browsed collectors behind the existing interface.
- [x] Add deterministic tests with fixtures and integration test gaps for network access.
- [x] Update API and reference docs if response semantics change.
- [x] Run `scripts/agent-task.sh verify` and `scripts/agent-task.sh docker-test`.

## Verification

- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- Collector outputs include source URL, observed date, confidence, and source name.

## Rollback Strategy

- Revert collector registration to PLAN-0005 fixture-backed collectors.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Keep live source integration separate from fixture collector boundary | Avoid presenting volatile public facts without explicit access-method documentation. |
| 2026-05-03 | Approve PitchWall public new-products JSON as the first live collector path | The endpoint is unauthenticated, exposed by the public homepage, and does not require forwarding user ideas as query parameters. |
| 2026-05-03 | Defer Product Hunt and BetaList live access | Product Hunt needs an approved API/token or explicit browsing path; BetaList needs a stable public access path before adding scraper-like behavior. |
| 2026-05-03 | Keep deterministic fixture fallback for live source failures and empty local matches | Report generation should remain reliable when third-party availability or local relevance matching is weak. |

## Progress

Implemented PitchWall live HTTP collector with deterministic fallback, fake-client tests,
and source/security/reliability documentation updates. Verification passed and plan is
complete.

## Outcome

- Added PitchWall live HTTP collection through an unauthenticated public JSON endpoint.
- Kept Product Hunt, BetaList, and domestic Korean collector paths deterministic until
  their access methods are approved.
- Added fixture fallback when PitchWall access fails or local matching returns no records.
- Updated frontend source-reference keys so duplicate source names with different URLs
  render predictably.
- Documented remaining source integration gaps as `DEBT-0007`.

## Verification Evidence

- `scripts/agent-task.sh verify`: passed; backend/frontend local checks skipped as
  expected because local dependencies are not installed.
- `scripts/agent-task.sh docker-test`: passed; backend pytest 11 tests, Ruff, web build,
  and web Vitest 2 tests passed.
- Live smoke: `PitchWallNewProductsCollector(max_records=2)` normalized current
  PitchWall records without sending the idea as a source query.

## Definition of Done

- At least one public source has an approved live or browsed collector path.
- Current facts are only displayed with observed dates and confidence.
- Fixture-backed fallback behavior remains deterministic and tested.

## Follow-Up Cleanup

- Resolve `DEBT-0007`: approve Product Hunt/BetaList access paths and add scheduled
  network smoke coverage for live collectors.
- Add report persistence plan.
- Add export/share plan.

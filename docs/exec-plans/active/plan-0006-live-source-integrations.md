# PLAN-0006 Live Source Integrations

Status: active
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

- [ ] Decide approved access method for each public source.
- [ ] Implement live or browsed collectors behind the existing interface.
- [ ] Add deterministic tests with fixtures and integration test gaps for network access.
- [ ] Update API and reference docs if response semantics change.
- [ ] Run `scripts/agent-task.sh verify` and `scripts/agent-task.sh docker-test`.

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

## Progress

Initial follow-up plan created after PLAN-0005 completion.

## Definition of Done

- At least one public source has an approved live or browsed collector path.
- Current facts are only displayed with observed dates and confidence.
- Fixture-backed fallback behavior remains deterministic and tested.

## Follow-Up Cleanup

- Add report persistence plan.
- Add export/share plan.

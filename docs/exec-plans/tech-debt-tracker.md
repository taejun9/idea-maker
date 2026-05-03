# Tech Debt Tracker

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Policy

Every intentional shortcut must have:

- owner
- reason
- risk
- cleanup trigger
- target date or review cadence

## Active Debt

| ID | Area | Debt | Risk | Owner | Cleanup Trigger | Status |
| --- | --- | --- | --- | --- | --- | --- |
| DEBT-0002 | CI | Frontend/backend dependency installation may be skipped until lockfiles exist | CI is initially partial | Codex | package lockfiles are added | open |
| DEBT-0004 | frontend | npm install reports 5 moderate audit findings in starter dependency tree | dependency risk needs triage before production | `platform-smith` | before public deployment or auth/user data launch | open |
| DEBT-0005 | backend | MVP reports are not persisted | Users cannot retrieve generated reports after refresh or across sessions | Codex | report persistence plan starts | open |
| DEBT-0006 | product | Export/share workflow is deferred | Users must manually copy report content | Codex | export/share plan starts | open |
| DEBT-0007 | integrations | Product Hunt and BetaList remain fixture-backed and PitchWall lacks scheduled network smoke coverage | Source breadth and third-party drift are not fully verified | `api-crafter` / `reliability-warden` | next source integration plan or scheduled smoke-test plan starts | open |

## Resolved Debt

| ID | Resolved Date | Resolution |
| --- | --- | --- |
| DEBT-0001 | 2026-05-03 | Replaced placeholder-only report source data with normalized collectors under `services/api/app/integrations/`; PitchWall now has a live path and remaining source gaps are tracked separately. |
| DEBT-0003 | 2026-05-03 | Ran harness improvement work from `codex/plan-0008-harness-engineering` worktree and added no-active-plan `ci` verification for clean `main`. |

## Weekly Gardening Checklist

- Close stale active plans.
- Move completed plans.
- Convert repeated debt into rules or tests.
- Update `docs/quality/quality-score.md` if risk changed.

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
| DEBT-0001 | backend | Recommendation output starts with deterministic placeholders | Reports are not market-current | Codex | source collector plan starts | open |
| DEBT-0002 | CI | Frontend/backend dependency installation may be skipped until lockfiles exist | CI is initially partial | Codex | package lockfiles are added | open |
| DEBT-0003 | git | Initial harness files were drafted before worktree policy was added | Working directory hygiene risk until first branch migration | Codex | first PR is created from a worktree branch | open |
| DEBT-0004 | frontend | npm install reports 5 moderate audit findings in starter dependency tree | dependency risk needs triage before production | `platform-smith` | before public deployment or auth/user data launch | open |

## Resolved Debt

| ID | Resolved Date | Resolution |
| --- | --- | --- |

## Weekly Gardening Checklist

- Close stale active plans.
- Move completed plans.
- Convert repeated debt into rules or tests.
- Update `QUALITY_SCORE.md` if risk changed.

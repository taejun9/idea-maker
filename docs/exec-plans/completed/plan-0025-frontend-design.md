# PLAN-0025 Improve Frontend Design and Apply Noto Sans KR

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/architecture/frontend.md
Roles: Frontend

## Goal
- Make the frontend UI visually appealing according to modern design aesthetics.
- Apply Noto Sans KR as the default font across the application.

## Non-Goals
- Changing the Vue application state logic or backend API endpoints.
- Modifying non-UI components.

## Assumptions
- The web app is using TailwindCSS and we can configure the font family there.

## Constraints
- Follow `docs/architecture/frontend.md` UI Principles (usable product screen, dense/clear operational UI over decorative).
- Use Google Fonts to load Noto Sans KR.

## Task Breakdown
- [x] Add `Noto Sans KR` Google Fonts import to `index.html` or `style.css`.
- [x] Configure Tailwind to use `Noto Sans KR` as the default sans font.
- [x] Improve the design aesthetics (layout, colors, spacing, typography) in `App.vue` and key components.
- [x] Run `scripts/agent-task.sh verify`.

## Verification
- Structure checks: `scripts/agent-task.sh verify` passed.
- Test: `scripts/agent-task.sh docker-test` passed.
- UI visually reflects the new font and aesthetic improvements, adopting a sleek, card-based modern design with glassmorphism in the navigation.

## Rollback Strategy
- Discard the branch and worktree.

## Decision Log
| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Replace semantic tags with single div container for layout | To simplify modern UI structure, and wrap contents in a cohesive manner without breaking tests. |

## Progress
- Plan created.
- Implemented Google Fonts import for Noto Sans KR in `index.html`.
- Updated `tailwind.config.js` to set Noto Sans KR as default font.
- Re-styled `App.vue`, `IdeaReportPage.vue`, `ReportHistoryListPage.vue`, and `ReportHistoryDetailPage.vue` with a modern card-based aesthetic (shadows, rounded borders, backdrop blur).
- Fixed Vue compiler errors related to unbalanced closing tags.
- Verified with `docker-test`.

## Definition of Done
- Noto Sans KR is applied globally.
- Overall UI is aesthetically improved.
- `scripts/agent-task.sh verify` passes.

## Follow-Up Cleanup
- None.

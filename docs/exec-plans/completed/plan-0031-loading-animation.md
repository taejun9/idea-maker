# PLAN-0031 Frontend Loading Animation

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/architecture/frontend.md, docs/product-specs/index.md, docs/quality/quality-score.md
Roles: frontend-developer, ui-designer

## Goal
Add a modern, visually striking loading animation to the frontend where loading states are needed (e.g., waiting for API responses during report generation or history fetching).

## Scope
- Create a reusable `LoadingAnimation.vue` component.
- Apply modern, dynamic design principles for the animation (e.g., pulsing gradient, spinning modern loader).
- Integrate the loading component into `IdeaReportPage.vue` (when submitting an idea), `ReportHistoryListPage.vue` (when fetching history), and other relevant pages with an `isLoading` or `isSubmitting` state.
- Ensure the loading state fits the premium aesthetic.

## Non-Goals
- Modifying backend endpoints.
- Altering other frontend features not related to loading states.

## Assumptions
- We can determine the loading states from existing component variables (e.g., `isLoading`, `isSubmitting`).
- The project uses Vue 3 + Tailwind CSS v4.

## Constraints
- Do not break existing UI layouts. The loading component should adapt to flexbox or flow layouts naturally.
- Follow the Apple-inspired, premium aesthetic established in the recent UI redesign.

## Task Breakdown
- [x] Investigate: Check `apps/web/src/features/idea-report/IdeaReportPage.vue` and `ReportHistoryListPage.vue` for existing loading states.
- [x] Implement Component: Create `apps/web/src/components/ui/LoadingAnimation.vue` with an impressive, smooth loading animation using Tailwind v4.
- [x] Integration: Update the features to show `LoadingAnimation.vue` instead of basic loading text or default browser loading.
- [x] Verification: Run `scripts/agent-task.sh verify` and build/lint checks.
- [x] Merge: Complete the task and merge to `main`.

## Verification
- `scripts/agent-task.sh verify`
- Check Vue component linting and building process via `scripts/agent-task.sh docker-test`.
- Visually verify the loading animation.

## Outcome

The frontend loading states use a reusable Tailwind-based loading animation
component in place of basic loading text where the plan integrated it.

## Rollback Strategy
Revert the component additions and file modifications in `IdeaReportPage.vue` and `ReportHistoryListPage.vue`.

## Decision Log
| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Use a custom Tailwind-based `LoadingAnimation` component. | Allows for highly customizable, premium loading states without adding heavy third-party UI library dependencies. |

## Definition of Done
- A reusable `LoadingAnimation.vue` component is created.
- The component is integrated into `IdeaReportPage.vue` and `ReportHistoryListPage.vue` replacing basic text.
- Lint, type checking, and tests pass successfully.
- Code is merged to main.

## Follow-Up Cleanup

- None recorded.

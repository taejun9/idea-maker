# PLAN-0009 Project Report Additions

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/product-specs/index.md, docs/generated/api-contract.md, docs/design-docs/core-beliefs.md
Roles: trail-guide, api-crafter, frontend-crafter, doc-keeper, quality-auditor

## Goal

Identify high-value additions for the idea report output and update the API, UI, tests, and repository documentation so future reports expose the missing MVP sections.

## Non-Goals

- Add or change external data source integrations.
- Add persistence or export behavior.

## Assumptions

- "Project report" refers to the product's generated idea report documented in `docs/product-specs/index.md`.
- The existing MVP product spec is the source for selecting additions; this task should not invent a new report category outside that scope.

## Constraints

- Do not commit directly on `main`.
- Keep report additions aligned with the existing MVP report scope.
- Preserve source URL, observed date, and confidence expectations for market facts.
- Avoid adding legal, financial, or investment advice claims.
- Keep deterministic report content suitable for current tests and fixture-backed source collectors.

## Task Breakdown

- [x] Read current product, architecture, quality, and operations docs relevant to report content.
- [x] Locate any report schema, templates, generated contracts, or tests that define report sections.
- [x] Select high-value report additions and document the reasoning.
- [x] Update backend response schema, deterministic service output, frontend type, UI rendering, and focused tests.
- [x] Update the appropriate source-of-record docs and generated/reference docs if needed.
- [x] Run required verification and move the plan to completed when finished.

## Verification

- `scripts/agent-task.sh doctor`
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh ci` after moving the completed plan
- `scripts/agent-task.sh docker-test`

## Rollback Strategy

Revert the documentation commit or move the completed plan back to active and revise the report additions before merging.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Add missing MVP report sections rather than inventing new ones. | Product specs already list useful report sections that the current API/UI contract does not expose. |
| 2026-05-03 | Keep source integration unchanged. | The additions are report-structure fields, not new public market facts. |

## Progress

- 2026-05-03: Created worktree and active execution plan.
- 2026-05-03: Found that API/UI expose only a subset of the documented MVP report sections.
- 2026-05-03: Added clarified concept, core use cases, differentiation opportunities, key risks, build complexity, and recommended MVP scope to the report contract and UI.
- 2026-05-03: `scripts/agent-task.sh verify` passed with backend/frontend local dependency skips.
- 2026-05-03: `scripts/agent-task.sh docker-test` passed backend tests, Ruff, frontend build, and Vitest.
- 2026-05-03: `scripts/agent-task.sh docker-down` cleaned up Compose resources.
- 2026-05-03: Final `scripts/agent-task.sh verify` passed before moving this plan to completed.

## Outcome

Completed the report contract expansion. The API and UI now expose the selected MVP-aligned additions: clarified concept, core use cases, differentiation opportunities, key risks, build complexity, and recommended MVP scope. Product and generated API docs now describe the implemented report contract.

## Definition of Done

- High-value report additions are exposed through API schema, frontend types, UI, and tests.
- Product/API docs reflect the new fields and boundaries.
- Verification passes.
- The completed plan is moved to `docs/exec-plans/completed/`.

## Follow-Up Cleanup

- Track implementation work separately if report schema, API, or UI changes are needed after documentation alignment.

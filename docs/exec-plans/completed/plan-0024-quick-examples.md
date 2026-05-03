# PLAN-0024 Quick Examples

Status: completed
Owner: Codex
Created: 2026-05-03
Last updated: 2026-05-03
Related docs: docs/product-specs/index.md, docs/architecture/frontend.md
Roles: frontend-crafter, trail-guide, doc-keeper, quality-auditor

## Goal

Show randomized quick idea examples aligned to the supported business fields:
IT, 교육, 금융, 운영관리, 네트워킹, 농축/수산업, 라이프스타일,
마케팅/PR, 모빌리티, 미디어/엔터테인먼트, 바이오/의류, 에너지/자원,
유통/물류, 임팩트, 재무, 프롭테크, 하드웨어.

## Non-Goals

- Do not add a new Gemma-backed quick-example generation API in this change.
- Do not change report generation, recommendation, or research adapter behavior.
- Do not introduce user-specific personalization or persistence for examples.

## Assumptions

- Refresh-time randomized local examples satisfy the immediate UX request.
- Gemma generation on every refresh needs a separate product and architecture decision because it adds latency, availability, and sensitive idea-handling concerns.
- The existing business-field list remains the source of truth for allowed Q5 fields.

## Constraints

- Keep `apps/web` limited to UI and client state.
- Avoid direct frontend access to backend internals or LLM adapters.
- Update product documentation when input experience behavior changes.
- Verify with the repository task branch harness before completion.

## Task Breakdown

- [x] Locate the current quick-example UI and test coverage.
- [x] Add a field-aligned quick-example pool and randomized display selection.
- [x] Update frontend tests for randomized examples without making them flaky.
- [x] Document the new input experience and the Gemma decision.
- [x] Run task verification and Docker-based tests required for frontend changes.

## Verification

- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh doctor`
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`
- Browser or Playwright check for the main input screen if the local Docker app starts cleanly.

## Rollback Strategy

Revert the quick-example data and selection helper changes, restore the previous static examples and test expectations, and remove this documentation update.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-03 | Use local randomized examples for this task. | It satisfies refresh-time variation without adding LLM latency, credentials, or new backend reliability risk. |
| 2026-05-03 | Treat Gemma quick-example generation as follow-up architecture work. | Existing Gemma support is scoped to organizing normalized research records, not generating unauthenticated homepage examples on every page load. |

## Progress

- 2026-05-03: Request intake completed and worktree created.
- 2026-05-03: Added randomized field-aligned quick examples and frontend test coverage.
- 2026-05-03: Fixed an IT quick example that matched the existing `리뷰` marketing keyword.
- 2026-05-03: `scripts/agent-task.sh verify` passed; `scripts/agent-task.sh docker-test` passed after the keyword fix.
- 2026-05-03: Playwright checked Docker Compose on `WEB_PORT=25180`, confirming randomized field labels, reload variation, button click input fill, and Q5 auto-selection.

## Outcome

Quick examples now load from a curated pool covering the requested 17 business
fields. The page displays a randomized three-example subset on each load with
field labels, and clicking an example fills the idea input while preserving Q5
auto-selection behavior. Product docs record that refresh-time Gemma generation
is deferred pending a separate API, fallback, latency, and data-handling design.

## Definition of Done

- Quick examples cover the requested business fields.
- The visible examples change randomly per page load while remaining deterministic enough to test.
- Tests and docs reflect the new behavior.
- Required verification commands pass or any blocker is documented.

## Follow-Up Cleanup

- Decide whether a backend quick-example endpoint should exist if the product later needs Gemma-generated examples.

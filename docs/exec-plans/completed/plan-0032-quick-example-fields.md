# PLAN-0032 Quick Example Fields

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/product-specs/index.md, docs/generated/api-contract.md
Roles: api-crafter, trail-guide, doc-keeper, quality-auditor

## Goal

Limit `GET /api/quick-idea-examples` generation to these six business fields:
IT, 교육, 금융, 라이프스타일, 마케팅/PR, and 미디어/엔터테인먼트.

## Non-Goals

- Do not change the full Q5 business-field option list.
- Do not change report generation field inference or saved report behavior.
- Do not change frontend layout.

## Assumptions

- The user-provided `미디어/엔터테이먼트` refers to the existing canonical
  product label `미디어/엔터테인먼트`.
- Requests for `count` greater than six should return the six allowed quick
  example fields rather than using other Q5 fields.
- AI generation and deterministic fallback should use the same restricted field
  set.

## Constraints

- Routes stay thin; field selection belongs in the service layer.
- Tests must not require a running local model.
- Docs must make the quick-example field restriction explicit.

## Task Breakdown

- [x] Inspect current quick-example selection and tests.
- [x] Restrict quick-example field selection to the six requested labels.
- [x] Update backend tests for the allowed field set and count clamping.
- [x] Update product/API docs and plan.
- [x] Run focused tests, verify, and Docker checks.
- [x] Complete and move this plan after verification.

## Verification

- `scripts/agent-task.sh doctor`
- Focused backend tests for quick examples
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test`

Verification evidence:

- `scripts/agent-task.sh doctor` passed.
- `POSTGRES_PORT=56432 docker compose run --rm api python -m pytest services/api/tests/test_idea_reports.py -q` passed with `25 passed`.
- `POSTGRES_PORT=56432 docker compose run --rm api python -m ruff check services/api tests tools` passed.
- First `scripts/agent-task.sh verify` exposed an inherited completed-plan guard failure in `plan-0031`; the missing sections were added.
- `scripts/agent-task.sh verify` passed after the plan format fix.
- `POSTGRES_PORT=56432 API_PORT=58032 WEB_PORT=55132 scripts/agent-task.sh docker-test` passed with backend tests `40 passed`, Ruff, frontend build, and frontend tests `12 passed`.

## Outcome

Quick-example generation now samples only `IT`, `교육`, `금융`, `라이프스타일`,
`마케팅/PR`, and `미디어/엔터테인먼트`. Both the AI request path and
deterministic fallback use that restricted field set, and requests above six
examples return at most the full six-field set.

## Rollback Strategy

Revert this change to restore quick-example selection from all Q5 fields except
`기타`.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Use the existing canonical label `미디어/엔터테인먼트`. | It is the schema and product-doc label already used by Q5 options. |
| 2026-05-04 | Return at most six examples even when `count` is larger. | The requested allowed field set contains six labels. |

## Progress

- 2026-05-04: Request intake completed and active plan created.
- 2026-05-04: Added `QUICK_EXAMPLE_FIELDS`, updated backend tests, and refreshed
  product/API/backend/reliability/security docs.
- 2026-05-04: Focused Docker tests, Ruff, `verify`, and full Docker tests passed.

## Definition of Done

- Quick examples are generated only for the six requested fields.
- Tests cover default and `count=10` behavior.
- Docs describe the restricted quick-example field set.
- Required verification passes.

## Follow-Up Cleanup

- None yet.

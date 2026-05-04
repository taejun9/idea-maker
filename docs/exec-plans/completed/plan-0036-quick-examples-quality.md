# PLAN-0036 Quick Examples Quality

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: README.md, docs/product-specs/index.md, docs/architecture/backend.md, docs/operations/reliability.md, docs/operations/security.md
Roles: trail-guide, api-crafter, frontend-crafter, reliability-warden, security-gatekeeper, doc-keeper, quality-auditor

## Goal

Improve quick idea examples so they stay within the intended quick-example
business fields and feel more AI-generated instead of repeatedly returning
similar deterministic-looking data.

## Non-Goals

- Do not expand the full Q5 report business-field taxonomy.
- Do not add a new external AI provider or require a running model for routine
  verification.
- Do not redesign the report creation page beyond quick-example behavior and
  copy needed to reflect the improved examples.
- Do not persist quick-example results in PostgreSQL.

## Assumptions

- The user's field restriction complaint refers to the quick example area on the
  input page, not the editable Q5 selector for full reports.
- The allowed quick-example fields for this task are `IT` and `교육` only.
- Repetition is likely caused by deterministic fallback text, prompt constraints,
  or process-local caching of successful model output.
- A fallback must remain because local Gemma4 is optional.

## Constraints

- Routes stay thin; example selection, prompt quality, cache policy, and fallback
  behavior belong in services or integrations.
- Local Gemma quick-example generation must receive only allowed field labels and
  a non-user variation angle, not raw user ideas, saved reports, local files,
  secrets, or competitor records.
- AI output must be parsed and validated before entering API response schemas.
- Tests must cover AI success, field restrictions, uniqueness/diversity behavior,
  and fallback without a live model.
- Root `README.md` must be updated in the same change because feature behavior is
  changing.

## Task Breakdown

- [x] Confirm current quick-example frontend/API/service/adapter behavior.
- [x] Run `scripts/agent-task.sh doctor` before implementation.
- [x] Tighten field selection and AI prompt/cache/fallback behavior as needed.
- [x] Add focused tests for field limits and improved variety.
- [x] Update product, backend, reliability/security docs, generated API docs if
      contract text changes, and root `README.md`.
- [x] Run focused Docker tests, `scripts/agent-task.sh verify`, and Docker
      runtime checks required by changed areas.
- [ ] Complete and move this plan after verification.

## Verification

- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh doctor`
- Focused backend tests for quick examples and local Gemma adapter behavior.
- Focused frontend tests if quick-example UI behavior changes.
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test` because quick-example runtime behavior may
  change across API and web.

Verification evidence:

- `scripts/agent-task.sh active-plan` passed.
- `scripts/agent-task.sh doctor` passed.
- `docker compose run --rm api python -m pytest services/api/tests/test_idea_reports.py services/api/tests/test_research_adapters.py -q` passed with `38 passed`.
- `docker compose run --rm api python -m ruff check services/api tests tools` passed.
- `docker compose run --rm --no-deps web npm run --workspace apps/web test -- --run` passed with `13 passed`.
- Browser verification on `http://127.0.0.1:55136` confirmed only IT/교육 quick examples render, Q5 keeps the full business-field list, and clicking an IT example fills the idea plus Q5=IT.
- `scripts/agent-task.sh verify` passed.
- `scripts/agent-task.sh docker-test` passed with backend tests `50 passed`, Ruff, frontend build, and frontend tests `13 passed`.

## Outcome

Quick examples now return only IT and 교육 examples by default. Q5 business-field
selection remains broader than the quick-example scope. Successful local Gemma
quick-example output is no longer cached, Gemma prompts include a non-user
variation angle, generated examples are rejected when duplicate idea text is
returned, and deterministic fallback now uses linked IT/education scenarios for
more coherent variety.

## Rollback Strategy

Revert this plan's branch before merge, or revert the merge commit after merge,
to restore the existing quick-example AI prompt, cache, and fallback behavior.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Keep local Gemma4 as the only AI generation boundary for quick examples. | It is already documented and avoids adding a new provider or secret surface. |
| 2026-05-04 | Preserve deterministic fallback while improving its variety. | Routine verification and product availability must not depend on a running local model. |

## Progress

- 2026-05-04: Request intake completed, `PLAN-0036` selected, and worktree
  branch `codex/plan-0036-quick-examples-quality` created.
- 2026-05-04: `active-plan` and `doctor` passed. Current quick-example behavior
  was confirmed to still allow six backend fields, while the frontend reused a
  broad field list for Q5 options.
- 2026-05-04: Limited quick examples to IT/교육, split frontend quick-example
  fields from the full Q5 options, removed quick-example AI result caching,
  added prompt variation and duplicate generated idea validation, and expanded
  deterministic fallback variety.
- 2026-05-04: Focused Docker backend tests passed with `38 passed`; backend
  Ruff passed; focused Docker frontend tests passed with `13 passed`.
- 2026-05-04: Browser verification on `http://127.0.0.1:55136` confirmed only
  IT/교육 quick examples render, the Q5 selector keeps the full business-field
  list, and clicking an IT example fills the idea and selects Q5=IT.
- 2026-05-04: `scripts/agent-task.sh verify` passed. Final
  `scripts/agent-task.sh docker-test` passed with backend tests `50 passed`,
  Ruff, frontend build, and frontend tests `13 passed`.

## Definition of Done

- Quick-example responses only use the intended quick-example field set.
- Generated and fallback examples have stronger per-field variety and fewer
  repeated static patterns.
- Tests cover the regression behind out-of-field examples and repetition.
- README and source-of-record docs describe the updated behavior.
- Required verification passes.

## Follow-Up Cleanup

- None yet.

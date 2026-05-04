# PLAN-0041 RAG Implementation Review

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/architecture/README.md, docs/architecture/backend.md, docs/product-specs/index.md, docs/operations/reliability.md, docs/operations/security.md, docs/references/rag-source-index.md, README.md
Roles: system-architect, api-crafter, reliability-warden, security-gatekeeper, quality-auditor

## Goal

Check whether the current vector RAG/source-index implementation is properly
applied to the project architecture, data handling rules, report generation
flow, and verification harness.

## Non-Goals

- Do not redesign RAG or replace the current retrieval approach unless a
  blocking defect is found.
- Do not add external embedding providers, pgvector, or a frontend UI.
- Do not merge code changes unless the review uncovers a concrete fix that can
  be safely implemented and verified in this task.

## Assumptions

- The current `main` branch contains the user's latest RAG implementation.
- A local deterministic vector retrieval path is acceptable for this review
  because provider-backed semantic embeddings remain a documented future gate.
- Routine checks must pass without Gemini authentication, a running Gemma
  server, external embedding APIs, or live third-party source availability.

## Constraints

- Work runs in `codex/plan-0041-rag-implementation-review`, not directly on
  `main`.
- Routes must remain thin; repositories own PostgreSQL source-index access, and
  services orchestrate retrieval and report generation.
- Source-index storage must not persist raw user ideas, query vectors, saved
  report payloads, secrets, local files, cookies, or authenticated responses.
- Retrieval output must expose user-relevant source evidence and status without
  leaking internal vectors or provider metadata.

## Task Breakdown

- [x] Run the active-plan gate and `scripts/agent-task.sh doctor`.
- [x] Inspect source-index repository, report-generation service wiring,
  schemas, migrations/schema docs, and RAG-related tests.
- [x] Check docs against implementation for vector retrieval behavior,
  fallbacks, privacy constraints, and verification expectations.
- [x] Run focused backend tests for source-index/report retrieval behavior.
- [x] Run `scripts/agent-task.sh verify`.
- [x] Report whether vector RAG is properly applied, including defects, risks,
  and missing verification if any.

## Verification

- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh doctor`
- Focused backend tests around source-index and report generation
- `scripts/agent-task.sh verify`

## Rollback Strategy

- If this review only produces findings, no runtime rollback is needed.
- If a focused fix is made, revert the touched files from this branch to restore
  the pre-review state.
- The existing token retrieval and request-path collectors remain the fallback
  path for source-index issues.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Review the implemented local vector RAG path before proposing provider-backed embeddings. | The user asked whether the current vector RAG application is correct. |

## Progress

- Request-intake meeting completed.
- Plan id selected: `PLAN-0041`.
- Created branch/worktree `codex/plan-0041-rag-implementation-review`.
- `scripts/agent-task.sh active-plan` passed.
- `scripts/agent-task.sh doctor` passed.
- Inspected source-index repository, report-generation wiring, schema docs,
  RAG docs, frontend research-status display, and focused tests.
- `python3 -m py_compile ...` passed for reviewed backend files and focused
  tests.
- Local `python3 -m pytest ...` was blocked because local Python lacks `pytest`;
  focused Docker pytest passed instead.
- Focused Docker pytest passed with `36 passed`.
- `scripts/agent-task.sh verify` passed; backend and frontend local steps were
  skipped by the script because local dependencies are absent.
- `scripts/agent-task.sh docker-test` passed with backend `55 passed`, Ruff,
  frontend build, and frontend `13 passed`.
- PostgreSQL source-index smoke passed with `method = source_index_vector` and
  `embedding` dimensions `64`.

## Outcome

The current implementation is structurally applied as local vector source-index
retrieval: normalized live public source records are persisted, local
deterministic embeddings are stored as JSONB, query vectors are computed only for
the request, vector retrieval runs before token fallback, and matching indexed
records are merged into report competitors and source references.

The review found no blocking runtime defect. The main caveat is product/contract
visibility: source-index retrieval status and method are internal today and are
not included in the public `research_status` payload, so users see source-index
records through source-reference notes but cannot see whether retrieval
succeeded, partially fell back, or was unavailable. The implementation is also
not provider-backed semantic vector RAG; it is a deterministic local vector
ranking layer over token-gated normalized source records.

## Definition of Done

- The implementation is checked against architecture, reliability, security,
  product docs, and tests.
- Verification results are recorded.
- The final report clearly states whether the current vector RAG application is
  sound, partial, or flawed.

## Follow-Up Cleanup

- Add source-index retrieval status/method to the report contract if product
  needs user-visible RAG diagnostics beyond source-reference notes.
- Keep provider-backed embeddings, pgvector, and semantic retrieval quality
  evaluation under the existing deferred RAG work.

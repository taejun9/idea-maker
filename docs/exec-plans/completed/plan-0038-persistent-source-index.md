# PLAN-0038 Persistent Source Index

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/architecture/README.md, docs/architecture/backend.md, docs/product-specs/index.md, docs/operations/reliability.md, docs/operations/security.md, docs/references/rag-source-index.md, docs/references/source-collectors.md, docs/generated/db-schema.md, README.md
Roles: system-architect, api-crafter, reliability-warden, security-gatekeeper, trail-guide, quality-auditor

## Goal

Implement Stage 1 RAG/source-index support by persisting normalized public source
records in PostgreSQL and retrieving them with deterministic metadata and token
matching before report organization.

## Non-Goals

- Do not add pgvector, embedding calls, vector search, or external embedding
  providers.
- Do not store raw user ideas, saved report payloads, cookies, credentials, local
  files, or authenticated source responses as retrieval documents.
- Do not add a frontend UI for retrieval internals.
- Do not make routine verification depend on Gemini authentication, a running
  Gemma server, or live third-party source availability.

## Assumptions

- The user approved proceeding from PLAN-0037 to Stage 1 implementation.
- PostgreSQL 18 remains the persistence target.
- Current request-path source collectors and Gemini CLI search can keep working;
  the source index augments them and can fall back when empty or unavailable.
- Fixture records are not indexed because they can include the submitted idea
  for deterministic report framing. They remain request-local report evidence
  only.

## Constraints

- Local runtime remains Docker Compose only.
- Backend routes stay thin; source indexing and retrieval live behind repository
  and service/integration boundaries.
- Source records used for generation keep source URL, source name, market,
  category, summary, observed date, confidence, and access method.
- Retrieval logs and statuses must avoid raw ideas and full prompts.
- Existing tests without `DATABASE_URL` must continue to run without requiring a
  live PostgreSQL instance.

## Task Breakdown

- [x] Inspect current report persistence, source collectors, schemas, and tests.
- [x] Add a source-index repository boundary for storing and retrieving
  normalized source records.
- [x] Connect report generation to retrieve indexed records with deterministic
  matching and fall back to current collectors when the index is empty.
- [x] Add focused tests for storage shape, deterministic retrieval, no raw idea
  persistence, fallback behavior, and report source merging.
- [x] Update README, generated schema, architecture/backend, reliability,
  security, source-collector, and RAG docs.
- [x] Run `scripts/agent-task.sh doctor`.
- [x] Run focused backend tests.
- [x] Run `scripts/agent-task.sh verify`.
- [x] Run `scripts/agent-task.sh docker-test` if runtime persistence behavior
  changes enough to require Docker verification.

## Verification

- `scripts/agent-task.sh doctor`
- Focused backend tests for source-index and report generation behavior
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh docker-test` when PostgreSQL runtime behavior is changed

## Rollback Strategy

- Revert source-index repository, service wiring, tests, and docs.
- Keep existing request-path source collectors and Gemini CLI search fallback
  intact so report generation can return to pre-index behavior.
- No external provider state or embedding index cleanup is required because this
  plan does not introduce embeddings or vector storage.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Implement Stage 1 persistent source index before vector RAG. | PLAN-0037 documented deterministic source index as the safest next step. |
| 2026-05-04 | Keep embeddings and pgvector out of this plan. | Provider, query privacy, and vector quality decisions are still deferred. |

## Progress

- Request-intake meeting completed.
- Plan id selected: `PLAN-0038`.
- Branch/worktree creation remains blocked by `.git` write restrictions in the
  current sandbox; no direct commit to `main` will be made.
- `scripts/agent-task.sh doctor` passed.
- Added `services/api/app/repositories/source_index.py` with in-memory and
  PostgreSQL source-index repositories.
- Connected API startup and report generation to source-index retrieval and
  best-effort indexing of live public source records.
- Added tests for token retrieval, freshness/market filtering, no raw-idea
  persistence, and report merging of indexed records.
- Updated README, generated schema, backend architecture, reliability, security,
  product, source-collector, RAG, and tech-debt docs.
- `python3 -m py_compile ...` passed for changed backend files and tests.
- `scripts/agent-task.sh docker-test` passed.
- PostgreSQL source-index smoke passed with schema creation, upsert, retrieval,
  and cleanup.
- `scripts/agent-task.sh verify` passed while this plan was active.

## Outcome

PLAN-0038 implemented Stage 1 persistent source-index support. The API now has a
source-index repository boundary for in-memory tests and PostgreSQL runtime. The
PostgreSQL path creates `source_observations`, stores indexable live public
source records, and retrieves matching records with deterministic token,
freshness, market, confidence, and observed-date ordering.

Report generation retrieves indexed source records before collecting current
request-path source records, merges indexed and current records, and best-effort
indexes newly collected live public records. Fixture records and records that
echo the submitted idea are not stored in the source index. Retrieved records are
marked in source-reference notes as source-index records.

Verification evidence:

- `scripts/agent-task.sh doctor`: passed
- `python3 -m py_compile ...`: passed
- `scripts/agent-task.sh docker-test`: passed with backend `54 passed`, Ruff,
  frontend build, and frontend `13 passed`
- PostgreSQL source-index smoke: passed
- `scripts/agent-task.sh verify`: passed

## Definition of Done

- Source records can be persisted and retrieved through a backend boundary.
- Report generation uses retrieved source records when available and preserves
  existing fallback behavior when not.
- Raw user ideas are not stored as retrieval documents.
- Tests cover deterministic retrieval and fallback behavior.
- Docs describe the implemented Stage 1 behavior and remaining vector-RAG gates.
- Required verification passes or any blocker is recorded.

## Follow-Up Cleanup

- Start embedding evaluation only after Stage 1 has enough source records and an
  accepted retrieval quality fixture.

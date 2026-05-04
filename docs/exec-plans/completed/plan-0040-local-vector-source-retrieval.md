# PLAN-0040 Local Vector Source Retrieval

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/references/rag-source-index.md, docs/generated/db-schema.md, docs/architecture/backend.md, docs/operations/security.md, docs/operations/reliability.md, README.md
Roles: system-architect, api-crafter, reliability-warden, security-gatekeeper, quality-auditor

## Goal

Add vector retrieval to the Stage 1 source index without external embedding
providers or pgvector by storing deterministic local embeddings for normalized
public source records and using request-local query vectors for retrieval.

## Non-Goals

- Do not call an external embedding provider.
- Do not add pgvector or a separate vector service.
- Do not store raw user ideas, query vectors, saved reports, cookies,
  credentials, local files, or authenticated responses.
- Do not change frontend UI.

## Assumptions

- The user explicitly asked to implement vector RAG from the current state.
- A local deterministic embedding is acceptable as the first vector retrieval
  implementation because it avoids provider, billing, retention, and raw-query
  exposure risks.
- Future semantic embedding providers can replace this implementation behind the
  same retrieval boundary after product and security decisions are accepted.

## Constraints

- PostgreSQL 18 remains the runtime database.
- Routine verification must not require network access, Gemini authentication,
  Gemma, external embedding APIs, or pgvector extension availability.
- Vector records must preserve source URL, observed date, confidence, source
  name, market, category, and access method.
- Query vectors are computed request-locally and discarded.

## Task Breakdown

- [x] Add local deterministic source-record embeddings to the source-index
  repository.
- [x] Store embeddings in PostgreSQL `source_observations` as JSONB vector data.
- [x] Use vector retrieval by default, with deterministic token fallback when no
  vector match is available.
- [x] Update tests for vector storage, vector ranking, token fallback, and
  no-raw-idea persistence.
- [x] Update README and RAG/backend/security/reliability/schema docs.
- [x] Run Docker tests, source-index smoke, `verify`, and `ci`.

## Verification

- `scripts/agent-task.sh docker-test`
- PostgreSQL vector source-index smoke
- `scripts/agent-task.sh verify`
- `scripts/agent-task.sh ci`

## Rollback Strategy

- Revert embedding/vector retrieval changes in `source_index.py`, tests, and
  docs.
- Existing token retrieval and request-path source collectors remain the fallback
  path.
- No external provider cleanup is required.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Implement local deterministic embeddings before provider-backed vectors. | It satisfies vector retrieval behavior without exposing raw ideas to a new provider. |
| 2026-05-04 | Store source embeddings as JSONB instead of pgvector. | The current Docker PostgreSQL 18 image does not guarantee pgvector availability. |

## Progress

- Request-intake meeting completed.
- Plan id selected: `PLAN-0040`.
- Added deterministic local source embeddings to the source-index repository.
- Added `embedding jsonb` storage to `source_observations`, including
  `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` for existing local databases.
- Updated retrieval to use token-gated vector scoring first, with token fallback
  when no vector match is available.
- Updated source-index tests for vector method and fixed-size embedding shape.
- Updated README, RAG, backend, security, reliability, product, source-collector,
  schema, and tech-debt docs.
- `python3 -m py_compile ...` passed.
- `scripts/agent-task.sh docker-test` passed.
- PostgreSQL vector retrieval smoke passed with `method = 'source_index_vector'`.
- `scripts/agent-task.sh verify` passed.

## Outcome

PLAN-0040 implemented local vector retrieval for source-index RAG without
external embedding providers, pgvector, or a separate vector service. Source
records now store deterministic JSONB vector data derived from normalized public
source fields. Query vectors are computed request-locally and are not persisted.

Retrieval now uses `source_index_vector` by default, with a token gate to avoid
hash-vector collision drift and token fallback when no vector match is available.
Provider-backed semantic embeddings and pgvector remain deferred behind product,
security, and quality decisions.

Verification evidence:

- `python3 -m py_compile ...`: passed
- `scripts/agent-task.sh docker-test`: passed with backend `55 passed`, Ruff,
  frontend build, and frontend `13 passed`
- PostgreSQL vector retrieval smoke: passed with `status = 'success'` and
  `method = 'source_index_vector'`
- `scripts/agent-task.sh verify`: passed

## Definition of Done

- Source-index records store deterministic local vector data.
- Retrieval uses vector scoring by default and returns source-index records for
  report generation.
- Raw user ideas and query vectors are not persisted.
- Tests and Docker verification pass.

## Follow-Up Cleanup

- Replace deterministic local embeddings with an evaluated provider or pgvector
  path only after product/security decisions and retrieval quality evaluation.

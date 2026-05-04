# PLAN-0039 Source Index Seed Smoke

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/references/rag-source-index.md, docs/generated/db-schema.md, docs/operations/reliability.md, docs/operations/security.md
Roles: api-crafter, reliability-warden, security-gatekeeper, quality-auditor

## Goal

Seed local PostgreSQL source-index records for the Stage 1 RAG implementation and
verify deterministic retrieval and report generation use the seeded records.

## Non-Goals

- Do not add pgvector, embeddings, vector columns, or an embedding provider.
- Do not store raw user ideas as retrieval documents.
- Do not commit runtime seed data.
- Do not change frontend UI or backend source code.

## Assumptions

- The user asked to add "vector data"; the current implementation has no vector
  storage, so this plan seeds source-index records instead.
- Seed records are local smoke-test data for the Docker PostgreSQL database.
- Routine verification should still pass without external live-source access.

## Constraints

- Local runtime remains Docker Compose only.
- Seed data must avoid raw user ideas, secrets, credentials, cookies,
  authenticated responses, local files, embeddings, and vector ids.
- Smoke commands should be deterministic and report whether seeded records are
  retrieved.

## Task Breakdown

- [x] Seed local PostgreSQL `source_observations` with local smoke records.
- [x] Run source-index retrieval smoke against the seeded records.
- [x] Run report generation smoke to confirm seeded source-index records appear
  in report source references.
- [x] Run `scripts/agent-task.sh verify`.
- [x] Complete the plan and move it to `completed/`.

## Verification

- Source-index retrieval smoke command
- Report generation smoke command
- `scripts/agent-task.sh verify`

## Rollback Strategy

- Delete seed records with `source_name = 'Local Source Index Seed'` if they
  should not remain in the local Docker database.
- No code rollback is needed because this plan does not change runtime code.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Seed Stage 1 source-index records instead of vector data. | The repository has no vector schema or embedding provider yet. |

## Progress

- Request-intake meeting completed.
- Plan id selected: `PLAN-0039`.
- Seeded 3 local PostgreSQL source-index records with `source_name = 'Local
  Source Index Seed'`.
- Retrieval smoke returned 2 review-analysis records with `status = 'success'`.
- Report smoke confirmed seeded source-index records appeared in source
  references and overseas competitor sections.
- `scripts/agent-task.sh docker-test` passed.
- `scripts/agent-task.sh verify` passed.

## Outcome

PLAN-0039 seeded local Stage 1 source-index data into the Docker PostgreSQL
database and verified retrieval/report behavior. This did not add vector columns,
embeddings, or pgvector data because the current implementation intentionally has
no vector store yet.

Seeded records:

- `AI Review Desk Seed`
- `국내 리뷰 분석 운영 시드`
- `Learning Routine Coach Seed`

Verification evidence:

- Source-index retrieval smoke: passed; review query retrieved `AI Review Desk
  Seed` and `국내 리뷰 분석 운영 시드`
- Report smoke: passed; generated report included the seeded source-index URL and
  source-index note
- `scripts/agent-task.sh docker-test`: passed with backend `54 passed`, Ruff,
  frontend build, and frontend `13 passed`
- `scripts/agent-task.sh verify`: passed

## Definition of Done

- Seed records exist in local PostgreSQL source index.
- Retrieval smoke confirms source-index matching works.
- Report smoke confirms generated reports can include seeded source-index
  references.
- Verification passes or blockers are recorded.

## Follow-Up Cleanup

- Replace local seed records with evaluated real collector records when embedding
  evaluation or scheduled source refresh work starts.

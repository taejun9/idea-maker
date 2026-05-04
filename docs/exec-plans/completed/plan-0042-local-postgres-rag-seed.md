# PLAN-0042 Local PostgreSQL RAG Seed

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/references/rag-source-index.md, docs/generated/db-schema.md, docs/operations/security.md, docs/operations/reliability.md
Roles: api-crafter, security-gatekeeper, quality-auditor

## Goal

Seed the currently running local Docker Compose PostgreSQL database with
source-index records that make local vector retrieval immediately testable.

## Non-Goals

- Do not add application code, frontend UI, external embedding providers,
  `pgvector`, or a scheduled refresh job.
- Do not store raw user ideas, saved reports, query vectors, secrets, cookies,
  credentials, local files, or authenticated source responses.
- Do not treat local seed records as verified market facts.

## Assumptions

- The user's running Docker Compose project is the root `idea-maker` stack with
  `idea-maker-db-1` healthy.
- "Necessary data" means `source_observations` rows with local deterministic
  embeddings for RAG/source-index smoke testing.
- Public-source records fetched from approved collectors may be inserted when
  the collector is available; deterministic local seed records cover the core
  Korean smoke queries when live public sources are unavailable or sparse.

## Constraints

- The seed must target the already running local Docker PostgreSQL database, not
  a separate worktree Compose project.
- Source-index writes must go through the repository boundary so embeddings and
  schema handling match application behavior.
- Verification must show `source_index_vector` retrieval and report-visible
  source-index records.

## Task Breakdown

- [x] Run active-plan and doctor checks in the task worktree.
- [x] Inspect the currently running Docker Compose services.
- [x] Seed local PostgreSQL through `PostgresSourceIndexRepository`.
- [x] Verify row counts, embedding dimensions, vector retrieval, and report
  inclusion.
- [x] Complete this plan and record verification.

## Verification

- `scripts/agent-task.sh active-plan`
- `scripts/agent-task.sh doctor`
- PostgreSQL source-index seed command output
- Source-index vector retrieval smoke
- Report generation smoke
- `scripts/agent-task.sh ci` after moving this plan to completed

## Rollback Strategy

- Delete seeded local records with `source_name` in `('Local RAG Seed',
  'PitchWall')` and URLs inserted by this task if the user wants the local DB
  cleaned.
- No application rollback is needed because this task does not change runtime
  code.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Seed the running root Compose database from the API container instead of starting a worktree Compose stack. | The user asked for data in the PostgreSQL instance already running locally. |

## Progress

- Request-intake meeting completed.
- Plan id selected: `PLAN-0042`.
- Created branch/worktree `codex/plan-0042-local-postgres-rag-seed`.
- Confirmed root Compose services were running: `idea-maker-db-1`,
  `idea-maker-api-1`, and `idea-maker-web-1`.
- `scripts/agent-task.sh active-plan` passed.
- `scripts/agent-task.sh doctor` passed.
- Seeded the running local Docker PostgreSQL database through
  `PostgresSourceIndexRepository`.
- Upserted 18 indexable records: 8 `Local RAG Seed` deterministic local smoke
  records and 10 current PitchWall public feed records.
- Backfilled 1 existing empty embedding from `Local Source Index Seed`.
- Final DB check found 21 `source_observations` rows and 21 rows with 64-value
  local deterministic embeddings.
- Source-index retrieval smoke for `리뷰 분석 도구` returned `status=success`
  and `method=source_index_vector`.
- Report generation smoke for `리뷰 분석 도구를 만드는 서비스` returned 8
  source-index references.
- `scripts/agent-task.sh verify` passed while this plan was active; backend and
  frontend local dependency checks were skipped by the script.

## Outcome

The currently running local Docker PostgreSQL database now contains source-index
data that makes local vector retrieval immediately testable.

Final source counts:

- `Local RAG Seed`: 8 records
- `Local Source Index Seed`: 3 records
- `PitchWall`: 10 records

All 21 `source_observations` rows have 64-value local deterministic embeddings.
The source-index smoke query returned `source_index_vector`, and a report smoke
included source-index references.

## Definition of Done

- The running local Docker PostgreSQL database contains source-index records with
  embeddings.
- A vector retrieval smoke returns `source_index_vector`.
- A report generation smoke includes at least one source-index reference.
- The final report states what was inserted and how to clean it up.

## Follow-Up Cleanup

- Replace local deterministic seed records with evaluated collector refresh jobs
  if persistent local source freshness becomes a product requirement.

# PLAN-0037 RAG Architecture Decision

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/architecture/README.md, docs/architecture/backend.md, docs/product-specs/index.md, docs/operations/reliability.md, docs/operations/security.md, docs/references/rag-source-index.md, README.md
Roles: system-architect, api-crafter, reliability-warden, security-gatekeeper, trail-guide, quality-auditor

## Goal

Document the implementation direction, security boundaries, reliability rules,
and evaluation plan for RAG before introducing vector storage, embeddings, or
new retrieval code.

## Non-Goals

- Do not implement pgvector, embedding calls, migrations, or retrieval APIs in
  this plan.
- Do not select a paid or external embedding provider without a documented
  product and security decision.
- Do not change report generation behavior or frontend UI behavior.
- Do not store raw user ideas as retrieval documents.

## Assumptions

- The user selected documentation and execution planning before implementation.
- Current code already has a source-record augmentation path for research
  reports, but not persistent vector RAG.
- RAG should improve competitor and source freshness quality before it is used
  as a speed optimization.
- PostgreSQL 18 remains the default database unless the design records a reason
  to introduce a separate retrieval service later.

## Constraints

- Local runtime remains Docker Compose only.
- Backend route handlers stay thin; collection, indexing, retrieval, and
  orchestration belong behind service or integration boundaries.
- User-submitted ideas are sensitive business intent and must not be stored in a
  retrieval index or sent to a new external embedding service without an
  explicit security review.
- Every source record used for generation must retain URL, source name, observed
  date, confidence, market, and access method.
- Routine verification for this documentation-only plan must not require Gemini
  authentication, a running Gemma server, or live third-party source access.

## Task Breakdown

- [x] Review existing RAG/source-index, backend architecture, reliability,
  security, and product docs.
- [x] Update the RAG/source-index decision with the recommended staged path,
  data model, retrieval contract, provider decision gates, and evaluation plan.
- [x] Update architecture, reliability, security, and README references if the
  design direction changes project-facing behavior or expectations.
- [x] Record deferred implementation work in the tech debt tracker if needed.
- [x] Run `scripts/agent-task.sh doctor`.
- [x] Run `scripts/agent-task.sh verify` while this plan is active.

## Verification

- Run `scripts/agent-task.sh doctor` before documentation edits beyond the plan.
- Run `scripts/agent-task.sh verify` before completion while this plan remains
  active.
- If verification is blocked by the current sandbox or Git state, record the
  exact blocker in the outcome.

## Rollback Strategy

- Revert the documentation changes in this plan if the selected RAG direction is
  rejected.
- Because no runtime code, schema migration, or external provider is introduced,
  rollback does not require Docker service or database state changes.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Start with RAG architecture and security documentation before implementation. | User selected planning option 3, and current docs defer vector/provider decisions. |
| 2026-05-04 | Avoid code, schema, pgvector, and embedding provider changes in this plan. | Documentation-first work should not introduce data-handling risk or runtime behavior changes. |

## Progress

- Request-intake meeting completed.
- Plan id selected: `PLAN-0037`.
- Branch/worktree creation attempted but blocked by `.git` write restrictions in
  the current sandbox; no direct commit to `main` will be made.
- `scripts/agent-task.sh doctor` passed.
- Reviewed product, architecture, backend, security, reliability,
  source-collector, and existing RAG/source-index docs.
- Expanded the RAG/source-index direction into a staged architecture decision.
- Updated backend, security, reliability, README, and tech-debt docs.
- `scripts/agent-task.sh active-plan` passed.
- `scripts/agent-task.sh verify` passed while this plan was active.

## Outcome

PLAN-0037 completed the documentation-first RAG decision. The repository now
records a staged path: persistent PostgreSQL source index with deterministic
retrieval first, embedding evaluation second, and vector retrieval only after
storage, freshness, provider, and evaluation gates are accepted.

The design keeps raw user ideas out of retrieval documents, treats embeddings as
public-source-record derived by default, and requires a product/security decision
before sending submitted ideas to any external embedding or vector provider.

Verification evidence:

- `scripts/agent-task.sh doctor`: passed
- `scripts/agent-task.sh active-plan`: passed
- `scripts/agent-task.sh verify`: passed; backend and frontend runtime checks
  were skipped by the script because this plan changed documentation only

## Definition of Done

- RAG direction is explicit enough to drive the next implementation plan.
- Security and reliability constraints for user ideas, source records, caching,
  and provider use are documented.
- Any deferred implementation tasks are tracked.
- Required verification has passed or any blocker is recorded.

## Follow-Up Cleanup

- Create the implementation plan only after the user accepts the staged RAG
  architecture and the provider/storage decisions.

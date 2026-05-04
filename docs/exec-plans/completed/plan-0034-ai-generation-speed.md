# PLAN-0034 AI Generation Speed And RAG Direction

Status: completed
Owner: Codex
Created: 2026-05-04
Last updated: 2026-05-04
Related docs: docs/architecture/README.md, docs/architecture/backend.md, docs/product-specs/index.md, docs/operations/reliability.md, docs/operations/security.md, docs/references/source-collectors.md, docs/references/rag-source-index.md
Roles: system-architect, api-crafter, reliability-warden, security-gatekeeper, trail-guide, quality-auditor

## Goal

Improve perceived speed for first-screen word recommendation and report generation without lowering output quality, and design the RAG/source-index direction for fresher competitor research quality.

## Non-Goals

- Do not reduce recommendation or report quality just to return faster.
- Do not introduce stale competitor facts as current market evidence.
- Do not persist raw user ideas into a retrieval index without an explicit security review.
- Do not add a vector database, embedding provider, or scraping dependency before the measured bottleneck and source policy justify it.

## Assumptions

- The highest-priority slow paths are first-screen word recommendations and report generation.
- The user does not accept lower quality as the tradeoff for speed.
- RAG is valuable if it improves current competitor/source quality, not as a blanket speed fix.
- Current optional AI adapters can fall back deterministically, but fallback must not become the default if it weakens user-visible quality.

## Constraints

- Local runtime remains Docker Compose only.
- Backend routes stay thin; generation, caching, retrieval, and adapter orchestration belong in services or integrations.
- User ideas are sensitive business intent and must not be logged raw or sent to new external services without product and security documentation.
- Source facts need URL, observed date, confidence, and retrieval status.
- Routine verification must not require Gemini authentication or a running llama.cpp server.

## Task Breakdown

- [x] Measure and document current latency by stage for word recommendations, normal report generation, and research report generation.
- [x] Identify quick wins that preserve quality, such as adapter health checks, bounded timeouts, request-stage instrumentation, prompt/token reductions, and safe parallelization.
- [x] Evaluate first-screen word recommendation improvements without quality loss, including cached high-quality examples, model warmup behavior, and local Gemma request tuning.
- [x] Evaluate report generation improvements, including parallel collection/organization where boundaries allow and avoiding duplicate business-context generation.
- [x] Define a RAG/source-index design for competitor research freshness: source scope, observed-date handling, retrieval confidence, invalidation, and security limits for user input.
- [x] Implement the smallest approved slice from the measured findings.
- [x] Update product, reliability, security, and source-collector docs when behavior or data handling changes.
- [x] Add focused backend tests for latency policy, fallback behavior, retrieval/source status, or caching behavior changed by the implementation.

## Verification

- Run `scripts/agent-task.sh doctor` before implementation.
- Run focused backend tests for generation/research adapter behavior.
- Run `scripts/agent-task.sh docker-test` if runtime API behavior changes.
- Run `scripts/agent-task.sh verify` before completion while this plan is active.
- If a frontend user flow changes, run the frontend test/build path and inspect the affected UI state.

## Rollback Strategy

- Keep latency instrumentation and behavior changes scoped behind existing service/integration boundaries.
- Revert new cache/retrieval paths by restoring deterministic and existing adapter flow.
- If RAG/source-index quality or security risk is unresolved, leave the design documented and ship only measurement or non-RAG speed improvements.

## Decision Log

| Date | Decision | Reason |
| --- | --- | --- |
| 2026-05-04 | Focus speed work on first-screen word recommendations and report generation. | User identified those as the slow paths. |
| 2026-05-04 | Do not trade quality for speed. | User rejected lower quality as an acceptable speed tradeoff. |
| 2026-05-04 | Treat RAG as a competitor-research quality/freshness feature, not the first speed fix. | RAG usually adds retrieval work, but can replace repeated live search if designed as a source index. |
| 2026-05-04 | Cache only successful Gemma results and public source payloads. | Fallback quality should not mask a recovered model, and source cache must not persist user ideas. |
| 2026-05-04 | Start baseline source collection and Gemini CLI search in parallel for research reports. | The two stages are independent and quality is preserved because organization still waits for merged records. |

## Progress

- Request-intake meeting completed.
- Blocking planning questions answered by user.
- Worktree branch created: `codex/ai-generation-speed`.
- Active execution plan created.
- Added process-local successful Gemma result caches for quick examples, Q5 business context, and word/short-sentence recommendations.
- Added process-local public source feed cache for PitchWall payloads with observed-date preservation.
- Added parallel startup for baseline source collection and Gemini CLI search in research report generation.
- Documented RAG/source-index direction in `docs/references/rag-source-index.md`.
- Focused backend tests passed: `44 passed`.
- Ruff backend check passed.
- `scripts/agent-task.sh verify` passed.
- `scripts/agent-task.sh ci` passed after moving the completed plan.
- `scripts/agent-task.sh docker-test` passed with backend `49 passed`, Ruff,
  frontend build, and frontend `12 passed`.

## Outcome

PLAN-0034 completed a quality-preserving speed pass. First-screen AI generation
paths now reuse successful process-local Gemma outputs for repeated quick-example
field sets and word/short-sentence recommendation seeds. Report generation now
reuses successful Q5 business-field contexts, caches public PitchWall feed
payloads before local filtering, and starts baseline source collection in
parallel with Gemini CLI search for research reports.

The RAG decision is documented as a source-index direction rather than an
immediate vector database addition. Future RAG work should retrieve from
normalized, dated source records and avoid indexing raw user ideas.

## Definition of Done

- Current bottleneck evidence is recorded.
- The chosen implementation improves perceived speed or preserves quality while making slow stages observable.
- Any RAG/source-index decision records data freshness, source confidence, security limits, and invalidation behavior.
- Tests and Docker-based verification pass for the changed areas.
- Updated docs describe changed runtime behavior and remaining limits.

## Follow-Up Cleanup

- Track persistent RAG/source-index work only after choosing an embedding model,
  storage path, refresh cadence, and retrieval evaluation method.
- Revisit quality score only if verification gates, source freshness risk, or security posture changes.

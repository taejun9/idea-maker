# RAG Source Index Direction

Last reviewed: 2026-05-04
Owner: Backend / Reliability / Security / Codex

## Purpose

This note defines how Idea-maker should approach RAG for fresher competitor and
startup reference quality. RAG is not the primary speed fix for model generation;
it is useful when repeated live search can be replaced by retrieval over normalized,
dated source records.

## Current Position

- PLAN-0034 adds a small source-index step by caching unauthenticated public
  source feed payloads before local filtering.
- PLAN-0038 adds Stage 1 persistence for normalized public source records and
  deterministic token retrieval before report organization.
- PLAN-0040 adds local deterministic vector retrieval by storing JSONB source
  embeddings derived from normalized public source records. It does not add
  external embedding providers, pgvector, or stored query vectors.
- The cache does not embed user ideas, does not persist report content, and does
  not replace source URL, observed date, or confidence fields.
- Provider-backed vector retrieval remains deferred until source freshness,
  invalidation, data handling, and retrieval quality are proven with normalized
  source records.
- The current research path is retrieval-augmented in the broad sense because it
  passes normalized source records into local Gemma organization, but it is not a
  persistent embedding or vector RAG system.

## Architecture Decision

Use a staged source-index architecture. Stage 1 persists normalized public source
records, stores local deterministic source vectors, and retrieves them with
token-gated vector scoring before falling back to metadata/token matching.
Provider-backed semantic embeddings remain an upgrade path, not the first
storage primitive.

### Stage 1: Persistent Source Index

- Add versioned PostgreSQL migrations before introducing multi-table source
  persistence.
- Persist only normalized public source records collected through approved
  collectors.
- Store collector metadata: source name, source URL, access method, observed
  date, fetched date, confidence, market, category, normalized title, summary,
  strengths, weaknesses, local source embedding, and collector version.
- Retrieve with deterministic local vector scoring over token-matched candidates
  first, then token filters when no vector match is available. Query vectors are
  computed request-locally and discarded.
- Mark retrieved records with `access_method="source_index"` in report output
  while preserving source URL, observed date, confidence, and source name.
- Store no raw user ideas, no saved report payloads, no authenticated source
  responses, and no cookies or credentials in retrieval tables.
- Pass only retrieved normalized source records into the report organizer.

### Stage 2: Provider Embedding Evaluation

- Add provider-backed embeddings only after Stage 1 has enough source records to
  evaluate recall, freshness, and duplicate behavior.
- Prefer embeddings over normalized public source records, not embeddings over
  raw user ideas or saved reports.
- Use digest or transient request identifiers for evaluation joins; do not store
  submitted ideas as retrieval documents.
- Evaluate Korean and English startup/source retrieval separately because token
  behavior and source coverage differ.

### Stage 3: Provider-Backed Vector Retrieval

- Choose PostgreSQL `pgvector` only if the source corpus remains small enough for
  the app database operational model and Docker Compose verification stays
  simple.
- Consider a separate retrieval service only if corpus size, refresh cadence, or
  ranking experiments exceed the API database boundary.
- Keep the service contract stable: retrieval returns normalized source records
  with provenance, not provider-specific vector hits.

## Recommended RAG Shape

1. Collect source records through approved collectors only.
2. Normalize every record into the existing source schema: title, URL, market,
   category, summary, observed date, confidence, source name, and access method.
3. Store only public source records and derived embeddings. Do not store raw user
   ideas as retrieval documents.
4. Retrieve records by a short-lived query derived from the submitted idea, then
   pass only normalized source records into the report organizer.
5. Show retrieval status in `research_status` when it becomes user-visible.

## Retrieval Contract

The retrieval boundary should accept:

- normalized idea text for request-local matching only
- optional Q5 business field
- locale
- requested markets
- observed date
- max records

The retrieval boundary should return:

- normalized source records
- retrieval status: `success`, `partial`, or `fallback`
- retrieval method: `source_index_vector`, `source_index_token`, `live_adapter`,
  or `fixture_fallback`
- freshness notes
- confidence notes

The report organizer must not receive raw collector payloads, vector ids,
embedding text, provider metadata, credentials, or untrusted instructions from
source pages.

## Freshness Rules

- Every retrieved record must retain its original observed date.
- Cached or indexed records must not be described as current unless their
  observed date and source policy support that claim.
- Source-specific TTLs should be documented next to each collector.
- If a live source fetch fails, continue with available records and expose
  fallback status rather than blocking report generation.
- Indexed records need invalidation rules by source. A public launch-directory
  feed can use a short freshness window, while fixture fallback records must
  remain low-confidence and must not be upgraded by storage alone.
- Refresh jobs should run outside the request path unless a collector is already
  approved for request-path access with a bounded timeout and fallback.

## Security Rules

- Do not send raw user ideas to a new external embedding or vector service without
  a product and security review.
- Do not index saved reports, user ideas, cookies, credentials, local files, or
  authenticated responses.
- Digest cache keys are acceptable for process-local lookup, but cached values
  that contain user-provided words remain sensitive and must stay in memory only.
- Local deterministic source embeddings are derived only from normalized public
  source text. If a future design embeds a request query with a provider, the
  query must be short-lived, not logged, and not stored.
- New embedding providers require documentation of data retention, region,
  billing/secrets, model name, and whether Korean source retrieval quality was
  evaluated.
- Retrieval logs should record counts, source names, freshness buckets, and
  method, not raw ideas, raw prompts, embeddings, or full source payloads.

## Evaluation Plan

- Build a small checked-in evaluation fixture with Korean and English idea seeds,
  expected source categories, and stale/fresh source examples.
- Measure whether retrieved records improve report source relevance compared
  with current live Gemini CLI search plus deterministic collectors.
- Track precision, duplicate rate, source freshness, fallback rate, and whether
  domestic and overseas records stay separated.
- Require deterministic tests for retrieval ordering, freshness filtering,
  low-confidence fixture handling, and no-raw-idea persistence.
- Keep live-source smoke checks separate from routine verification so local
  `verify` does not depend on third-party availability.

## Deferred Decisions

- Whether Stage 3 should use PostgreSQL 18 with `pgvector` or a separate
  retrieval service.
- Which embedding model is allowed for Korean and English startup/source
  retrieval.
- How often each public startup directory should be refreshed outside request
  paths.
- Which live-source smoke cadence is acceptable for Product Hunt, PitchWall,
  BetaList, and domestic competitor sources.

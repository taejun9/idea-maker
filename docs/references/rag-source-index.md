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
- The cache does not embed user ideas, does not persist report content, and does
  not replace source URL, observed date, or confidence fields.
- Vector retrieval is deferred until source freshness, invalidation, and data
  handling rules are proven with normalized source records.

## Recommended RAG Shape

1. Collect source records through approved collectors only.
2. Normalize every record into the existing source schema: title, URL, market,
   category, summary, observed date, confidence, source name, and access method.
3. Store only public source records and derived embeddings. Do not store raw user
   ideas as retrieval documents.
4. Retrieve records by a short-lived query derived from the submitted idea, then
   pass only normalized source records into the report organizer.
5. Show retrieval status in `research_status` when it becomes user-visible.

## Freshness Rules

- Every retrieved record must retain its original observed date.
- Cached or indexed records must not be described as current unless their
  observed date and source policy support that claim.
- Source-specific TTLs should be documented next to each collector.
- If a live source fetch fails, continue with available records and expose
  fallback status rather than blocking report generation.

## Security Rules

- Do not send raw user ideas to a new external embedding or vector service without
  a product and security review.
- Do not index saved reports, user ideas, cookies, credentials, local files, or
  authenticated responses.
- Digest cache keys are acceptable for process-local lookup, but cached values
  that contain user-provided words remain sensitive and must stay in memory only.

## Deferred Decisions

- Whether PostgreSQL 18 should use pgvector or a separate retrieval service.
- Which embedding model is allowed for Korean startup/source retrieval.
- How often public startup directories should be refreshed outside request paths.
- How retrieval quality will be evaluated against live Gemini CLI search.

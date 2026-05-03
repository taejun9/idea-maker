# Observability For Codex

Last reviewed: 2026-05-03
Owner: Reliability / Codex

## Purpose

Make system state readable to Codex during local development, CI, and debugging.

## Local Debug Loop

1. Start Docker Compose.
2. Call `/health`.
3. Check PostgreSQL 18 container health.
4. Run one report request.
5. Inspect JSON logs for `request_id`, `event`, `duration_ms`, and `error_code`.
6. Verify DOM text and `data-testid` selectors for the report flow.

## Required Metrics

- `http_requests_total`
- `http_request_duration_ms`
- `idea_report_created_total`
- `source_lookup_total`
- `source_lookup_failed_total`
- `idea_report_generation_duration_ms`

## Trace Boundaries

Create spans around:

- HTTP request
- report generation service
- each external source lookup
- report persistence once DB exists

## UI Readability

Primary screens should expose stable selectors:

- `data-testid="idea-input"`
- `data-testid="generate-report"`
- `data-testid="report-summary"`
- `data-testid="report-history-list"`
- `data-testid="history-detail-link"`
- `data-testid="domestic-competitors"`
- `data-testid="overseas-competitors"`
- `data-testid="source-references"`

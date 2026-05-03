# Reliability

Last reviewed: 2026-05-03
Owner: Reliability / Codex

## Reliability Goals

- The app must fail with explicit, user-readable errors.
- Every backend request must have a request id.
- Every external source call must have timeout, retry policy, source label, and observed date.
- Codex must be able to reproduce and verify a bug locally without private dashboards.

## Health Contract

Backend must expose:

- `GET /health`: process health, no external dependency check
- `GET /ready`: dependency readiness including PostgreSQL 18 once DB wiring exists

## Logging Contract

All service logs use JSON lines:

```json
{
  "timestamp": "2026-05-03T00:00:00Z",
  "level": "INFO",
  "event": "idea.report.created",
  "request_id": "req_123",
  "user_id": "anonymous",
  "source": "api",
  "duration_ms": 42,
  "error_code": null
}
```

Do not log secrets, raw API keys, auth headers, or full user prompts. Log prompt length, normalized topic, and report id instead.

## External Source Policy

Product Hunt, PitchWall, BetaList, and similar sources are volatile. Store:

- source name
- source URL
- retrieval date
- query
- normalized fields
- confidence notes

If current public facts are needed, Codex must browse or use an approved source-fetching integration. Stale cached facts must be labeled as stale.

Current PitchWall live collection uses one unauthenticated HTTP GET, a 3 second timeout,
no retry inside the request path, and deterministic fixture fallback when the endpoint
fails or no local token match is found.

Gemini CLI search, local Gemma4 organization, and local Gemma4 business-context
generation are optional request-path adapters. They have explicit timeouts and
must return structured fallback status instead of failing the report request.
Routine verification must not require Gemini authentication or a running
llama.cpp server. Business-context generation is scoped to selected Q5 labels and
falls back to deterministic contexts when the local model is unavailable.

## Incident Notes

Use `docs/exec-plans/active/` for incident fixes that require code changes. Completed incidents move to `docs/exec-plans/completed/` with root cause and regression test notes.

## Work Reports

Codex must report at task start and task finish.

Required first line:

- Start: `<작업자명>: <작업내용>`
- Finish: `<작업자명>: <보고내용>`

Start report:

- task id / branch
- goal
- expected changed areas
- verification plan
- risks or assumptions

Finish report:

- changed files summary
- commands run
- pass/fail status
- docs updated
- remaining risks and follow-up items

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

Gemini CLI search, local Gemma4 organization, local Gemma4 business-context
generation, local Gemma4 quick-example generation, and local Gemma4 item
recommendation generation are optional request-path adapters. They have explicit
timeouts and must return structured fallback status instead of failing the report,
quick-example, or recommendation request. Routine verification must not require
Gemini authentication or a running llama.cpp server. Business-context generation
is scoped to selected Q5 labels and quick-example generation receives only the
two allowed quick-example labels plus a non-user variation angle; both fall back
to deterministic content when the local model is unavailable. Item
recommendation generation receives the submitted word or short sentence and
falls back to deterministic field-aware recommendations when Gemma is unavailable
or invalid.

Successful local Gemma outputs for Q5 business-field context and item
recommendations are cached in process for a short TTL so repeated requests do not
block on the same model call. Quick-example AI output is not cached, preserving
freshness for repeated page loads. Fallback responses are not cached, which lets
a recovered Gemma server serve the next request. Research reports run baseline
source collection and Gemini CLI search in parallel, then organize the merged
records afterward.

Public source feed payloads can be cached briefly before local filtering. The
cache stores only the public feed payload and its observed date, not user ideas or
per-user report output. A source fetch failure is not cached and continues to use
the existing fixture fallback path.

## Generation Latency Budget

Configured request-path external waits as of PLAN-0036:

- Quick examples: one local Gemma call with
  `LOCAL_GEMMA_QUICK_EXAMPLES_TIMEOUT_SECONDS`, default 180 seconds. Successful
  quick-example output is not cached because the first screen should not repeat
  the same generated examples across page loads.
- Word/short-sentence recommendations: one local Gemma call with
  `LOCAL_GEMMA_RECOMMENDATIONS_TIMEOUT_SECONDS`, default 180 seconds. Repeated
  successful requests for the same normalized input and model use the AI cache.
- Normal report generation: public source collection includes the PitchWall live
  feed timeout, default 3 seconds, and supported Q5 fields may add one local Gemma
  business-context call, default 4 seconds. Repeated public feed and Q5 context
  hits use their caches.
- Research report generation: baseline source collection and Gemini CLI search
  now start in parallel. The remaining sequential waits are the slower of
  PitchWall live feed timeout or `GEMINI_SEARCH_TIMEOUT_SECONDS`, then Gemma
  organization, then any uncached Q5 business-context call.

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

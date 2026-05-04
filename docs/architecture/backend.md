# Backend

Last reviewed: 2026-05-03
Owner: Backend / Codex

## Stack

- Python 3.12+
- FastAPI
- Pydantic
- pytest
- Ruff
- PostgreSQL 18
- Docker Compose for local runtime and integration tests

## API Principles

- Routes are thin.
- Services contain business logic.
- Integrations normalize external sources before returning data.
- Schemas define every request and response boundary.
- Errors have stable `error_code` values.
- PostgreSQL access belongs in repository modules, not route handlers.
- Local CORS origins include the default Vite origin and any Docker Compose `WEB_PORT`
  or explicit `WEB_ORIGINS` values used for local verification.

## Source Recommendation Boundary

Recommendation sources include Product Hunt, PitchWall, BetaList, domestic competitors, and overseas competitors. Source collectors must return normalized records with:

- title
- URL
- market
- category
- summary
- observed date
- confidence
- source name

## Research Adapter Boundary

Selected recommendations can request an optional research pipeline:

1. `GeminiCliSearchAdapter` runs Gemini CLI in headless mode to collect public-source leads.
2. Search results are normalized into source records before report generation.
3. `LocalGemmaOrganizer` calls a llama.cpp OpenAI-compatible chat endpoint to organize normalized records.
4. Adapter failures return structured fallback status and must not raise uncaught request errors.

`LocalGemmaBusinessContextGenerator` uses the same OpenAI-compatible local Gemma
boundary to generate business-field context for IT, 교육, 금융, 라이프스타일,
마케팅/PR, and 미디어/엔터테인먼트. It receives only the business-field label,
validates JSON output, and falls back to deterministic context when unavailable.

`LocalGemmaQuickIdeaExampleGenerator` uses the same boundary for
`GET /api/quick-idea-examples`. The service selects supported Q5 field labels,
sends only those labels to Gemma, validates one generated idea per requested
field, and falls back to deterministic examples when the adapter is unavailable
or invalid.

Runtime configuration:

- `GEMINI_CLI_COMMAND`, default `gemini`
- `GEMINI_CLI_MODEL`, default `gemini-2.5-flash`
- `GEMINI_SEARCH_TIMEOUT_SECONDS`, default `12`
- `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `GOOGLE_CLOUD_PROJECT`, or
  `GOOGLE_CLOUD_PROJECT_ID` when Gemini CLI needs non-interactive authentication
- `LOCAL_GEMMA_BASE_URL`, default `http://localhost:8089` in code and `http://host.docker.internal:8089` in Docker Compose
- `LOCAL_GEMMA_MODEL`, default `gemma4`
- `LOCAL_GEMMA_TIMEOUT_SECONDS`, default `4`
- `LOCAL_GEMMA_CONTEXT_TIMEOUT_SECONDS`, default `LOCAL_GEMMA_TIMEOUT_SECONDS`
  or `4`, used for business-field context generation
- `LOCAL_GEMMA_QUICK_EXAMPLES_TIMEOUT_SECONDS`, default `180`, used for
  quick-example idea generation because page-load examples may tolerate slower
  model responses

Routes must not call subprocesses or HTTP adapters directly; this logic belongs in service/integration modules.
The API Docker image includes Node 22 and `@google/gemini-cli` so Docker Compose
can run Gemini CLI when credentials are provided.

## Verification

When backend changes:

```bash
scripts/agent-task.sh docker-test
```

Fast local harness checks may run without containers, but DB/API runtime verification is Docker-only.

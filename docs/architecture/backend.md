# Backend

Last reviewed: 2026-05-04
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
`GET /api/quick-idea-examples`. The service selects only IT and 교육 labels,
sends only those labels plus a non-user variation angle to Gemma, validates one
unique generated idea per requested field, and falls back to varied deterministic
IT/education examples when the adapter is unavailable or invalid.

`LocalGemmaIdeaRecommendationGenerator` uses the same boundary for
`POST /api/idea-recommendations`. It receives the submitted word or short
sentence, asks Gemma for four concrete Korean item recommendations, validates
JSON shape, uniqueness, and connection to at least one input term, then falls
back to deterministic field-aware recommendations when unavailable or invalid.

Successful local Gemma results for Q5 business-field context and
word/short-sentence recommendations are cached in process for a short TTL by
model, endpoint, and request shape. Quick-example AI output is deliberately not
cached so page-load examples can vary across repeated requests. Recommendation
cache keys use a digest of the normalized input; cached values remain
process-local and are not persisted.
Structured JSON Gemma requests disable model thinking when the OpenAI-compatible
llama.cpp endpoint supports `chat_template_kwargs.enable_thinking`.

Research report generation starts baseline source collection and Gemini CLI
search in parallel because both depend only on the normalized idea and observed
date. Gemma organization still runs after records are merged so the organizer has
the full evidence set.

## RAG / Source Index Boundary

The current research path is source-augmented generation with persistent
source-index retrieval and local deterministic vector scoring. Future
provider-backed RAG work must keep the same backend boundaries:

- collectors and retrieval modules return normalized source records
- repositories own PostgreSQL source-index reads and writes
- services orchestrate retrieval, merging, and report organization
- routes do not call collectors, embedding providers, vector search, SQL, or
  subprocesses directly

The current implementation persists normalized public source records, stores
JSONB local source embeddings, and retrieves with token-gated vector scoring
before token fallback. External embedding providers or `pgvector` may be added
only after the source schema, freshness rules, invalidation, and retrieval
evaluation method are accepted.

The retrieval contract returns source records plus status, method, and notes.
Report output marks indexed records with `access_method="source_index"` through
their source-reference note. Retrieval must not leak vector ids, provider
metadata, raw collector payloads, credentials, or untrusted source instructions
into report generation. Query vectors are request-local and are not persisted.

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
- `LOCAL_GEMMA_RECOMMENDATIONS_TIMEOUT_SECONDS`, default `180`, used for
  AI-generated item recommendations from short user input
- `AI_GENERATION_CACHE_TTL_SECONDS`, default `600`, used for process-local
  successful Gemma result reuse for Q5 business-field context and item
  recommendations
- `AI_GENERATION_CACHE_MAX_ENTRIES`, default `128`
- `SOURCE_INDEX_CACHE_TTL_SECONDS`, default `300`, used for public source feed
  payload reuse before local filtering
- `SOURCE_INDEX_CACHE_MAX_ENTRIES`, default `16`

Routes must not call subprocesses or HTTP adapters directly; this logic belongs in service/integration modules.
The API Docker image includes Node 22 and `@google/gemini-cli` so Docker Compose
can run Gemini CLI when credentials are provided.

## Verification

When backend changes:

```bash
scripts/agent-task.sh docker-test
```

Fast local harness checks may run without containers, but DB/API runtime verification is Docker-only.

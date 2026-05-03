# BACKEND.md

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

## Verification

When backend changes:

```bash
scripts/agent-task.sh docker-test
```

Fast local harness checks may run without containers, but DB/API runtime verification is Docker-only.

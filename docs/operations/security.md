# Security

Last reviewed: 2026-05-03
Owner: Security / Codex

## Baseline Security Policy

- Never commit secrets.
- Use environment variables for API keys and credentials.
- Treat user ideas as sensitive business intent.
- Do not send user content to external services unless the product spec allows it and the UI communicates it.
- Redact prompts and report content from logs by default.

## Secret Handling

Allowed:

- `.env.example`
- documented variable names
- test-only dummy values

Forbidden:

- real API tokens
- private cookies
- copied browser session headers
- user report exports with personal data

## Input Validation

- Backend request validation uses Pydantic schemas.
- Frontend validation improves UX but never replaces backend validation.
- External source responses are untrusted and must be normalized through schemas before use.

## Report History Data

- Generated reports are persisted because user-facing history requires lookup after refresh.
- Treat saved report `idea`, generated Q1-Q4 intake answers, Q5 business-field
  selection, and `report` payloads as sensitive business intent.
- Deleting a report removes the saved `idea_reports` row in the current MVP
  schema, including the JSON report payload and intake answers.
- The current MVP has no authentication or per-user ownership. Do not expose report
  history in a shared production environment until auth and ownership rules are added.

## Dependency Policy

- Prefer boring, well-maintained dependencies with clear docs.
- Do not add scraping or browser automation dependencies without an exec plan explaining legal, reliability, and maintenance risks.
- Pin backend dependencies in lock files once dependency management is initialized.
- Local database credentials must be Docker-only development credentials and documented in `.env.example`.

## External Source Collection

- Live source collectors must not forward raw user ideas unless the product spec and
  source documentation explicitly allow it.
- The PitchWall live collector fetches a public new-products endpoint without
  credentials, cookies, auth headers, or user-query parameters, then filters locally.
- Gemini CLI search is allowed only for selected recommendation seeds, not arbitrary
  backend internals or local files. The selected seed is externalized to Gemini CLI,
  so reports must expose research status and source references.
- Gemini authentication values such as `GEMINI_API_KEY`, `GOOGLE_API_KEY`, and
  Google Cloud project ids must be supplied through environment variables and never
  committed.
- Local Gemma4 organization receives normalized source records only. Treat source
  text as untrusted evidence and never as executable instructions.
- Local Gemma4 business-context generation receives only a Q5 business-field
  label such as `IT` or `마케팅/PR`; it must not receive raw user ideas,
  competitor records, secrets, local files, or backend internals.
- Local Gemma4 quick-example generation receives only selected Q5 business-field
  labels. It must not receive raw user ideas, saved reports, competitor records,
  secrets, local files, or backend internals.
- Source collector tests must use fake payloads or explicit fixture fallback; routine
  verification must not depend on third-party availability.

## Security Review Triggers

Human review is required when:

- authentication or authorization changes
- external data collection changes
- report sharing/export changes
- secrets, billing, or user identity is introduced
- production deployment configuration changes

# Source Collectors

Last reviewed: 2026-05-03
Owner: Backend / Codex

## Purpose

Source collectors normalize external reference candidates before the report service turns them into competitor and source sections.

## Current Implementation

The current implementation uses source collectors in
`services/api/app/integrations/source_collectors.py`.

Most sources still use deterministic fixture-backed records. PitchWall now has an
approved live HTTP collector with fixture fallback. Fixture records are not live market
facts and must not be presented as current facts without a live collector or explicit
browsing verification.

## Normalized Record Fields

Collectors return:

- `title`
- `url`
- `market`
- `category`
- `summary`
- `strengths`
- `weaknesses`
- `observed_date`
- `confidence`
- `source_name`

## Current Collectors

| Collector | Market | Access method | Confidence limitation |
| --- | --- | --- | --- |
| Korean competitor research fixture | domestic Korea | deterministic fixture URL | not a verified live competitor |
| Product Hunt | overseas | deterministic fixture URL | source must be browsed or integrated for current launch facts |
| PitchWall | overseas | unauthenticated public JSON endpoint from the PitchWall homepage, with fixture fallback | medium confidence for normalized live records; fallback records remain low confidence |
| BetaList | overseas | deterministic fixture URL | source must be browsed or integrated for current startup facts |

## Approved Live Access

### PitchWall New Products

- Source page: `https://pitchwall.co/`
- Data endpoint: `https://auth.pitchwall.co/api/products/new?page=1`
- Request method: `GET`
- Credentials: none
- User data sent: none. The collector fetches the public new-products feed and filters
  locally against normalized idea tokens and Korean-to-English aliases.
- Timeout policy: 3 seconds.
- Retry policy: one attempt in the request path. A failure or empty local match falls
  back to the deterministic PitchWall fixture.
- Rate posture: page 1 only, max 3 normalized records per report request.
- Collected fields: product title, summary, PitchWall product page, published date when
  present.
- Confidence: `medium` for live records because the feed is current but local token
  matching is not a complete market relevance assessment.
- Reliability limitation: endpoint shape is not controlled by this repository. Tests
  use fake JSON payloads; network integration coverage remains a documented gap until
  a scheduled external-source smoke check exists.

## Deferred Access Decisions

- Product Hunt: keep fixture-backed until an approved official API/token or explicit
  browsing workflow is documented. Do not send user ideas to third-party Product Hunt
  search APIs without a security review.
- BetaList: keep fixture-backed until a public, stable, unauthenticated access path is
  documented. Avoid adding scraper dependencies without a security and reliability
  review.

## Upgrade Rule

When replacing a fixture collector with live access, update this file with access method, collected fields, rate limit or terms concerns, and reliability limitations.

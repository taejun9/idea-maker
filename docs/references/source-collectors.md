# Source Collectors

Last reviewed: 2026-05-03
Owner: Backend / Codex

## Purpose

Source collectors normalize external reference candidates before the report service turns them into competitor and source sections.

## Current Implementation

The current implementation uses fixture-backed collectors in `services/api/app/integrations/source_collectors.py`.

These records are deterministic integration stubs. They are not live market facts and must not be presented as current facts without a live collector or explicit browsing verification.

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
| PitchWall | overseas | deterministic fixture URL | source must be browsed or integrated for current directory facts |
| BetaList | overseas | deterministic fixture URL | source must be browsed or integrated for current startup facts |

## Upgrade Rule

When replacing a fixture collector with live access, update this file with access method, collected fields, rate limit or terms concerns, and reliability limitations.

# References

Last reviewed: 2026-05-03
Owner: Research / Codex

## Purpose

This directory stores durable notes about external sources, APIs, directories, and research methods. It does not store unverified current market facts.

## Source Policy

For Product Hunt, PitchWall, BetaList, Korean competitors, and overseas competitors, record:

- source name
- URL
- observed date
- access method
- fields collected
- rate limits or terms concerns
- confidence limitations

## Current Reference Sources

| Source | Use | Notes |
| --- | --- | --- |
| Product Hunt | startup/product launch references | volatile; browse or integrate before current claims |
| PitchWall | startup/product launch references | volatile; browse or integrate before current claims |
| BetaList | early startup references | volatile; browse or integrate before current claims |
| Korean search/news/directories | domestic competitors | source must be cited per report |

Implementation note: current report source records are normalized through fixture-backed collectors documented in `source-collectors.md`.

## Codex Runtime References

- `codex-git-workflow.md`: worktree branch, PR, merge, cleanup flow.
- `codex-prompt-pack.md`: reusable Codex prompts.
- `codex-extensions.md`: recommended skills, MCP/plugin capabilities, and installation policy.
- `source-collectors.md`: source collector normalization, fixture limitations, and upgrade rules.

## Update When

- a new source is introduced
- a source access method changes
- terms, rate limits, or reliability risks are discovered
- generated reports rely on a source-specific normalization rule

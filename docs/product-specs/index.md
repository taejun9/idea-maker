# Product Specs

Last reviewed: 2026-05-03
Owner: Product / Codex

## Product Type

Idea-maker is a web service that turns a short idea into a structured business/product report.

## Users

- solo founders
- indie hackers
- product managers
- startup teams validating early concepts
- students or operators preparing idea reports

## Core Workflow

1. User enters a short idea in natural language.
2. If the input is a single word, the system recommends related concrete item ideas first.
3. User selects one recommended item or enters a fuller idea directly.
4. System clarifies the selected item or full idea into a concrete concept.
5. System recommends adjacent products/startups using sources such as Product Hunt, PitchWall, and BetaList.
6. System separates domestic Korean competitors and overseas competitors.
7. System generates a report containing overview, clarified concept, target users, core use cases, strengths, weaknesses, differentiation opportunities, risks, MVP scope, competitor table, source references, and next validation steps.

## Input Experience

- The idea input starts empty so users can enter their own concept without clearing a preset value.
- The entry form exposes visible examples, helper copy, character feedback, and validation state for keyboard and screen reader users.
- Single-word input with at least 1 non-space character requests related item recommendations instead of directly calling the report API.
- Multi-word input submits directly to report generation after at least 5 non-space characters, matching the report API contract.

## MVP Report Sections

- Executive summary
- Clarified concept
- Target users
- Core use cases
- Domestic competitors in Korea
- Overseas competitors
- Startup references from public launch directories
- Strengths
- Weaknesses
- Differentiation opportunities
- Key risks
- Build complexity
- Recommended MVP scope
- Validation checklist

## Implemented Report Contract

The current report API exposes the following MVP sections:

- Executive summary: `overview`
- Clarified concept: `clarified_concept`
- Target users: `target_users`
- Core use cases: `core_use_cases`
- Strengths and weaknesses: `strengths`, `weaknesses`
- Differentiation opportunities: `differentiation_opportunities`
- Key risks: `key_risks`
- Build complexity: `build_complexity`
- Recommended MVP scope: `recommended_mvp_scope`
- Domestic and overseas competitors: `domestic_competitors`, `overseas_competitors`
- Startup and source references: `source_references`
- Validation checklist: `next_validation_steps`

## Data Source Rules

- Public source facts must include source URL and observed date.
- If a source cannot be accessed, the report must say so and continue with available sources.
- Do not present old cached market facts as current.
- Product Hunt, PitchWall, and BetaList are used as inspiration/reference sources, not as the only truth.

## Non-Goals

- automatic incorporation or legal advice
- financial projections as authoritative claims
- scraping behind login walls without explicit approval
- replacing human market validation

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
2. If the input is a word or short sentence, the system recommends related concrete item ideas first.
3. User selects one recommended item or enters a fuller idea directly.
4. For a selected recommendation, the system searches public sources with Gemini CLI when available.
5. The system organizes normalized source evidence with local Gemma4 on llama.cpp when available.
6. System clarifies the selected item or full idea into a concrete concept.
7. System recommends adjacent products/startups using sources such as Product Hunt, PitchWall, and BetaList.
8. System separates domestic Korean competitors and overseas competitors.
9. User fills Q1-Q5 idea intake answers before final report generation.
10. System generates a report containing overview, Q1-Q5 answers, clarified concept, target users, core use cases, strengths, weaknesses, differentiation opportunities, risks, MVP scope, competitor table, source references, research status, and next validation steps.
11. User can reopen generated reports from the report history list and detail pages.
12. User can delete saved reports from the report history list.

## Input Experience

- The idea input starts empty so users can enter their own concept without clearing a preset value.
- The entry form exposes visible examples, helper copy, character feedback, and validation state for keyboard and screen reader users.
- Word or short-sentence input with at least 1 non-space character requests related item recommendations instead of directly calling the report API.
- Q1-Q5 answer inputs are submitted with the final report request and stored in the saved report payload.
- Selecting a recommended item requests the search-and-organization report path after Q1-Q5 answers are valid.
- Longer input submits directly to report generation after at least 5 non-space characters and valid Q1-Q5 answers, matching the report API contract.

## MVP Report Sections

- Executive summary
- Idea intake questions: Q1 one-line idea, Q2 background story, Q3 user/problem,
  Q4 realization plan, Q5 business field selection
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

- Report identity and history metadata: `id`, `idea`, `locale`, `created_at`
- Executive summary: `overview`
- Idea intake questions and business-field options: `idea_intake_questions`
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
- Search and organization status: `research_status`

`idea_intake_questions` contains the required Q1-Q5 prompts:

- Q1 asks for a one-line idea introduction and requires at least 10 characters.
- Q2-Q4 ask for background story, solved user/problem, and realization plan.
  These questions include copy noting that photos can be freely placed by
  drag-and-drop, with up to 5 photos total across the 3 questions.
- Q5 asks for one business field from IT, 교육, 금융, 운영관리, 네트워킹,
  농축/수산업, 라이프스타일, 마케팅/PR, 모빌리티, 미디어/엔터테인먼트,
  바이오/의류, 에너지/자원, 유통/물류, 임팩트, 재무, 프롭테크,
  하드웨어, 기타.
- When answers are submitted through `idea_intake_answers`, each matching
  `idea_intake_questions` item includes the saved `answer` value. Reports
  created by older clients keep empty answer values for backward compatibility.

The report history API exposes:

- `GET /api/idea-reports`: newest-first report summaries for the report history page
- `GET /api/idea-reports/{report_id}`: the full saved report detail
- `DELETE /api/idea-reports/{report_id}`: remove a saved report from history

The Docker runtime persists generated reports in PostgreSQL 18. Local tests without
`DATABASE_URL` use an in-memory repository so routine unit tests do not require a
database outside Docker.

## Data Source Rules

- Public source facts must include source URL and observed date.
- If a source cannot be accessed, the report must say so and continue with available sources.
- Do not present old cached market facts as current.
- Product Hunt, PitchWall, and BetaList are used as inspiration/reference sources, not as the only truth.
- Gemini CLI search and local Gemma4 organization are optional adapters. Their status must be exposed in `research_status`, and deterministic fallback must complete the report when either adapter is unavailable.

## Non-Goals

- automatic incorporation or legal advice
- financial projections as authoritative claims
- scraping behind login walls without explicit approval
- replacing human market validation

# 개미군단 Team Roster

Last reviewed: 2026-05-03
Owner: Team / Codex

## Purpose

This file defines the Codex-facing team map. Names are Korean for readability, and ids are English for branches, ownership labels, scripts, and issue tags.

## Team Identity

- Korean name: 개미군단
- English id: `ant-legion`
- Operating model: Codex-only implementation harness with human intent, review, and approval.

## Roles

| Korean name | ID | Role | Responsibilities | When Codex Uses This Role |
| --- | --- | --- | --- | --- |
| 길잡이 | `trail-guide` | Product Strategist | 제품 방향, 사용자, 보고서 구성, 국내/해외 경쟁 분석 기준 | product spec, report UX, source priority |
| 설계장 | `system-architect` | AI Systems Architect | 전체 아키텍처, 계층 경계, 실행 계획 체계 | cross-layer design, architecture review |
| 대장장이 | `platform-smith` | DevEx/Platform Engineer | Docker, CI, scripts, worktree flow, lint harness | tooling, local runtime, CI failures |
| 파수꾼 | `reliability-warden` | Reliability Engineer | logs, metrics, health checks, debugging 루프 | incidents, observability, flaky behavior |
| 문지기 | `security-gatekeeper` | Security Reviewer | secrets, user data, external source risk | auth, data handling, source collection |
| 화면장이 | `frontend-crafter` | Frontend Engineer | Vue UI, state, API client, UI verification | web app changes |
| API장이 | `api-crafter` | Backend Engineer | FastAPI, Pydantic, service/repository boundaries | API and backend logic |
| 기록관 | `doc-keeper` | Knowledge Steward | docs freshness, exec plans, tech debt, generated docs | doc gardening and drift cleanup |
| 검수관 | `quality-auditor` | Quality Engineer | tests, eval harness, quality score, PR gates | verification and review |

## Ownership Rules

- Every exec plan lists at least one role id.
- Every architecture or quality rule change mentions `system-architect` or `quality-auditor`.
- Every Docker/CI/script change mentions `platform-smith`.
- Every external source integration mentions `security-gatekeeper` and `reliability-warden`.
- Every product report section change mentions `trail-guide`.

## Branch Label Convention

Use role ids only when helpful:

```text
codex/<task-id>
codex/platform-smith-docker-runtime
codex/api-crafter-report-schema
```

## Report Convention

Start report includes:

- team: 개미군단 (`ant-legion`)
- active role ids
- task id
- branch/worktree
- goal
- expected changed areas
- verification plan

Finish report includes:

- active role ids
- completed changes
- verification results
- docs updated
- remaining risk
- follow-up owner id


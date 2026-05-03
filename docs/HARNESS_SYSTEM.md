# Codex Harness Engineering System

Last reviewed: 2026-05-03
Owner: Platform / Codex

## Assumptions

- 이 프로젝트는 Codex에서만 운영한다.
- 팀명은 개미군단이며 canonical team id는 `ant-legion`이다.
- frontend는 Vue + Vite + TailwindCSS + TypeScript를 기본으로 한다.
- backend는 Python FastAPI를 기본으로 한다.
- 로컬 런타임과 테스트는 Docker Compose로 실행한다.
- PostgreSQL은 18 버전을 사용한다.
- Node는 22 버전을 사용한다.
- 추천/경쟁사 조사 소스는 Product Hunt, PitchWall, BetaList, 국내 경쟁사, 해외 경쟁사다.
- 초기 팀 규모는 1-3명이며, Codex가 구현/검증/문서 갱신의 대부분을 수행한다.
- 초기 배포는 단일 web + API 서비스이며, DB는 나중에 PostgreSQL을 도입한다.

## 0. Executive Summary

이 시스템은 Codex가 안정적으로 일하도록 저장소를 작업 환경, 지식 시스템, 검증 장치, 품질 평가 루프로 설계한다. `AGENTS.md`는 짧은 맵이고, 실제 지식은 `docs/`에 버전 관리된다. 중요한 규칙은 문서가 아니라 `tools/`, `lint-rules/`, CI에서 검사한다.

핵심 레버리지는 세 가지다.

- 작업 전 읽어야 할 문서와 실행 계획을 고정한다.
- Codex가 수정 후 반드시 돌리는 `scripts/agent-task.sh verify`와 CI/main용 `scripts/agent-task.sh ci`를 둔다.
- 품질, 문서 신선도, 아키텍처 위반을 CI에서 반복 측정한다.

장점은 반복 가능한 개발, 낮은 온보딩 비용, 작은 PR, 명확한 롤백이다. 한계는 초기 문서/규칙 유지비와 과도한 규칙화 위험이다. 그래서 모든 규칙은 `docs/quality/quality-score.md`와 tech debt tracker에서 주기적으로 조정한다.

## 1. System Blueprint

```text
Human intent
  -> Codex reads AGENTS.md
  -> Codex sends worker-name-prefixed task start report
  -> Codex runs request-intake planning meeting
  -> Codex creates worktree branch
  -> Codex reads docs and active exec plans
  -> Codex creates or updates an execution plan from meeting output
  -> Codex implements a small change
  -> scripts/agent-task.sh verify
  -> CI repeats mechanical checks
  -> PR review checks risk and docs
  -> merge
  -> worktree and branch cleanup
  -> Codex sends worker-name-prefixed task finish report
  -> completed exec plan + quality score + tech debt updates
```

Repository map:

```text
AGENTS.md                    Codex entry map
README.md                    human project entry
docs/                        source of record
docs/architecture/           enforceable architecture contracts
docs/operations/             reliability and security operations
docs/quality/                rubrics and quality score
docs/observability/          logs, metrics, debugging contracts
tools/                       repository inspection scripts
scripts/                     Codex command harness
lint-rules/                  machine-readable architecture policies
evals/                       harness evaluation scenarios
apps/web/                    Vue frontend
services/api/                Python backend
.github/workflows/           CI
```

Lifecycle:

1. Prompt and planning meeting: user states intent; Codex records goal, scope, non-goals, assumptions or open questions, role ids, expected changed areas, verification, and selected plan id.
2. Execution plan: every task gets or updates a plan in `docs/exec-plans/active/` from that meeting before task work.
3. Implementation: Codex changes the smallest coherent slice.
4. Verification: local harness and tests run.
5. PR: short PR, checklist, docs update notes.
6. Merge: block gates must pass; warn gates produce follow-up debt.
7. Cleanup: completed plan, score update, debt tracker update.

## 2. Repository Layout

```text
.
├── AGENTS.md
├── README.md
├── apps/
│   └── web/
│       ├── package.json
│       ├── index.html
│       ├── src/
│       └── tests/
├── services/
│   └── api/
│       ├── app/
│       └── tests/
├── docs/
│   ├── HARNESS_SYSTEM.md
│   ├── architecture/
│   │   ├── README.md
│   │   ├── backend.md
│   │   └── frontend.md
│   ├── design-docs/
│   ├── exec-plans/
│   │   ├── active/
│   │   └── completed/
│   ├── generated/
│   ├── observability/
│   │   └── README.md
│   ├── operations/
│   │   ├── reliability.md
│   │   └── security.md
│   ├── product-specs/
│   ├── quality/
│   │   ├── quality-score.md
│   │   └── review-rubric.md
│   ├── references/
│   └── team/
├── scripts/
├── tools/
├── tests/
├── evals/
├── lint-rules/
├── docker-compose.yml
└── .github/workflows/
```

Directory responsibilities:

- `docs/design-docs/`: durable engineering decisions and beliefs.
- `docs/architecture/`: architecture boundaries and frontend/backend rules.
- `docs/product-specs/`: product goals, users, workflows, report structure.
- `docs/exec-plans/active/`: current multi-step Codex work.
- `docs/exec-plans/completed/`: finished plans with outcomes.
- `docs/references/`: external source notes and integration references.
- `docs/team/`: 개미군단 역할, 한글 이름, 영어 id, 책임.
- `docs/generated/`: generated facts such as DB schema and API contracts.
- `docs/operations/`: reliability, security, and runtime operating rules.
- `docs/quality/`: scoring rubrics and review standards.
- `scripts/`: stable commands Codex should run.
- `tools/`: repository checks used locally and in CI.
- `docs/observability/`: logging, metrics, tracing, debugging guides.
- `evals/`: scenarios to measure whether the harness works.
- `lint-rules/`: machine-readable policy source for structure checks.

## 3. AGENTS.md Draft

The actual file is `AGENTS.md`. It must stay short and route Codex to source-of-record docs.

## 4. Docs System of Record

Required docs and update triggers:

| File | Purpose | Update trigger |
| --- | --- | --- |
| `docs/design-docs/index.md` | design doc index | new/changed design doc |
| `docs/design-docs/core-beliefs.md` | product and engineering beliefs | strategy or operating principle changes |
| `docs/product-specs/index.md` | product scope | user-facing behavior changes |
| `docs/team/roster.md` | Codex-facing team responsibilities | role or ownership changes |
| `docs/exec-plans/README.md` | plan framework | workflow changes |
| `docs/exec-plans/active/*.md` | active work plan | complex work starts or changes |
| `docs/exec-plans/completed/*.md` | outcome history | plan completes |
| `docs/exec-plans/tech-debt-tracker.md` | debt queue | warn gates, shortcuts, deferred work |
| `docs/references/README.md` | source policy | source/integration changes |
| `docs/references/codex-extensions.md` | skills/MCP recommendations | extension install or adoption changes |
| `docs/generated/db-schema.md` | generated DB facts | DB migration changes |
| `docs/quality/quality-score.md` | merge quality posture | quality gate changes |
| `docs/operations/reliability.md` | health/logging/debugging | reliability behavior changes |
| `docs/operations/security.md` | security posture | auth/data/source changes |
| `docs/architecture/frontend.md` | frontend rules | UI architecture changes |
| `docs/architecture/backend.md` | backend rules | API/service architecture changes |

## 5. Execution Plan Framework

Every complex task plan includes:

- metadata: id, owner, status, created, last updated
- goal and non-goals
- assumptions and constraints
- task breakdown
- verification criteria
- rollback strategy
- decision log
- progress status
- definition of done
- follow-up cleanup

Completed MVP plan exists at `docs/exec-plans/completed/plan-0001-idea-report-mvp.md`.

## 6. Architecture Rules

Rules are written in prose in `docs/architecture/README.md` and mirrored in `lint-rules/architecture_rules.yml` for mechanical checks.

Machine-testable statements:

- `apps/web` must not import from `services/api`.
- files under `apps/web/src/components` must not call `fetch`.
- backend route modules must not import `sqlite3`, `psycopg`, `sqlalchemy`, or external source clients directly.
- all required source-of-record docs must include `Last reviewed:`.
- active exec plans must include `Roles`, `Rollback Strategy`, `Verification`, and `Decision Log`.
- completed exec plans must include outcome, verification, and follow-up cleanup sections.

## 7. Mechanical Enforcement

Local:

```bash
scripts/agent-task.sh doctor
scripts/agent-task.sh verify
scripts/agent-task.sh ci
```

`verify` is for task branches with an active plan. `ci` is for clean `main` and
CI runs after active plans have been completed and moved.

CI stages:

1. repository structure
2. docs freshness and links
3. architecture rules
4. backend lint/test
5. frontend install/build/test
6. execution plan placement and required sections
7. quality score smoke check

Initial scripts:

- `tools/structure_guard.py`
- `tools/docs_freshness.py`
- `tools/link_check.py`
- `tools/architecture_scan.py`
- `tools/exec_plan_guard.py`
- `tools/quality_score.py`

## 8. Agent Workflow Harness

All workflows start with a worker-name-prefixed request-intake planning meeting report and finish with a worker-name-prefixed finish report. All implementation work uses worktree branches and avoids direct commits on `main`.

Bug fix:

1. send `<작업자명>: <작업내용>` start report and run request-intake planning meeting
2. create worktree branch
3. create or update active exec plan from meeting output
4. reproduce with Docker test or local command
5. inspect logs/errors
6. patch smallest layer
7. add regression test
8. update plan/debt docs if needed
9. run verify and docker-test
10. send `<작업자명>: <보고내용>` finish report

New feature:

1. run request-intake planning meeting
2. create active exec plan from meeting output
3. update product spec first
4. add backend schema/service/API slice
5. add frontend feature slice
6. add tests and UI verification
7. complete plan

Refactoring:

1. define invariant and rollback
2. add characterization tests
3. move code in small steps
4. run architecture scan
5. update architecture docs only if rule changes

Doc gardening:

1. run docs freshness and link checks
2. remove stale duplicates
3. update indexes
4. move completed plans
5. update quality score and debt tracker

## 9. Observability and Readability for Agents

Use JSON logs, stable error codes, request ids, and deterministic health endpoints. UI states should be inspectable by DOM text and stable `data-testid` attributes for primary workflows. Error messages must include what failed, likely cause, and next action without exposing secrets.

Development verification:

- call `/health`
- run a sample report request
- inspect JSON logs
- inspect UI DOM/screenshot
- compare expected report sections

## 10. Eval Harness

KPIs:

- prompt success rate
- first-attempt success rate
- average fix iterations
- docs reference accuracy
- architecture violation rate
- human intervention time per PR
- regression bug ratio
- drift cleanup speed
- docs freshness

Scenarios live in `evals/harness_scenarios.yml` and are meant to be run monthly or after harness changes.

## 11. Merge Philosophy and Quality Gates

Short PRs are the default. Block gates: syntax, structure guard, required docs, architecture scan, tests for touched layer, secret leakage. Warn gates: low coverage in immature modules, stale non-critical references, planned debt with tracker entry.

Auto-merge is allowed only for docs-only gardening and low-risk test additions when all block gates pass. Human escalation is required for auth, external data collection, billing, deployment, quality gate relaxation, or rollback-risk changes.

Git flow:

1. create worktree from `main`
2. branch name `codex/<task-id>`
3. run request-intake planning meeting
4. create or update an active plan from meeting output before task work
5. commit only in that worktree
6. commit message format `<action>(plan-NNNN): <task>`
7. PR into `main`
8. merge after gates with `scripts/agent-task.sh main-merge-push <task-id> <action> "<task>"`
9. push `origin/main` immediately without separate approval unless the user explicitly requested a pause
10. delete branch and worktree

## 12. Entropy Control / Garbage Collection

Golden rules:

- map in `AGENTS.md`, knowledge in `docs/`, enforcement in `tools/`
- route thin, services explicit, integrations isolated
- no undocumented external source fact
- no broad PR without an exec plan
- no warning without a debt tracker entry

Weekly: move completed plans, update tech debt, fix broken links.

Monthly: update quality score, review stale docs, promote repeated review comments into architecture rules.

## 13. Starter File Pack

The starter file pack has been materialized in this repository. See the root docs, `docs/`, `scripts/`, `tools/`, and `.github/workflows/ci.yml`.

## 14. Codex Prompt Pack

Codex-only prompts live in `docs/references/codex-prompt-pack.md`.

## 15. Adoption Roadmap

Day 1:

- create file pack
- run `scripts/agent-task.sh doctor`
- make the first product spec update

Week 1:

- implement MVP report API and UI
- require exec plans for broad changes
- add first UI verification workflow

Week 2-4:

- add real source collectors
- introduce DB and generated schema docs
- tighten block gates where false positives are low

Month 2+:

- evaluate KPI trends
- automate docs gardening
- add regression evals from production bugs
- promote recurring human preferences into mechanical rules

## 16. Final Deliverables Checklist

| Deliverable | Purpose | Required | Maintainer | Trigger |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | Codex entry map | yes | human + Codex | workflow changes |
| `docs/architecture/README.md` | boundary contract | yes | Codex | architecture changes |
| `docs/` | source of record | yes | Codex | every behavior/rule change |
| `scripts/agent-task.sh` | local harness | yes | Codex | verification changes |
| `tools/*.py` | mechanical checks | yes | CI + Codex | new rule |
| `.github/workflows/ci.yml` | repeatable CI | yes | CI | gate changes |
| `docs/quality/` | review rubric | yes | human + Codex | merge policy changes |
| `evals/` | harness KPI scenarios | yes | Codex | monthly review |
| `docs/observability/` | debug/readability contracts | yes | Codex | logging/metrics changes |
| `docs/team/roster.md` | 개미군단 역할/책임 | yes | human + Codex | ownership changes |
| `docker-compose.yml` | local runtime | yes | Codex | runtime changes |

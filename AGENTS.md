# AGENTS.md

Codex 전용 작업 지침이다. 이 파일은 백과사전이 아니라 저장소 운영 지식으로 가는 지도다.

## Project

- 팀: 개미군단 (`ant-legion`)
- 제품: 간단한 아이디어를 구체화하고, 유사/경쟁 서비스를 조사해 보고서를 작성하는 웹 서비스
- 기본 스택: Vue + Vite + TailwindCSS frontend, Python FastAPI backend, PostgreSQL 18
- 로컬 실행: Docker Compose only
- 운영 원칙: 사람이 구현을 직접 많이 하기보다 Codex가 반복 가능하게 구현, 검증, 문서 갱신을 수행한다.

## Read First

1. `ARCHITECTURE.md` - 계층, 의존성, 금지 패턴
2. `docs/design-docs/core-beliefs.md` - 제품/엔지니어링 판단 기준
3. `docs/product-specs/index.md` - 제품 범위와 사용자 가치
4. `docs/exec-plans/README.md` - 큰 작업을 실행 계획으로 쪼개는 법
5. `docs/team/roster.md` - 개미군단 역할과 책임
6. `docs/references/codex-git-workflow.md` - worktree 기반 Git 운영
7. `QUALITY_SCORE.md` - 품질 점수와 병합 기준
8. `RELIABILITY.md`, `SECURITY.md`, `FRONTEND.md`, `BACKEND.md` - 영역별 규칙

## Standard Codex Loop

1. 작업 시작 리포트를 남긴다: 목표, 범위, 예상 변경 파일, 검증 계획.
2. `main`에서 직접 커밋하지 않는다. worktree로 `codex/<task-id>` 브랜치를 시작한다.
3. 작업 범위를 확인하고 관련 문서를 읽는다.
4. 큰 변경은 `docs/exec-plans/active/`에 실행 계획을 만든다.
5. 구현 전 `scripts/agent-task.sh doctor`를 실행한다.
6. 작게 구현하고 Docker 기반 테스트, 구조 검사, 문서 검사를 실행한다.
7. 변경한 동작, 규칙, 의사결정은 같은 PR에서 문서에 반영한다.
8. 완료 전 `scripts/agent-task.sh verify`와 필요한 `scripts/agent-task.sh docker-test`를 통과시킨다.
9. 작업 종료 리포트를 남긴다: 변경 요약, 검증 결과, 남은 리스크, 다음 작업.

## Hard Rules

- 에이전트가 볼 수 없는 지식은 존재하지 않는 것으로 간주한다.
- 제품/아키텍처/운영 결정은 Slack, Google Docs, 사람 기억이 아니라 이 저장소 문서에 남긴다.
- `apps/web`은 UI와 클라이언트 상태만 담당한다.
- `services/api`는 API, orchestration, domain service, repository boundary를 담당한다.
- frontend에서 DB, secret, backend 내부 모듈을 직접 참조하지 않는다.
- backend route에서 외부 API 호출, DB 쿼리, 복잡한 비즈니스 로직을 직접 작성하지 않는다.
- shared utility는 두 곳 이상에서 실제로 필요할 때만 만든다.
- 테스트나 lint를 약화시키는 변경은 실행 계획과 품질 점수 갱신 없이는 금지한다.
- `main` 브랜치 직접 커밋은 금지한다.
- feature/fix 작업은 worktree branch -> PR/main merge -> worktree/branch cleanup 흐름을 따른다.
- 로컬 DB는 PostgreSQL 18 Docker 컨테이너만 사용한다.
- 로컬 Node 런타임은 Docker 이미지 또는 Node 22를 사용한다.

## Verification

Run before final handoff:

```bash
scripts/agent-task.sh verify
```

Minimum checks:

- structure guard
- docs freshness and links
- architecture rule scan
- backend tests when backend changed
- frontend build/test when frontend changed
- Docker Compose integration checks when runtime behavior changed

## Documentation Updates

Update docs in the same change when:

- user-facing behavior changes
- architecture boundary changes
- new external integration is added
- validation, logging, security, reliability, or PR policy changes
- an exec plan is completed or abandoned

# idea-maker

버전: 0.1.0
생성일: 2026-05-03
마지막 업데이트: 2026-05-04

`idea-maker`는 짧은 아이디어를 입력하면 구체화된 제품/사업 보고서로 정리해 주는 웹 서비스다. 사용자가 막연한 아이디어를 입력하면 시스템은 구체적인 아이템 후보를 추천하고, 선택된 아이디어를 국내 경쟁 서비스와 해외 경쟁 서비스, 공개 스타트업/제품 디렉터리 참고 사례가 포함된 보고서로 정리한다.

## 핵심 가치

- 빈 캔버스 대신 바로 검토할 수 있는 구조화된 아이디어 보고서를 만든다.
- 국내 경쟁 서비스와 해외 경쟁 서비스를 분리해 시장 맥락을 비교할 수 있게 한다.
- Product Hunt, PitchWall, BetaList 같은 공개 출처는 참고 자료로 쓰되, 출처 URL, 관측일, 신뢰도 메모를 함께 남긴다.
- 로컬 Gemma4와 Gemini CLI 같은 선택적 AI/research adapter를 활용하되, 사용할 수 없을 때도 deterministic fallback으로 흐름을 완료한다.
- Codex가 반복 가능하게 구현, 검증, 문서 갱신을 수행하도록 저장소 운영 규칙을 문서와 스크립트로 관리한다.

## 주요 사용자

- 초기 아이디어를 검증하려는 1인 창업자와 인디 해커
- 제품 방향을 정리해야 하는 PM과 스타트업 팀
- 아이디어 보고서나 과제 자료를 준비하는 학생과 운영자

## 제품 흐름

1. 사용자가 자연어로 짧은 아이디어를 입력한다.
2. 첫 화면의 빠른 예시는 IT와 교육 분야만 제공하며, 로컬 Gemma4가 가능하면 매번 새 예시를 만들고 불가능하면 다양화된 fallback 예시를 보여준다.
3. 단어 또는 짧은 문장이면 시스템이 구현 가능한 아이템 후보 4개를 먼저 추천한다.
4. 사용자는 추천 아이템을 선택하거나 더 긴 아이디어를 직접 입력한다.
5. 시스템이 Q1-Q4 아이디어 intake 답변을 생성하고 Q5 사업 분야를 추론한다. 사용자는 Q5를 수정할 수 있다.
6. 선택된 추천 아이템은 Gemini CLI 검색과 로컬 Gemma4 정리 adapter를 사용할 수 있을 때 공개 출처 research 경로를 탄다.
7. 국내 경쟁 서비스, 해외 경쟁 서비스, 인접 스타트업 사례를 수집하거나 fixture 기반 참고 자료로 보강한다.
8. 개요, Q1-Q5, 구체화된 개념, 타깃 사용자, 핵심 사용 사례, 강점, 약점, 차별화 기회, 리스크, MVP 범위, 출처, research 상태, 검증 체크리스트를 포함한 보고서를 생성한다.
9. 생성된 보고서는 PostgreSQL 18에 저장되며, 히스토리 목록과 상세 화면에서 다시 열거나 삭제할 수 있다.

## 기술 구성

- 프론트엔드: Vue 3, Vite, TailwindCSS, TypeScript, Vitest
- 백엔드: Python 3.12+, FastAPI, Pydantic, pytest, Ruff
- 데이터베이스: PostgreSQL 18
- 로컬 실행: Docker Compose only
- 운영 방식: Codex worktree branch, 실행 계획, 문서 갱신, Docker 기반 검증

## 저장소 구조

- `apps/web`: Vue UI, 클라이언트 상태, API 클라이언트
- `services/api`: FastAPI route, schema, service, integration, repository boundary
- `docs`: 제품, 아키텍처, 운영, 품질, 실행 계획의 source of record
- `scripts`: Codex 작업과 검증을 위한 안정적인 명령
- `tools`: 문서 신선도, 구조, 아키텍처 규칙 검사
- `lint-rules`: 기계적으로 검사할 아키텍처 정책

## 로컬 실행과 검증

```bash
scripts/agent-task.sh doctor
scripts/agent-task.sh verify
scripts/agent-task.sh docker-test
```

개발 서버는 Docker Compose로 실행한다.

```bash
scripts/agent-task.sh docker-up
```

## 문서 운영 규칙

루트 `README.md`는 항상 한국어로 프로젝트 전체를 요약한다. 기능을 추가하거나 수정하는 모든 변경은 루트 `README.md`를 같은 변경에서 반드시 갱신한다. 그 외 프로젝트 수정도 README의 내용, `버전`, `마지막 업데이트`가 현재 상태와 맞는지 확인하고 필요한 경우 같은 변경에서 갱신한다. `버전`은 별도 제품 버전 정책이 생기기 전까지 `pyproject.toml`의 프로젝트 버전을 따른다.

## Codex 시작점

1. `AGENTS.md`
2. `RTK.md`
3. `docs/HARNESS_SYSTEM.md`
4. `docs/architecture/README.md`
5. `docs/product-specs/index.md`
6. `docs/references/codex-extensions.md`

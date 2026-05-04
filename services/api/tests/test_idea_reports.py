from random import Random
from threading import Event
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from services.api.app import services as idea_services
from services.api.app.integrations.research_adapters import (
    BusinessContextGenerationResult,
    GeneratedIdeaRecommendation,
    GeneratedQuickIdeaExample,
    IdeaRecommendationsGenerationResult,
    LocalGemmaBusinessContextGenerator,
    LocalGemmaIdeaRecommendationGenerator,
    LocalGemmaQuickIdeaExampleGenerator,
    OrganizationResult,
    QuickIdeaExamplesGenerationResult,
    SearchAdapterResult,
    business_context_generation_fallback,
    item_recommendations_generation_fallback,
    quick_idea_examples_generation_fallback,
)
from services.api.app.integrations.source_collectors import (
    NormalizedSourceRecord,
    SourceCollectorError,
    UrlFetchingSourceClient,
    clear_source_index_cache,
)
from services.api.app.main import allowed_cors_origins, app
from services.api.app.repositories.idea_reports import InMemoryIdeaReportRepository
from services.api.app.schemas import (
    IdeaRecommendationRequest,
    IdeaReportRequest,
    IdeaReportResponse,
)
from services.api.app.services import (
    QUICK_EXAMPLE_FIELDS,
    clear_ai_generation_caches,
    create_idea_recommendations,
    create_idea_report,
    create_quick_idea_examples,
    quick_idea_example_for_field,
)


@pytest.fixture(autouse=True)
def use_in_memory_report_repository():
    original_repository = app.state.idea_report_repository
    app.state.idea_report_repository = InMemoryIdeaReportRepository()
    yield
    app.state.idea_report_repository = original_repository


@pytest.fixture(autouse=True)
def clear_generation_caches():
    clear_ai_generation_caches()
    clear_source_index_cache()
    yield
    clear_ai_generation_caches()
    clear_source_index_cache()


@pytest.fixture(autouse=True)
def disable_live_business_context_generation(monkeypatch):
    def fallback_context(self, *, business_field: str) -> BusinessContextGenerationResult:
        return business_context_generation_fallback(
            business_field,
            "network disabled in deterministic API tests",
        )

    monkeypatch.setattr(LocalGemmaBusinessContextGenerator, "generate", fallback_context)

    def fallback_examples(
        self,
        *,
        fields: tuple[str, ...],
    ) -> QuickIdeaExamplesGenerationResult:
        return quick_idea_examples_generation_fallback(
            "network disabled in deterministic API tests"
        )

    monkeypatch.setattr(LocalGemmaQuickIdeaExampleGenerator, "generate", fallback_examples)

    def fallback_recommendations(
        self,
        *,
        keyword: str,
    ) -> IdeaRecommendationsGenerationResult:
        return item_recommendations_generation_fallback(
            "network disabled in deterministic API tests"
        )

    monkeypatch.setattr(
        LocalGemmaIdeaRecommendationGenerator,
        "generate",
        fallback_recommendations,
    )


def fail_live_source_fetch(self, url: str, *, timeout_seconds: float) -> object:
    raise SourceCollectorError("network disabled in deterministic API tests")


def test_create_idea_report_returns_competitor_sections(monkeypatch) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)
    client = TestClient(app)

    response = client.post(
        "/api/idea-reports",
        json={"idea": "동네 소상공인을 위한 AI 리뷰 분석 도구"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["idea"] == "동네 소상공인을 위한 AI 리뷰 분석 도구"
    assert body["locale"] == "ko-KR"
    assert body["created_at"]
    assert body["domestic_competitors"]
    assert body["overseas_competitors"]
    assert body["source_references"]
    assert "[TODO" not in body["domestic_competitors"][0]["name"]
    assert body["domestic_competitors"][0]["source_url"]
    assert body["overseas_competitors"][0]["source_url"]
    assert body["domestic_competitors"][0]["confidence"] == "low"
    assert body["source_references"][0]["observed_date"]
    assert "fixture-backed" in body["source_references"][0]["note"].lower()
    assert "AI 리뷰 분석 도구" in body["overview"]
    assert body["idea_intake_questions"][0] == {
        "code": "Q1",
        "prompt": "나의 아이디어를 한 줄로 소개해주세요.",
        "requirement": "자동 생성",
        "photo_guidance": None,
        "options": [],
        "answer": "동네 소상공인을 위한 AI 리뷰 분석 도구",
    }
    assert body["idea_intake_questions"][1]["requirement"] == "자동 생성"
    assert body["idea_intake_questions"][1]["photo_guidance"] is None
    assert body["idea_intake_questions"][1]["answer"]
    assert "동네 소상공인" in body["idea_intake_questions"][1]["answer"]
    assert "마케팅/PR" in body["idea_intake_questions"][1]["answer"]
    assert "마케팅/PR" in body["idea_intake_questions"][2]["answer"]
    assert "반응 수집" in body["idea_intake_questions"][3]["answer"]
    assert body["idea_intake_questions"][4]["prompt"] == "사업 분야를 선택해주세요."
    assert body["idea_intake_questions"][4]["answer"] == "마케팅/PR"
    assert body["idea_intake_questions"][4]["options"] == [
        "IT",
        "교육",
        "금융",
        "운영관리",
        "네트워킹",
        "농축/수산업",
        "라이프스타일",
        "마케팅/PR",
        "모빌리티",
        "미디어/엔터테인먼트",
        "바이오/의류",
        "에너지/자원",
        "유통/물류",
        "임팩트",
        "재무",
        "프롭테크",
        "하드웨어",
        "기타",
    ]
    assert "마케팅/PR" in body["clarified_concept"]
    assert any("동네 소상공인" in item for item in body["target_users"])
    assert any("마케팅/PR" in item for item in body["core_use_cases"])
    assert any("동네 소상공인" in item for item in body["strengths"])
    assert any("마케팅/PR" in item for item in body["weaknesses"])
    assert any("고객 반응" in item for item in body["differentiation_opportunities"])
    assert any("마케팅/PR" in item for item in body["key_risks"])
    assert body["build_complexity"].startswith("중간")
    assert any("반응 수집" in item for item in body["recommended_mvp_scope"])
    assert any("마케팅 담당자" in item for item in body["next_validation_steps"])
    assert body["research_status"]["requested"] is False


def test_create_idea_report_persists_intake_answers(monkeypatch) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)
    client = TestClient(app)
    answers = [{"code": "Q5", "answer": "IT"}]

    created_response = client.post(
        "/api/idea-reports",
        json={
            "idea": "동네 소상공인을 위한 AI 리뷰 분석 도구",
            "idea_intake_answers": answers,
        },
    )
    created_report = created_response.json()
    detail_response = client.get(f"/api/idea-reports/{created_report['id']}")

    assert created_response.status_code == 200
    assert detail_response.status_code == 200
    assert created_report["idea_intake_questions"][0]["answer"] == (
        "동네 소상공인을 위한 AI 리뷰 분석 도구"
    )
    assert created_report["idea_intake_questions"][4]["answer"] == "IT"
    assert detail_response.json()["idea_intake_questions"] == created_report[
        "idea_intake_questions"
    ]


@pytest.mark.parametrize(
    ("answers", "expected_message"),
    [
        (
            [
                {"code": "Q5", "answer": "IT"},
                {"code": "Q5", "answer": "교육"},
            ],
            "idea_intake_answers must not contain duplicate question codes",
        ),
        (
            [
                {"code": "Q5", "answer": "없는 분야"},
            ],
            "Q5 answer must be one of the business field options",
        ),
    ],
)
def test_create_idea_report_validates_intake_answers(
    answers,
    expected_message: str,
) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/idea-reports",
        json={
            "idea": "동네 소상공인을 위한 AI 리뷰 분석 도구",
            "idea_intake_answers": answers,
        },
    )

    assert response.status_code == 422
    assert expected_message in str(response.json()["detail"])


def test_create_idea_report_validates_short_idea() -> None:
    client = TestClient(app)

    response = client.post("/api/idea-reports", json={"idea": "짧음"})

    assert response.status_code == 422


def test_list_idea_reports_returns_saved_report_summaries(monkeypatch) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)
    client = TestClient(app)
    idea = f"보고서 목록 조회 테스트 {uuid4()}"

    created_response = client.post(
        "/api/idea-reports",
        json={"idea": idea, "idea_intake_answers": [{"code": "Q5", "answer": "교육"}]},
    )
    list_response = client.get("/api/idea-reports")

    assert created_response.status_code == 200
    assert list_response.status_code == 200
    created_report = created_response.json()
    matching_summaries = [
        report
        for report in list_response.json()["reports"]
        if report["id"] == created_report["id"]
    ]
    assert matching_summaries
    assert matching_summaries[0]["idea"] == idea
    assert matching_summaries[0]["overview"] == created_report["overview"]
    assert matching_summaries[0]["business_field"] == "교육"
    assert matching_summaries[0]["domestic_competitor_count"] > 0
    assert matching_summaries[0]["source_reference_count"] > 0


def test_delete_idea_report_removes_saved_report(monkeypatch) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)
    client = TestClient(app)
    idea = f"보고서 삭제 테스트 {uuid4()}"

    created_response = client.post("/api/idea-reports", json={"idea": idea})
    created_report = created_response.json()
    delete_response = client.delete(f"/api/idea-reports/{created_report['id']}")
    detail_response = client.get(f"/api/idea-reports/{created_report['id']}")
    list_response = client.get("/api/idea-reports")

    assert delete_response.status_code == 204
    assert detail_response.status_code == 404
    assert created_report["id"] not in [
        report["id"] for report in list_response.json()["reports"]
    ]


def test_delete_idea_report_returns_not_found_for_missing_report() -> None:
    client = TestClient(app)

    response = client.delete(f"/api/idea-reports/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "idea_report_not_found"


def test_get_idea_report_returns_saved_detail(monkeypatch) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)
    client = TestClient(app)
    idea = f"보고서 상세 조회 테스트 {uuid4()}"

    created_response = client.post("/api/idea-reports", json={"idea": idea})
    created_report = created_response.json()
    detail_response = client.get(f"/api/idea-reports/{created_report['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created_report["id"]
    assert detail_response.json()["idea"] == idea
    assert detail_response.json()["clarified_concept"] == created_report["clarified_concept"]


def test_idea_report_response_backfills_intake_questions_for_saved_payloads(
    monkeypatch,
) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)
    report = create_idea_report(
        IdeaReportRequest(idea="기존 저장 보고서 호환성 확인용 아이디어")
    )
    saved_payload = report.model_dump(mode="json")
    saved_payload.pop("idea_intake_questions")

    restored_report = IdeaReportResponse.model_validate(saved_payload)

    assert restored_report.idea_intake_questions[0].code == "Q1"
    assert restored_report.idea_intake_questions[4].options[-1] == "기타"


def test_create_idea_report_uses_ai_business_context_for_requested_field(
    monkeypatch,
) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)

    class FakeBusinessContextGenerator:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def generate(self, *, business_field: str) -> BusinessContextGenerationResult:
            self.calls.append(business_field)
            return BusinessContextGenerationResult(
                provider="gemma4",
                status="success",
                business_field=business_field,
                users=("AI 마케팅 실무자", "브랜드 성장팀", "고객 경험 담당자"),
                job="캠페인 반응을 읽고 다음 메시지를 정하는 일",
                outcome="전환율 개선과 부정 이슈 대응 시간 단축",
                adoption_risk="채널 데이터 권한과 브랜드 톤 검수",
                differentiation_focus="한국어 고객 반응에서 실행 메시지를 뽑는 흐름",
                mvp_capability="반응 수집, 감성 분류, 메시지 초안",
                notes=("fake AI context used",),
            )

    context_generator = FakeBusinessContextGenerator()

    report = create_idea_report(
        IdeaReportRequest(
            idea="브랜드 리뷰 반응을 분석해 캠페인 메시지를 추천하는 서비스",
            idea_intake_answers=[{"code": "Q5", "answer": "마케팅/PR"}],
        ),
        context_generator=context_generator,
    )

    assert context_generator.calls == ["마케팅/PR"]
    assert "AI 마케팅 실무자" in report.target_users[0]
    assert "캠페인 반응" in report.core_use_cases[1]
    assert "전환율 개선" in report.differentiation_opportunities[2]
    assert report.recommended_mvp_scope[0] == "반응 수집, 감성 분류, 메시지 초안"


def test_create_idea_report_reuses_cached_default_ai_business_context(
    monkeypatch,
) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)
    calls: list[str] = []

    def successful_context(
        self,
        *,
        business_field: str,
    ) -> BusinessContextGenerationResult:
        calls.append(business_field)
        return BusinessContextGenerationResult(
            provider="gemma4",
            status="success",
            business_field=business_field,
            users=("AI 제품팀", "데이터 운영자", "자동화 담당자"),
            job="반복 업무 흐름을 읽고 다음 행동을 정하는 일",
            outcome="처리 시간 감소",
            adoption_risk="데이터 권한과 결과 검수",
            differentiation_focus="한국어 업무 맥락에 맞춘 자동화",
            mvp_capability="업무 입력, 분류, 알림",
            notes=("fake cached context",),
        )

    monkeypatch.setattr(
        LocalGemmaBusinessContextGenerator,
        "generate",
        successful_context,
    )

    for _ in range(2):
        report = create_idea_report(
            IdeaReportRequest(
                idea="AI 업무 요청을 분류하고 담당자에게 알리는 서비스",
                idea_intake_answers=[{"code": "Q5", "answer": "IT"}],
            ),
        )
        assert report.idea_intake_questions[4].answer == "IT"

    assert calls == ["IT"]


def test_create_idea_report_does_not_call_ai_context_for_other_fields(
    monkeypatch,
) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)

    class FailingBusinessContextGenerator:
        def generate(self, *, business_field: str) -> BusinessContextGenerationResult:
            raise AssertionError(f"unexpected AI context call for {business_field}")

    report = create_idea_report(
        IdeaReportRequest(
            idea="매장 체크리스트와 교대 업무를 관리하는 서비스",
            idea_intake_answers=[{"code": "Q5", "answer": "운영관리"}],
        ),
        context_generator=FailingBusinessContextGenerator(),
    )

    assert report.idea_intake_questions[4].answer == "운영관리"
    assert any("현장 운영 매니저" in item for item in report.target_users)


def test_create_idea_report_falls_back_when_ai_context_generation_fails(
    monkeypatch,
) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)

    class FallbackBusinessContextGenerator:
        def generate(self, *, business_field: str) -> BusinessContextGenerationResult:
            return business_context_generation_fallback(
                business_field,
                "fake AI context failure",
            )

    report = create_idea_report(
        IdeaReportRequest(
            idea="생활 루틴을 추천하는 라이프스타일 앱",
            idea_intake_answers=[{"code": "Q5", "answer": "라이프스타일"}],
        ),
        context_generator=FallbackBusinessContextGenerator(),
    )

    assert any("개인 생활 루틴" in item for item in report.target_users)
    assert any("루틴 입력" in item for item in report.recommended_mvp_scope)


def test_get_idea_report_returns_not_found_for_missing_report() -> None:
    client = TestClient(app)

    response = client.get(f"/api/idea-reports/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "idea_report_not_found"


def test_get_quick_idea_examples_returns_five_business_field_examples() -> None:
    client = TestClient(app)

    response = client.get("/api/quick-idea-examples")

    assert response.status_code == 200
    body = response.json()
    assert len(body["examples"]) == 5
    assert len({example["field"] for example in body["examples"]}) == 5
    assert all(example["field"] in QUICK_EXAMPLE_FIELDS for example in body["examples"])
    assert all(example["idea"] for example in body["examples"])


def test_get_quick_idea_examples_limits_fields_to_supported_ai_contexts() -> None:
    client = TestClient(app)

    response = client.get("/api/quick-idea-examples?count=10")

    assert response.status_code == 200
    body = response.json()
    assert len(body["examples"]) == len(QUICK_EXAMPLE_FIELDS)
    assert {example["field"] for example in body["examples"]} == set(
        QUICK_EXAMPLE_FIELDS
    )


def test_create_quick_idea_examples_randomizes_generated_output() -> None:
    first_response = create_quick_idea_examples(random_source=Random(1))
    second_response = create_quick_idea_examples(random_source=Random(2))

    assert len(first_response.examples) == 5
    assert len(second_response.examples) == 5
    assert first_response.examples != second_response.examples


def test_create_quick_idea_examples_uses_ai_generated_output() -> None:
    class FakeQuickIdeaExampleGenerator:
        def generate(
            self,
            *,
            fields: tuple[str, ...],
        ) -> QuickIdeaExamplesGenerationResult:
            return QuickIdeaExamplesGenerationResult(
                provider="gemma4",
                status="success",
                examples=tuple(
                    GeneratedQuickIdeaExample(
                        field=field,
                        idea=f"{field} 분야 사용자가 반복 문제를 해결하는 AI 생성 예시",
                    )
                    for field in fields
                ),
                notes=("fake AI quick examples used",),
            )

    response = create_quick_idea_examples(
        count=3,
        random_source=Random(3),
        example_generator=FakeQuickIdeaExampleGenerator(),
    )

    assert len(response.examples) == 3
    assert all("AI 생성 예시" in example.idea for example in response.examples)


def test_create_quick_idea_examples_reuses_cached_default_ai_output(
    monkeypatch,
) -> None:
    calls: list[tuple[str, ...]] = []

    def successful_examples(
        self,
        *,
        fields: tuple[str, ...],
    ) -> QuickIdeaExamplesGenerationResult:
        calls.append(fields)
        return QuickIdeaExamplesGenerationResult(
            provider="gemma4",
            status="success",
            examples=tuple(
                GeneratedQuickIdeaExample(
                    field=field,
                    idea=f"{field} 분야 사용자를 위한 캐시된 AI 예시",
                )
                for field in fields
            ),
            notes=("fake cached examples",),
        )

    monkeypatch.setattr(
        LocalGemmaQuickIdeaExampleGenerator,
        "generate",
        successful_examples,
    )

    first_response = create_quick_idea_examples(count=3, random_source=Random(3))
    second_response = create_quick_idea_examples(count=3, random_source=Random(3))

    assert first_response == second_response
    assert calls == [tuple(example.field for example in first_response.examples)]


def test_quick_idea_example_uses_ai_business_context_for_requested_field() -> None:
    class FakeBusinessContextGenerator:
        def generate(self, *, business_field: str) -> BusinessContextGenerationResult:
            assert business_field == "IT"
            return BusinessContextGenerationResult(
                provider="gemma4",
                status="success",
                business_field=business_field,
                users=("AI 기반 제품팀", "데이터 운영자", "사내 자동화 담당자"),
                job="AI 업무 흐름을 설계하고 오류를 줄이는 일",
                outcome="반복 처리 시간 감소",
                adoption_risk="사내 데이터 보안과 모델 품질 검수",
                differentiation_focus="업무 맥락에 맞춘 AI 실행 흐름",
                mvp_capability="AI 태스크 큐와 결과 검수 화면",
                notes=("fake AI context used",),
            )

    example = quick_idea_example_for_field(
        "IT",
        Random(0),
        context_generator=FakeBusinessContextGenerator(),
    )

    assert example.field == "IT"
    assert "AI" in example.idea


def test_create_idea_recommendations_returns_related_items() -> None:
    client = TestClient(app)

    response = client.post("/api/idea-recommendations", json={"keyword": "리뷰"})

    assert response.status_code == 200
    body = response.json()
    assert body["keyword"] == "리뷰"
    assert len(body["recommendations"]) == 4
    assert len({recommendation["title"] for recommendation in body["recommendations"]}) == 4
    assert all(
        "리뷰" in " ".join(
            (
                recommendation["title"],
                recommendation["summary"],
                recommendation["rationale"],
                recommendation["report_seed"],
            )
        )
        for recommendation in body["recommendations"]
    )
    assert len(body["recommendations"][0]["report_seed"]) >= 5
    assert body["recommendations"][0]["rationale"]


def test_create_idea_recommendations_uses_ai_generated_output() -> None:
    class FakeRecommendationGenerator:
        def generate(self, *, keyword: str) -> IdeaRecommendationsGenerationResult:
            assert keyword == "반려동물 산책"
            return IdeaRecommendationsGenerationResult(
                provider="gemma4",
                status="success",
                recommendations=(
                    GeneratedIdeaRecommendation(
                        title="반려동물 산책 매칭",
                        summary="바쁜 보호자와 검증된 산책 파트너를 연결하는 예약 서비스",
                        rationale="입력어의 산책 문제를 즉시 실행 가능한 매칭 MVP로 좁힙니다.",
                        report_seed=(
                            "반려동물 산책이 어려운 보호자에게 검증된 산책 "
                            "파트너를 연결하는 서비스"
                        ),
                    ),
                    GeneratedIdeaRecommendation(
                        title="반려동물 산책 루틴 코치",
                        summary="산책 기록과 날씨를 바탕으로 다음 산책 루틴을 추천하는 앱",
                        rationale="반복 행동을 기록하면 보호자 유지율을 검증하기 쉽습니다.",
                        report_seed=(
                            "반려동물 산책 기록을 분석해 보호자에게 맞춤 "
                            "루틴을 추천하는 앱"
                        ),
                    ),
                    GeneratedIdeaRecommendation(
                        title="반려동물 산책 안전 리포트",
                        summary="산책 경로의 위험 메모와 체크인을 공유하는 동네 안전 도구",
                        rationale="안전 문제는 작은 지역 커뮤니티 MVP로 검증할 수 있습니다.",
                        report_seed=(
                            "반려동물 산책 경로의 위험 요소와 체크인을 "
                            "공유하는 안전 리포트 도구"
                        ),
                    ),
                    GeneratedIdeaRecommendation(
                        title="반려동물 산책 미션 구독",
                        summary="보호자에게 짧은 산책 미션과 보상 기록을 제공하는 구독 앱",
                        rationale="재미와 기록을 결합하면 생활 루틴 서비스로 확장할 수 있습니다.",
                        report_seed="반려동물 산책 습관을 짧은 미션과 보상 기록으로 돕는 구독 앱",
                    ),
                ),
                notes=("fake AI recommendations used",),
            )

    response = create_idea_recommendations(
        IdeaRecommendationRequest(keyword="반려동물 산책"),
        recommendation_generator=FakeRecommendationGenerator(),
    )

    assert response.keyword == "반려동물 산책"
    assert response.recommendations[0].title == "반려동물 산책 매칭"
    assert "검증된 산책 파트너" in response.recommendations[0].report_seed


def test_create_idea_recommendations_reuses_cached_default_ai_output(
    monkeypatch,
) -> None:
    calls: list[str] = []

    def successful_recommendations(
        self,
        *,
        keyword: str,
    ) -> IdeaRecommendationsGenerationResult:
        calls.append(keyword)
        return IdeaRecommendationsGenerationResult(
            provider="gemma4",
            status="success",
            recommendations=(
                GeneratedIdeaRecommendation(
                    title="반려동물 산책 매칭",
                    summary="바쁜 보호자와 산책 파트너를 연결하는 예약 서비스",
                    rationale="입력어의 산책 문제를 매칭 MVP로 좁힙니다.",
                    report_seed="반려동물 산책이 어려운 보호자를 위한 매칭 서비스",
                ),
                GeneratedIdeaRecommendation(
                    title="반려동물 산책 루틴 코치",
                    summary="산책 기록을 바탕으로 다음 루틴을 추천하는 앱",
                    rationale="반복 산책 행동을 기록해 유지율을 확인합니다.",
                    report_seed="반려동물 산책 기록을 분석해 맞춤 루틴을 추천하는 앱",
                ),
                GeneratedIdeaRecommendation(
                    title="반려동물 산책 안전 리포트",
                    summary="산책 경로의 위험 메모를 공유하는 동네 안전 도구",
                    rationale="산책 안전 문제를 지역 단위로 검증합니다.",
                    report_seed="반려동물 산책 경로의 위험 요소를 공유하는 안전 도구",
                ),
                GeneratedIdeaRecommendation(
                    title="반려동물 산책 미션 구독",
                    summary="짧은 산책 미션과 보상 기록을 제공하는 구독 앱",
                    rationale="산책 습관을 생활 루틴 서비스로 확장합니다.",
                    report_seed="반려동물 산책 습관을 미션과 보상 기록으로 돕는 앱",
                ),
            ),
            notes=("fake cached recommendations",),
        )

    monkeypatch.setattr(
        LocalGemmaIdeaRecommendationGenerator,
        "generate",
        successful_recommendations,
    )

    first_response = create_idea_recommendations(
        IdeaRecommendationRequest(keyword="반려동물 산책")
    )
    second_response = create_idea_recommendations(
        IdeaRecommendationRequest(keyword="반려동물 산책")
    )

    assert first_response == second_response
    assert calls == ["반려동물 산책"]


def test_create_idea_recommendations_fallback_varies_by_input() -> None:
    review_response = create_idea_recommendations(IdeaRecommendationRequest(keyword="리뷰"))
    learning_response = create_idea_recommendations(IdeaRecommendationRequest(keyword="학습"))

    assert [item.title for item in review_response.recommendations] != [
        item.title for item in learning_response.recommendations
    ]
    assert any("고객 반응" in item.title for item in review_response.recommendations)
    assert any("학습 루틴" in item.title for item in learning_response.recommendations)


def test_create_idea_recommendations_accepts_short_sentence() -> None:
    client = TestClient(app)

    response = client.post("/api/idea-recommendations", json={"keyword": "리뷰 분석"})

    assert response.status_code == 200
    assert response.json()["keyword"] == "리뷰 분석"


def test_create_idea_recommendations_requires_concise_input() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/idea-recommendations",
        json={
            "keyword": (
                "너무 긴 입력은 추천 전에 더 명확한 문장으로 다듬어야 하므로 "
                "바로 보고서 생성 대상으로 취급합니다"
            )
        },
    )

    assert response.status_code == 422


def test_create_researched_idea_report_uses_search_and_organization_adapters() -> None:
    class FakeSearchAdapter:
        def search(self, *, idea: str, observed_date) -> SearchAdapterResult:
            return SearchAdapterResult(
                provider="gemini_cli",
                status="success",
                records=(
                    NormalizedSourceRecord(
                        title="ReviewPulse",
                        url="https://example.com/reviewpulse",
                        market="overseas",
                        category="test search result",
                        summary=f"{idea} related live-search candidate.",
                        strengths=("Fresh search lead",),
                        weaknesses=("Needs manual verification",),
                        observed_date=observed_date,
                        confidence="medium",
                        source_name="Gemini CLI search",
                        access_method="live_http",
                    ),
                ),
                notes=("fake gemini search used",),
            )

    class FakeOrganizer:
        def organize(self, *, idea: str, records: list[NormalizedSourceRecord]):
            return OrganizationResult(
                provider="gemma4",
                status="success",
                summary=f"{idea} organized with {len(records)} records.",
                target_users=("리뷰 담당 운영자",),
                core_use_cases=("리뷰 이슈를 모아 우선순위를 정한다.",),
                opportunities=("리뷰 기반 개선 루프를 자동화한다.",),
                risks=("검색 결과 사실 확인이 필요하다.",),
                mvp_scope=("리뷰 수집과 이슈 분류",),
                notes=("fake gemma organizer used",),
            )

    report = create_idea_report(
        IdeaReportRequest(
            idea="리뷰 고객 반응 분석 도구",
            research=True,
        ),
        search_adapter=FakeSearchAdapter(),
        organizer=FakeOrganizer(),
    )

    assert report.research_status.requested is True
    assert report.research_status.search_provider == "gemini_cli"
    assert report.research_status.organization_provider == "gemma4"
    assert "fake gemini search used" in report.research_status.notes
    assert "ReviewPulse" in [competitor.name for competitor in report.overseas_competitors]
    assert report.target_users == ["리뷰 담당 운영자"]
    assert report.core_use_cases == ["리뷰 이슈를 모아 우선순위를 정한다."]
    assert "리뷰 담당 운영자" in report.idea_intake_questions[1].answer
    assert "리뷰 담당 운영자" in report.idea_intake_questions[2].answer
    assert "고객 반응" in " ".join(report.strengths)


def test_researched_idea_report_starts_source_collection_and_search_in_parallel(
    monkeypatch,
) -> None:
    source_started = Event()
    search_started = Event()

    def fake_collect_source_records(*, idea: str, observed_date) -> list[NormalizedSourceRecord]:
        assert idea == "리뷰 고객 반응 분석 도구"
        source_started.set()
        assert search_started.wait(timeout=1)
        return []

    class FakeSearchAdapter:
        def search(self, *, idea: str, observed_date) -> SearchAdapterResult:
            assert source_started.wait(timeout=1)
            search_started.set()
            return SearchAdapterResult(
                provider="gemini_cli",
                status="success",
                records=(),
                notes=("fake parallel search used",),
            )

    class FakeOrganizer:
        def organize(self, *, idea: str, records: list[NormalizedSourceRecord]):
            return OrganizationResult(
                provider="gemma4",
                status="success",
                summary=f"{idea} organized after parallel collection.",
                target_users=("리뷰 담당 운영자",),
                core_use_cases=("리뷰 이슈를 모아 우선순위를 정한다.",),
                opportunities=("리뷰 기반 개선 루프를 자동화한다.",),
                risks=("검색 결과 사실 확인이 필요하다.",),
                mvp_scope=("리뷰 수집과 이슈 분류",),
                notes=("fake gemma organizer used",),
            )

    monkeypatch.setattr(
        idea_services,
        "collect_source_records",
        fake_collect_source_records,
    )

    report = create_idea_report(
        IdeaReportRequest(
            idea="리뷰 고객 반응 분석 도구",
            research=True,
        ),
        search_adapter=FakeSearchAdapter(),
        organizer=FakeOrganizer(),
    )

    assert report.research_status.search_status == "success"
    assert source_started.is_set()
    assert search_started.is_set()


def test_idea_report_cors_allows_local_web_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/idea-reports",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_cors_origins_include_configured_web_port() -> None:
    origins = allowed_cors_origins({"WEB_PORT": "15173"})

    assert "http://127.0.0.1:15173" in origins
    assert "http://localhost:15173" in origins

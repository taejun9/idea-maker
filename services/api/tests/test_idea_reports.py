from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from services.api.app.integrations.research_adapters import (
    OrganizationResult,
    SearchAdapterResult,
)
from services.api.app.integrations.source_collectors import (
    NormalizedSourceRecord,
    SourceCollectorError,
    UrlFetchingSourceClient,
)
from services.api.app.main import allowed_cors_origins, app
from services.api.app.repositories.idea_reports import InMemoryIdeaReportRepository
from services.api.app.schemas import IdeaReportRequest, IdeaReportResponse
from services.api.app.services import create_idea_report


@pytest.fixture(autouse=True)
def use_in_memory_report_repository():
    original_repository = app.state.idea_report_repository
    app.state.idea_report_repository = InMemoryIdeaReportRepository()
    yield
    app.state.idea_report_repository = original_repository


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
        "requirement": "필수, 최소 10자 이상 입력해주세요.",
        "photo_guidance": None,
        "options": [],
    }
    assert body["idea_intake_questions"][1]["photo_guidance"].startswith(
        "사진은 드래그앤드랍"
    )
    assert body["idea_intake_questions"][4]["prompt"] == "사업 분야를 선택해주세요."
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
    assert "SaaS" in body["clarified_concept"]
    assert body["core_use_cases"]
    assert body["differentiation_opportunities"]
    assert body["key_risks"]
    assert body["build_complexity"].startswith("중간")
    assert body["recommended_mvp_scope"]
    assert body["research_status"]["requested"] is False


def test_create_idea_report_validates_short_idea() -> None:
    client = TestClient(app)

    response = client.post("/api/idea-reports", json={"idea": "짧음"})

    assert response.status_code == 422


def test_list_idea_reports_returns_saved_report_summaries(monkeypatch) -> None:
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", fail_live_source_fetch)
    client = TestClient(app)
    idea = f"보고서 목록 조회 테스트 {uuid4()}"

    created_response = client.post("/api/idea-reports", json={"idea": idea})
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
    assert matching_summaries[0]["domestic_competitor_count"] > 0
    assert matching_summaries[0]["source_reference_count"] > 0


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


def test_get_idea_report_returns_not_found_for_missing_report() -> None:
    client = TestClient(app)

    response = client.get(f"/api/idea-reports/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"]["error_code"] == "idea_report_not_found"


def test_create_idea_recommendations_returns_related_items() -> None:
    client = TestClient(app)

    response = client.post("/api/idea-recommendations", json={"keyword": "리뷰"})

    assert response.status_code == 200
    body = response.json()
    assert body["keyword"] == "리뷰"
    assert len(body["recommendations"]) == 4
    assert body["recommendations"][0]["title"] == "리뷰 고객 반응 분석 도구"
    assert "리뷰" in body["recommendations"][0]["report_seed"]
    assert len(body["recommendations"][0]["report_seed"]) >= 5
    assert body["recommendations"][0]["rationale"]


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

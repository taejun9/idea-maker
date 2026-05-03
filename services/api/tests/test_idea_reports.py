from fastapi.testclient import TestClient

from services.api.app.integrations.source_collectors import (
    SourceCollectorError,
    UrlFetchingSourceClient,
)
from services.api.app.main import allowed_cors_origins, app


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
    assert "SaaS" in body["clarified_concept"]
    assert body["core_use_cases"]
    assert body["differentiation_opportunities"]
    assert body["key_risks"]
    assert body["build_complexity"].startswith("중간")
    assert body["recommended_mvp_scope"]


def test_create_idea_report_validates_short_idea() -> None:
    client = TestClient(app)

    response = client.post("/api/idea-reports", json={"idea": "짧음"})

    assert response.status_code == 422


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


def test_create_idea_recommendations_requires_single_keyword() -> None:
    client = TestClient(app)

    response = client.post("/api/idea-recommendations", json={"keyword": "리뷰 분석"})

    assert response.status_code == 422


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

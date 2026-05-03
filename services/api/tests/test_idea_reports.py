from fastapi.testclient import TestClient

from services.api.app.main import app


def test_create_idea_report_returns_competitor_sections() -> None:
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


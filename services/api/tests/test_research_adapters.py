import json

from services.api.app.integrations import research_adapters
from services.api.app.integrations.research_adapters import (
    LocalGemmaBusinessContextGenerator,
)


class FakeUrlResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self, limit: int) -> bytes:
        assert limit > 0
        return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")


def test_local_gemma_business_context_generator_parses_context_payload(monkeypatch):
    requested_urls: list[str] = []

    def fake_urlopen(request, *, timeout: float):
        requested_urls.append(request.full_url)
        assert timeout == 0.25
        return FakeUrlResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "users": ["학습자", "강사", "교육 운영자"],
                                    "job": "학습 상태를 해석해 다음 행동을 정하는 일",
                                    "outcome": "학습 지속률 개선",
                                    "adoption_risk": "학습 데이터 품질과 보호자 설득",
                                    "differentiation_focus": "개인별 학습 루틴 추천",
                                    "mvp_capability": "오답 기록과 다음 학습 추천",
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(research_adapters, "urlopen", fake_urlopen)

    result = LocalGemmaBusinessContextGenerator(
        base_url="http://gemma.local",
        model="gemma-test",
        timeout_seconds=0.25,
    ).generate(business_field="교육")

    assert requested_urls == ["http://gemma.local/v1/chat/completions"]
    assert result.provider == "gemma4"
    assert result.status == "success"
    assert result.business_field == "교육"
    assert result.users == ("학습자", "강사", "교육 운영자")
    assert result.mvp_capability == "오답 기록과 다음 학습 추천"


def test_local_gemma_business_context_generator_falls_back_on_invalid_payload(
    monkeypatch,
):
    def fake_urlopen(request, *, timeout: float):
        return FakeUrlResponse({"choices": [{"message": {"content": "{}"}}]})

    monkeypatch.setattr(research_adapters, "urlopen", fake_urlopen)

    result = LocalGemmaBusinessContextGenerator(
        base_url="http://gemma.local",
        timeout_seconds=0.25,
    ).generate(business_field="IT")

    assert result.provider == "fallback"
    assert result.status == "fallback"
    assert result.business_field == "IT"
    assert "not valid JSON" in result.notes[0]

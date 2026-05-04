import json

from services.api.app.integrations import research_adapters
from services.api.app.integrations.research_adapters import (
    LocalGemmaBusinessContextGenerator,
    LocalGemmaIdeaRecommendationGenerator,
    LocalGemmaQuickIdeaExampleGenerator,
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
    requested_bodies: list[dict[str, object]] = []

    def fake_urlopen(request, *, timeout: float):
        requested_urls.append(request.full_url)
        requested_bodies.append(json.loads(request.data.decode("utf-8")))
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
    assert requested_bodies[0]["chat_template_kwargs"] == {"enable_thinking": False}


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


def test_local_gemma_quick_idea_example_generator_parses_examples_payload(
    monkeypatch,
):
    requested_urls: list[str] = []
    requested_bodies: list[dict[str, object]] = []

    def fake_urlopen(request, *, timeout: float):
        requested_urls.append(request.full_url)
        requested_bodies.append(json.loads(request.data.decode("utf-8")))
        assert timeout == 0.5
        return FakeUrlResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "examples": [
                                        {
                                            "field": "IT",
                                            "idea": (
                                                "사내 운영팀이 반복 승인 업무를 자동화하는 "
                                                "AI 워크플로우 도구"
                                            ),
                                        },
                                        {
                                            "field": "교육",
                                            "idea": (
                                                "초등 학습자가 오답 습관을 고치는 "
                                                "개인 맞춤 복습 앱"
                                            ),
                                        },
                                    ]
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(research_adapters, "urlopen", fake_urlopen)

    result = LocalGemmaQuickIdeaExampleGenerator(
        base_url="http://gemma.local",
        model="gemma-test",
        timeout_seconds=0.5,
    ).generate(fields=("IT", "교육"))

    assert requested_urls == ["http://gemma.local/v1/chat/completions"]
    assert result.provider == "gemma4"
    assert result.status == "success"
    assert [example.field for example in result.examples] == ["IT", "교육"]
    assert result.examples[0].idea.startswith("사내 운영팀")
    assert requested_bodies[0]["chat_template_kwargs"] == {"enable_thinking": False}


def test_local_gemma_quick_idea_example_generator_falls_back_on_field_mismatch(
    monkeypatch,
):
    def fake_urlopen(request, *, timeout: float):
        return FakeUrlResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "examples": [
                                        {
                                            "field": "IT",
                                            "idea": (
                                                "사내 운영팀이 반복 승인 업무를 자동화하는 "
                                                "AI 워크플로우 도구"
                                            ),
                                        }
                                    ]
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(research_adapters, "urlopen", fake_urlopen)

    result = LocalGemmaQuickIdeaExampleGenerator(
        base_url="http://gemma.local",
        timeout_seconds=0.5,
    ).generate(fields=("IT", "교육"))

    assert result.provider == "fallback"
    assert result.status == "fallback"
    assert "fields mismatch" in result.notes[0]


def test_local_gemma_idea_recommendation_generator_parses_recommendations_payload(
    monkeypatch,
):
    requested_bodies: list[dict[str, object]] = []

    def fake_urlopen(request, *, timeout: float):
        requested_bodies.append(json.loads(request.data.decode("utf-8")))
        assert timeout == 0.75
        return FakeUrlResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "recommendations": [
                                        {
                                            "title": "반려동물 산책 매칭",
                                            "summary": (
                                                "바쁜 보호자와 검증된 산책 파트너를 "
                                                "연결하는 예약 서비스"
                                            ),
                                            "rationale": (
                                                "입력어의 산책 문제를 즉시 실행 가능한 "
                                                "매칭 MVP로 좁힙니다."
                                            ),
                                            "report_seed": (
                                                "반려동물 산책이 어려운 보호자에게 "
                                                "검증된 산책 파트너를 연결하는 서비스"
                                            ),
                                        },
                                        {
                                            "title": "반려동물 산책 루틴 코치",
                                            "summary": (
                                                "산책 기록과 날씨를 바탕으로 다음 "
                                                "산책 루틴을 추천하는 앱"
                                            ),
                                            "rationale": (
                                                "반복 행동을 기록하면 보호자 유지율을 "
                                                "검증하기 쉽습니다."
                                            ),
                                            "report_seed": (
                                                "반려동물 산책 기록을 분석해 보호자에게 "
                                                "맞춤 루틴을 추천하는 앱"
                                            ),
                                        },
                                        {
                                            "title": "반려동물 산책 안전 리포트",
                                            "summary": (
                                                "산책 경로의 위험 메모와 체크인을 "
                                                "공유하는 동네 안전 도구"
                                            ),
                                            "rationale": (
                                                "안전 문제는 작은 지역 커뮤니티 MVP로 "
                                                "검증할 수 있습니다."
                                            ),
                                            "report_seed": (
                                                "반려동물 산책 경로의 위험 요소와 "
                                                "체크인을 공유하는 안전 리포트 도구"
                                            ),
                                        },
                                        {
                                            "title": "반려동물 산책 미션 구독",
                                            "summary": (
                                                "보호자에게 짧은 산책 미션과 보상 "
                                                "기록을 제공하는 구독 앱"
                                            ),
                                            "rationale": (
                                                "재미와 기록을 결합하면 생활 루틴 "
                                                "서비스로 확장할 수 있습니다."
                                            ),
                                            "report_seed": (
                                                "반려동물 산책 습관을 짧은 미션과 "
                                                "보상 기록으로 돕는 구독 앱"
                                            ),
                                        },
                                    ]
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(research_adapters, "urlopen", fake_urlopen)

    result = LocalGemmaIdeaRecommendationGenerator(
        base_url="http://gemma.local",
        model="gemma-test",
        timeout_seconds=0.75,
    ).generate(keyword="반려동물 산책")

    assert result.provider == "gemma4"
    assert result.status == "success"
    assert [item.title for item in result.recommendations] == [
        "반려동물 산책 매칭",
        "반려동물 산책 루틴 코치",
        "반려동물 산책 안전 리포트",
        "반려동물 산책 미션 구독",
    ]
    assert "반려동물 산책" in requested_bodies[0]["messages"][1]["content"]
    assert requested_bodies[0]["chat_template_kwargs"] == {"enable_thinking": False}


def test_local_gemma_idea_recommendation_generator_falls_back_on_generic_payload(
    monkeypatch,
):
    def fake_urlopen(request, *, timeout: float):
        return FakeUrlResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "recommendations": [
                                        {
                                            "title": f"일반 추천 {index}",
                                            "summary": (
                                                "아무 입력과도 연결되지 않는 "
                                                "일반 추천입니다."
                                            ),
                                            "rationale": (
                                                "사용자 입력과 연결되지 않아 "
                                                "거부되어야 합니다."
                                            ),
                                            "report_seed": f"일반적인 SaaS 추천 아이디어 {index}",
                                        }
                                        for index in range(4)
                                    ]
                                },
                                ensure_ascii=False,
                            )
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(research_adapters, "urlopen", fake_urlopen)

    result = LocalGemmaIdeaRecommendationGenerator(
        base_url="http://gemma.local",
        timeout_seconds=0.75,
    ).generate(keyword="반려동물 산책")

    assert result.provider == "fallback"
    assert result.status == "fallback"
    assert "not tied to keyword" in result.notes[0]

from datetime import UTC, datetime

from services.api.app.schemas import (
    Competitor,
    IdeaReportRequest,
    IdeaReportResponse,
    SourceReference,
)


def create_placeholder_report(payload: IdeaReportRequest) -> IdeaReportResponse:
    """Return deterministic MVP output until real source collectors are implemented."""
    observed = datetime.now(tz=UTC).date()
    normalized_idea = payload.idea.strip()

    return IdeaReportResponse(
        overview=f"'{normalized_idea}' 아이디어를 초기 검증 가능한 제품 개념으로 구체화합니다.",
        target_users=["초기 창업자", "소규모 제품팀", "시장 조사가 필요한 기획자"],
        strengths=["짧은 입력으로 구조화된 보고서를 생성", "국내/해외 경쟁 구도를 분리"],
        weaknesses=["초기 버전은 외부 소스 실시간 수집이 제한적", "정성 판단은 추가 검증 필요"],
        domestic_competitors=[
            Competitor(
                name="[TODO 국내 경쟁사]",
                market="domestic_kr",
                summary="국내 경쟁사는 실제 source collector 도입 후 채운다.",
                strengths=["현지 시장 이해"],
                weaknesses=["현재는 placeholder"],
                observed_date=observed,
                confidence="low",
            )
        ],
        overseas_competitors=[
            Competitor(
                name="[TODO overseas competitor]",
                market="overseas",
                summary="해외 경쟁사는 Product Hunt, PitchWall, BetaList 등으로 보강한다.",
                strengths=["글로벌 reference 확보"],
                weaknesses=["현재는 placeholder"],
                observed_date=observed,
                confidence="low",
            )
        ],
        source_references=[
            SourceReference(
                source_name="Product Hunt",
                source_url="https://www.producthunt.com/",
                observed_date=observed,
                note="Current facts require browsing or an approved collector before use.",
                confidence="low",
            ),
            SourceReference(
                source_name="PitchWall",
                source_url="https://pitchwall.co/",
                observed_date=observed,
                note="Current facts require browsing or an approved collector before use.",
                confidence="low",
            ),
            SourceReference(
                source_name="BetaList",
                source_url="https://betalist.com/",
                observed_date=observed,
                note="Current facts require browsing or an approved collector before use.",
                confidence="low",
            ),
        ],
        next_validation_steps=[
            "핵심 사용자 5명을 인터뷰한다.",
            "국내/해외 경쟁사 각각 5개 이상을 최신 source로 확인한다.",
            "가장 작은 MVP 기능 1개를 정의한다.",
        ],
    )


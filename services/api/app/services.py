from datetime import UTC, datetime

from services.api.app.integrations.source_collectors import (
    Market,
    NormalizedSourceRecord,
    collect_source_records,
)
from services.api.app.schemas import (
    Competitor,
    IdeaReportRequest,
    IdeaReportResponse,
    SourceReference,
)


def create_idea_report(payload: IdeaReportRequest) -> IdeaReportResponse:
    observed = datetime.now(tz=UTC).date()
    normalized_idea = payload.idea.strip()
    source_records = collect_source_records(idea=normalized_idea, observed_date=observed)

    return IdeaReportResponse(
        overview=f"'{normalized_idea}' 아이디어를 초기 검증 가능한 제품 개념으로 구체화합니다.",
        target_users=["초기 창업자", "소규모 제품팀", "시장 조사가 필요한 기획자"],
        strengths=["짧은 입력으로 구조화된 보고서를 생성", "국내/해외 경쟁 구도를 분리"],
        weaknesses=[
            "외부 소스는 fixture-backed collector stub로 시작",
            "정성 판단은 추가 검증 필요",
        ],
        domestic_competitors=competitors_for_market(source_records, "domestic_kr"),
        overseas_competitors=competitors_for_market(source_records, "overseas"),
        source_references=source_references_from_records(source_records),
        next_validation_steps=[
            "핵심 사용자 5명을 인터뷰한다.",
            "국내/해외 경쟁사 각각 5개 이상을 최신 source로 확인한다.",
            "가장 작은 MVP 기능 1개를 정의한다.",
        ],
    )


def competitors_for_market(
    records: list[NormalizedSourceRecord], market: Market
) -> list[Competitor]:
    return [
        Competitor(
            name=record.title,
            market=record.market,
            summary=record.summary,
            strengths=list(record.strengths),
            weaknesses=list(record.weaknesses),
            source_url=record.url,
            observed_date=record.observed_date,
            confidence=record.confidence,
        )
        for record in records
        if record.market == market
    ]


def source_references_from_records(records: list[NormalizedSourceRecord]) -> list[SourceReference]:
    references: dict[str, SourceReference] = {}
    for record in records:
        references[record.source_name] = SourceReference(
            source_name=record.source_name,
            source_url=record.url,
            observed_date=record.observed_date,
            note=(
                f"{record.category} collector record. "
                "Fixture-backed data is for deterministic workflow validation; "
                "verify current facts before external claims."
            ),
            confidence=record.confidence,
        )
    return list(references.values())

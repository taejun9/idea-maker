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
        clarified_concept=(
            f"{normalized_idea}를 특정 고객군의 반복 업무를 줄이는 문제-해결형 "
            "SaaS 또는 운영 도구로 정의합니다."
        ),
        target_users=["초기 창업자", "소규모 제품팀", "시장 조사가 필요한 기획자"],
        core_use_cases=[
            "짧은 아이디어를 입력해 검증 가능한 제품 콘셉트로 정리한다.",
            "국내/해외 유사 서비스를 나눠 보고 포지셔닝 빈틈을 찾는다.",
            "인터뷰와 MVP 실험에 바로 쓸 다음 행동을 정한다.",
        ],
        strengths=["짧은 입력으로 구조화된 보고서를 생성", "국내/해외 경쟁 구도를 분리"],
        weaknesses=[
            "외부 소스는 접근 실패 시 fixture fallback을 사용",
            "정성 판단은 추가 검증 필요",
        ],
        differentiation_opportunities=[
            "국내 사용자의 업무 맥락과 언어를 우선 반영한다.",
            "경쟁사 목록보다 검증 질문과 MVP 범위를 함께 제시한다.",
            "출처, 관찰일, 신뢰도를 노출해 시장 사실과 가설을 분리한다.",
        ],
        key_risks=[
            "fixture-backed 소스는 현재 시장 사실로 주장할 수 없다.",
            "초기 사용자 문제가 충분히 날카롭지 않으면 기능 범위가 퍼질 수 있다.",
            "외부 데이터 접근 정책이 바뀌면 소스 수집 품질이 흔들릴 수 있다.",
        ],
        build_complexity=(
            "중간: 핵심 보고서 생성은 단순하지만 "
            "최신 소스 검증과 신뢰도 관리는 별도 경계가 필요합니다."
        ),
        recommended_mvp_scope=[
            "아이디어 입력과 구체화된 콘셉트 생성",
            "국내/해외 경쟁 서비스 분리 표",
            "차별화 기회, 주요 리스크, 다음 검증 단계",
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
        references[f"{record.source_name}:{record.url}"] = SourceReference(
            source_name=record.source_name,
            source_url=record.url,
            observed_date=record.observed_date,
            note=source_reference_note(record),
            confidence=record.confidence,
        )
    return list(references.values())


def source_reference_note(record: NormalizedSourceRecord) -> str:
    if record.access_method == "live_http":
        return (
            f"{record.category} collector record. "
            "Live public source data was fetched without credentials or user-query forwarding; "
            "observed date and confidence describe collection time, not market fit."
        )

    return (
        f"{record.category} collector record. "
        "Fixture-backed data is for deterministic workflow validation; "
        "verify current facts before external claims."
    )

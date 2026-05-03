from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from services.api.app.integrations.research_adapters import (
    GeminiCliSearchAdapter,
    LocalGemmaOrganizer,
    OrganizationResult,
    SearchAdapterResult,
    organization_fallback,
)
from services.api.app.integrations.source_collectors import (
    Market,
    NormalizedSourceRecord,
    collect_source_records,
)
from services.api.app.schemas import (
    Competitor,
    IdeaRecommendation,
    IdeaRecommendationRequest,
    IdeaRecommendationResponse,
    IdeaReportListResponse,
    IdeaReportRequest,
    IdeaReportResponse,
    IdeaReportSummary,
    ResearchStatus,
    SourceReference,
    idea_intake_questions_from_answers,
)

RECOMMENDATION_PATTERNS = (
    {
        "title": "{keyword} 고객 반응 분석 도구",
        "summary": "{keyword} 관련 리뷰, 문의, 피드백을 모아 반복 이슈를 보여주는 운영 도구",
        "rationale": "고객 목소리를 구조화하면 초기 MVP 문제 정의와 경쟁 분석이 쉬워집니다.",
        "report_seed": (
            "{keyword} 관련 고객 리뷰와 문의를 자동으로 분석해 "
            "개선 우선순위를 제안하는 SaaS"
        ),
    },
    {
        "title": "{keyword} 업무 자동화 체크리스트",
        "summary": "{keyword} 업무를 단계별 체크리스트와 자동 알림으로 관리하는 팀 생산성 도구",
        "rationale": "한 단어 아이디어를 반복 업무 절감이라는 명확한 가치로 확장합니다.",
        "report_seed": "{keyword} 업무를 체크리스트와 자동 알림으로 표준화하는 팀 생산성 서비스",
    },
    {
        "title": "{keyword} 시장 기회 대시보드",
        "summary": "{keyword} 관련 경쟁 서비스, 가격, 사용자 반응을 한 화면에 정리하는 리서치 도구",
        "rationale": "시장 조사와 포지셔닝을 먼저 확인해야 보고서의 경쟁 분석 품질이 올라갑니다.",
        "report_seed": "{keyword} 분야의 경쟁 서비스와 사용자 반응을 추적하는 시장 기회 대시보드",
    },
    {
        "title": "{keyword} 맞춤 추천 큐레이터",
        "summary": (
            "사용자 상황을 받아 {keyword} 관련 콘텐츠, 서비스, 실행 과제를 추천하는 "
            "큐레이션 서비스"
        ),
        "rationale": (
            "넓은 키워드를 개인화 추천 문제로 좁히면 대상 사용자와 사용 사례를 잡기 쉽습니다."
        ),
        "report_seed": (
            "사용자 상황에 맞춰 {keyword} 관련 콘텐츠와 실행 과제를 추천하는 큐레이션 서비스"
        ),
    },
)


class IdeaReportRepository(Protocol):
    def save_report(self, report: IdeaReportResponse) -> None:
        ...

    def list_reports(self, *, limit: int) -> list[IdeaReportResponse]:
        ...

    def get_report(self, report_id: str) -> IdeaReportResponse | None:
        ...

    def delete_report(self, report_id: str) -> bool:
        ...


def create_idea_report(
    payload: IdeaReportRequest,
    *,
    search_adapter: GeminiCliSearchAdapter | None = None,
    organizer: LocalGemmaOrganizer | None = None,
) -> IdeaReportResponse:
    created_at = datetime.now(tz=UTC)
    observed = created_at.date()
    normalized_idea = payload.idea.strip()
    baseline_records = collect_source_records(idea=normalized_idea, observed_date=observed)
    search_result: SearchAdapterResult | None = None
    organization: OrganizationResult | None = None

    if payload.research:
        search_result = (search_adapter or GeminiCliSearchAdapter()).search(
            idea=normalized_idea,
            observed_date=observed,
        )
        source_records = merge_source_records(
            [*search_result.records, *baseline_records],
        )
        organization = (organizer or LocalGemmaOrganizer()).organize(
            idea=normalized_idea,
            records=source_records,
        )
    else:
        source_records = baseline_records
        organization = default_report_organization()

    organization = organization or organization_fallback(
        normalized_idea,
        "Research organization was not requested.",
    )

    return IdeaReportResponse(
        id=str(uuid4()),
        idea=normalized_idea,
        locale=payload.locale,
        created_at=created_at,
        overview=report_overview(normalized_idea, payload.research, organization),
        idea_intake_questions=idea_intake_questions_from_answers(
            payload.idea_intake_answers
        ),
        clarified_concept=(
            f"{normalized_idea}를 특정 고객군의 반복 업무를 줄이는 문제-해결형 "
            "SaaS 또는 운영 도구로 정의합니다."
        ),
        target_users=list(organization.target_users),
        core_use_cases=list(organization.core_use_cases),
        strengths=[
            "추천 아이템을 검색 가능한 제품 콘셉트로 확장",
            "국내/해외 경쟁 구도를 분리",
        ],
        weaknesses=[
            "외부 검색 또는 로컬 정리 adapter 실패 시 fallback을 사용",
            "정성 판단은 추가 검증 필요",
        ],
        differentiation_opportunities=list(organization.opportunities),
        key_risks=list(organization.risks),
        build_complexity=(
            "중간: 핵심 보고서 생성은 단순하지만 "
            "최신 소스 검증과 신뢰도 관리는 별도 경계가 필요합니다."
        ),
        recommended_mvp_scope=list(organization.mvp_scope),
        domestic_competitors=competitors_for_market(source_records, "domestic_kr"),
        overseas_competitors=competitors_for_market(source_records, "overseas"),
        source_references=source_references_from_records(source_records),
        next_validation_steps=[
            "핵심 사용자 5명을 인터뷰한다.",
            "국내/해외 경쟁사 각각 5개 이상을 최신 source로 확인한다.",
            "가장 작은 MVP 기능 1개를 정의한다.",
        ],
        research_status=research_status_from_results(
            requested=payload.research,
            search_result=search_result,
            organization=organization,
        ),
    )


def list_idea_reports(
    repository: IdeaReportRepository,
    *,
    limit: int = 50,
) -> IdeaReportListResponse:
    return IdeaReportListResponse(
        reports=[
            summarize_idea_report(report)
            for report in repository.list_reports(limit=limit)
        ],
    )


def get_idea_report(
    repository: IdeaReportRepository,
    *,
    report_id: str,
) -> IdeaReportResponse | None:
    return repository.get_report(report_id)


def delete_idea_report(
    repository: IdeaReportRepository,
    *,
    report_id: str,
) -> bool:
    return repository.delete_report(report_id)


def summarize_idea_report(report: IdeaReportResponse) -> IdeaReportSummary:
    return IdeaReportSummary(
        id=report.id,
        idea=report.idea,
        created_at=report.created_at,
        overview=report.overview,
        research_requested=report.research_status.requested,
        domestic_competitor_count=len(report.domestic_competitors),
        overseas_competitor_count=len(report.overseas_competitors),
        source_reference_count=len(report.source_references),
    )


def create_idea_recommendations(
    payload: IdeaRecommendationRequest,
) -> IdeaRecommendationResponse:
    keyword = payload.keyword.strip()
    return IdeaRecommendationResponse(
        keyword=keyword,
        recommendations=[
            IdeaRecommendation(
                title=pattern["title"].format(keyword=keyword),
                summary=pattern["summary"].format(keyword=keyword),
                rationale=pattern["rationale"].format(keyword=keyword),
                report_seed=pattern["report_seed"].format(keyword=keyword),
            )
            for pattern in RECOMMENDATION_PATTERNS
        ],
    )


def report_overview(
    idea: str,
    research_requested: bool,
    organization: OrganizationResult,
) -> str:
    if research_requested:
        return (
            f"'{idea}' 아이디어를 추천 아이템 기반 검색과 자료 정리 흐름으로 "
            f"구체화합니다. {organization.summary}"
        )
    return f"'{idea}' 아이디어를 초기 검증 가능한 제품 개념으로 구체화합니다."


def default_report_organization() -> OrganizationResult:
    return OrganizationResult(
        provider="not_requested",
        status="skipped",
        summary="",
        target_users=("초기 창업자", "소규모 제품팀", "시장 조사가 필요한 기획자"),
        core_use_cases=(
            "짧은 아이디어를 입력해 검증 가능한 제품 콘셉트로 정리한다.",
            "국내/해외 유사 서비스를 나눠 보고 포지셔닝 빈틈을 찾는다.",
            "인터뷰와 MVP 실험에 바로 쓸 다음 행동을 정한다.",
        ),
        opportunities=(
            "국내 사용자의 업무 맥락과 언어를 우선 반영한다.",
            "경쟁사 목록보다 검증 질문과 MVP 범위를 함께 제시한다.",
            "출처, 관찰일, 신뢰도를 노출해 시장 사실과 가설을 분리한다.",
        ),
        risks=(
            "fixture-backed 소스는 현재 시장 사실로 주장할 수 없다.",
            "초기 사용자 문제가 충분히 날카롭지 않으면 기능 범위가 퍼질 수 있다.",
            "외부 데이터 접근 정책이 바뀌면 소스 수집 품질이 흔들릴 수 있다.",
        ),
        mvp_scope=(
            "아이디어 입력과 구체화된 콘셉트 생성",
            "국내/해외 경쟁 서비스 분리 표",
            "차별화 기회, 주요 리스크, 다음 검증 단계",
        ),
        notes=(),
    )


def merge_source_records(records: list[NormalizedSourceRecord]) -> list[NormalizedSourceRecord]:
    deduped: dict[str, NormalizedSourceRecord] = {}
    for record in records:
        deduped[f"{record.source_name}:{record.url}"] = record
    return list(deduped.values())


def research_status_from_results(
    *,
    requested: bool,
    search_result: SearchAdapterResult | None,
    organization: OrganizationResult,
) -> ResearchStatus:
    if not requested:
        return ResearchStatus(
            requested=False,
            search_provider="not_requested",
            search_status="skipped",
            organization_provider="not_requested",
            organization_status="skipped",
            notes=[],
        )

    notes = [
        *(search_result.notes if search_result else ()),
        *organization.notes,
    ]
    return ResearchStatus(
        requested=True,
        search_provider=search_result.provider if search_result else "fallback",
        search_status=search_result.status if search_result else "fallback",
        organization_provider=organization.provider,
        organization_status=organization.status,
        notes=list(notes),
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
    if record.category == "Gemini CLI grounded search result":
        return (
            "Gemini CLI grounded search result. "
            "The selected recommendation seed was sent to Gemini CLI for public-source search; "
            "verify current facts before external claims."
        )

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

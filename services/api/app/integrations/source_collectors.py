from dataclasses import dataclass
from datetime import date
from typing import Literal, Protocol

Confidence = Literal["low", "medium", "high"]
Market = Literal["domestic_kr", "overseas"]
KOREAN_REVIEW_SEARCH_URL = (
    "https://www.google.com/search?"
    "q=%EA%B5%AD%EB%82%B4+%EB%A6%AC%EB%B7%B0+%EB%B6%84%EC%84%9D+SaaS"
)


@dataclass(frozen=True)
class NormalizedSourceRecord:
    title: str
    url: str
    market: Market
    category: str
    summary: str
    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]
    observed_date: date
    confidence: Confidence
    source_name: str


class SourceCollector(Protocol):
    source_name: str

    def collect(self, *, idea: str, observed_date: date) -> list[NormalizedSourceRecord]:
        """Return normalized records without leaking source-specific shapes."""


@dataclass(frozen=True)
class FixtureCollector:
    source_name: str
    source_url: str
    market: Market
    category: str
    title_template: str
    summary_template: str
    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]

    def collect(self, *, idea: str, observed_date: date) -> list[NormalizedSourceRecord]:
        normalized_idea = idea.strip()
        return [
            NormalizedSourceRecord(
                title=self.title_template.format(idea=normalized_idea),
                url=self.source_url,
                market=self.market,
                category=self.category,
                summary=self.summary_template.format(idea=normalized_idea),
                strengths=self.strengths,
                weaknesses=self.weaknesses,
                observed_date=observed_date,
                confidence="low",
                source_name=self.source_name,
            )
        ]


def default_collectors() -> list[SourceCollector]:
    return [
        FixtureCollector(
            source_name="Korean competitor research fixture",
            source_url=KOREAN_REVIEW_SEARCH_URL,
            market="domestic_kr",
            category="domestic competitor fixture",
            title_template="국내 리뷰 분석 SaaS 후보군",
            summary_template=(
                "'{idea}'와 유사한 국내 서비스 후보를 수집하기 위한 fixture-backed "
                "collector record입니다."
            ),
            strengths=(
                "국내 리뷰 채널과 언어 맥락을 우선 검토",
                "현지 영업/고객지원 요구를 빠르게 확인",
            ),
            weaknesses=("실제 경쟁사 사실은 다음 collector 단계에서 검증 필요",),
        ),
        FixtureCollector(
            source_name="Product Hunt",
            source_url="https://www.producthunt.com/",
            market="overseas",
            category="startup launch directory fixture",
            title_template="Product Hunt review-insights reference",
            summary_template=(
                "Product Hunt에서 '{idea}'와 인접한 launch reference를 찾기 위한 "
                "fixture-backed collector record입니다."
            ),
            strengths=("초기 제품 포지셔닝 참고에 적합", "글로벌 launch copy와 카테고리 탐색 가능"),
            weaknesses=("현재 launch 사실은 live collector 또는 browsing으로 확인 필요",),
        ),
        FixtureCollector(
            source_name="PitchWall",
            source_url="https://pitchwall.co/",
            market="overseas",
            category="startup directory fixture",
            title_template="PitchWall SMB analytics reference",
            summary_template=(
                "PitchWall에서 '{idea}'와 비슷한 SMB analytics reference를 찾기 위한 "
                "fixture-backed collector record입니다."
            ),
            strengths=("초기 스타트업 설명 구조를 비교하기 좋음",),
            weaknesses=("디렉터리 정보의 최신성 검증 필요",),
        ),
        FixtureCollector(
            source_name="BetaList",
            source_url="https://betalist.com/",
            market="overseas",
            category="early startup fixture",
            title_template="BetaList early-stage review tooling reference",
            summary_template=(
                "BetaList에서 '{idea}'와 인접한 early-stage tooling을 찾기 위한 "
                "fixture-backed collector record입니다."
            ),
            strengths=("출시 전/초기 단계 제품 아이디어 비교에 유용",),
            weaknesses=("실제 제품 상태와 접근 가능 여부 확인 필요",),
        ),
    ]


def collect_source_records(
    *, idea: str, observed_date: date, collectors: list[SourceCollector] | None = None
) -> list[NormalizedSourceRecord]:
    selected_collectors = collectors or default_collectors()
    records: list[NormalizedSourceRecord] = []
    for collector in selected_collectors:
        records.extend(collector.collect(idea=idea, observed_date=observed_date))
    return records

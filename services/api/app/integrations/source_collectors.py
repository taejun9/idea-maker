import json
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Literal, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from pydantic import BaseModel, ConfigDict, ValidationError

Confidence = Literal["low", "medium", "high"]
Market = Literal["domestic_kr", "overseas"]
AccessMethod = Literal["fixture", "live_http"]
KOREAN_REVIEW_SEARCH_URL = (
    "https://www.google.com/search?q=%EA%B5%AD%EB%82%B4+%EB%A6%AC%EB%B7%B0+%EB%B6%84%EC%84%9D+SaaS"
)
PITCHWALL_HOME_URL = "https://pitchwall.co/"
PITCHWALL_PRODUCT_BASE_URL = "https://pitchwall.co"
PITCHWALL_NEW_PRODUCTS_API_URL = "https://auth.pitchwall.co/api/products/new?page=1"
SOURCE_USER_AGENT = "IdeaMakerBot/0.1 (+https://pitchwall.co/)"
IDEA_TOKEN_ALIASES = {
    "리뷰": ("review", "feedback", "sentiment"),
    "분석": ("analysis", "analytics", "insight", "insights"),
    "소상공인": ("smb", "business", "commerce"),
    "고객": ("customer", "customers"),
    "도구": ("tool", "tools"),
}


class SourceCollectorError(RuntimeError):
    """Raised when a live source cannot be normalized into trusted records."""


class JsonSourceClient(Protocol):
    def fetch_json(self, url: str, *, timeout_seconds: float) -> object:
        """Fetch and decode JSON from a public source URL."""


@dataclass(frozen=True)
class UrlFetchingSourceClient:
    user_agent: str = SOURCE_USER_AGENT
    max_bytes: int = 500_000
    max_attempts: int = 1

    def fetch_json(self, url: str, *, timeout_seconds: float) -> object:
        last_error: SourceCollectorError | None = None
        attempts = max(1, self.max_attempts)

        for _ in range(attempts):
            request = Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": self.user_agent,
                },
            )
            try:
                with urlopen(request, timeout=timeout_seconds) as response:
                    raw_body = response.read(self.max_bytes + 1)
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                last_error = SourceCollectorError(f"Unable to fetch source URL {url}: {exc}")
                continue

            if len(raw_body) > self.max_bytes:
                raise SourceCollectorError(
                    f"Source response exceeded {self.max_bytes} bytes: {url}"
                )

            try:
                return json.loads(raw_body.decode("utf-8"))
            except UnicodeDecodeError as exc:
                raise SourceCollectorError(f"Source response was not UTF-8 JSON: {url}") from exc
            except json.JSONDecodeError as exc:
                raise SourceCollectorError(f"Source response was not valid JSON: {url}") from exc

        if last_error is not None:
            raise last_error
        raise SourceCollectorError(f"Unable to fetch source URL {url}")


class PitchWallProductPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str
    summary: str = ""
    page: str
    published_at: str | None = None


class PitchWallProductsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    data: list[PitchWallProductPayload]


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
    access_method: AccessMethod = "fixture"


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
                access_method="fixture",
            )
        ]


@dataclass(frozen=True)
class PitchWallNewProductsCollector:
    source_name: str = "PitchWall"
    client: JsonSourceClient = field(default_factory=UrlFetchingSourceClient)
    api_url: str = PITCHWALL_NEW_PRODUCTS_API_URL
    timeout_seconds: float = 3.0
    max_records: int = 3

    def collect(self, *, idea: str, observed_date: date) -> list[NormalizedSourceRecord]:
        payload = self.client.fetch_json(self.api_url, timeout_seconds=self.timeout_seconds)
        try:
            response = PitchWallProductsResponse.model_validate(payload)
        except ValidationError as exc:
            raise SourceCollectorError(
                "PitchWall response did not match expected product shape"
            ) from exc

        idea_tokens = normalized_idea_tokens(idea)
        records = [
            self._record_from_product(product, observed_date)
            for product in response.data
            if self._matches_idea(product, idea_tokens)
        ][: self.max_records]

        if not records:
            raise SourceCollectorError("PitchWall returned no locally matched products")
        return records

    def _record_from_product(
        self, product: PitchWallProductPayload, observed_date: date
    ) -> NormalizedSourceRecord:
        source_url = urljoin(PITCHWALL_PRODUCT_BASE_URL, product.page)
        published_note = normalized_published_note(product.published_at)
        source_summary = product.summary.strip() or "No summary provided by PitchWall."

        return NormalizedSourceRecord(
            title=product.title.strip(),
            url=source_url,
            market="overseas",
            category="startup directory live HTTP record",
            summary=f"PitchWall live listing: {source_summary}{published_note}",
            strengths=(
                "Public PitchWall listing fetched without sending the user idea as a query",
                "Useful as an overseas launch-directory reference",
            ),
            weaknesses=(
                "PitchWall latest-products feed is not exhaustive",
                "Local token matching may miss relevant listings or include broad AI references",
            ),
            observed_date=observed_date,
            confidence="medium",
            source_name=self.source_name,
            access_method="live_http",
        )

    def _matches_idea(self, product: PitchWallProductPayload, idea_tokens: set[str]) -> bool:
        if not idea_tokens or not product.title.strip():
            return False

        haystack = f"{product.title} {product.summary}".lower()
        return any(token_matches_text(token, haystack) for token in idea_tokens)


@dataclass(frozen=True)
class FallbackSourceCollector:
    primary: SourceCollector
    fallback: SourceCollector

    @property
    def source_name(self) -> str:
        return self.primary.source_name

    def collect(self, *, idea: str, observed_date: date) -> list[NormalizedSourceRecord]:
        try:
            records = self.primary.collect(idea=idea, observed_date=observed_date)
        except SourceCollectorError:
            return self.fallback.collect(idea=idea, observed_date=observed_date)

        if not records:
            return self.fallback.collect(idea=idea, observed_date=observed_date)
        return records


def normalized_idea_tokens(idea: str) -> set[str]:
    tokens: set[str] = set()
    for token in re.findall(r"[a-z0-9]+|[가-힣]+", idea.lower()):
        if len(token) >= 2:
            tokens.add(token)
        for korean_token, aliases in IDEA_TOKEN_ALIASES.items():
            if korean_token in token:
                tokens.update(aliases)
    return tokens


def token_matches_text(token: str, text: str) -> bool:
    if token.isascii() and token.isalnum():
        return re.search(rf"\b{re.escape(token)}\b", text) is not None
    return token in text


def normalized_published_note(published_at: str | None) -> str:
    if not published_at or not re.match(r"^\d{4}-\d{2}-\d{2}", published_at):
        return ""
    return f" Published on PitchWall at {published_at[:10]}."


def korean_competitor_fixture_collector() -> SourceCollector:
    return FixtureCollector(
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
    )


def product_hunt_fixture_collector() -> SourceCollector:
    return FixtureCollector(
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
    )


def pitchwall_fixture_collector() -> SourceCollector:
    return FixtureCollector(
        source_name="PitchWall",
        source_url=PITCHWALL_HOME_URL,
        market="overseas",
        category="startup directory fixture fallback",
        title_template="PitchWall SMB analytics reference",
        summary_template=(
            "PitchWall live collector가 현재 '{idea}'와 로컬 매칭되는 공개 listing을 "
            "찾지 못했을 때 사용하는 fixture-backed fallback record입니다."
        ),
        strengths=("초기 스타트업 설명 구조를 비교하기 좋음",),
        weaknesses=("live 접근 실패 또는 매칭 실패 시 현재 directory 사실로 사용 금지",),
    )


def betalist_fixture_collector() -> SourceCollector:
    return FixtureCollector(
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
    )


def default_collectors() -> list[SourceCollector]:
    return [
        korean_competitor_fixture_collector(),
        product_hunt_fixture_collector(),
        FallbackSourceCollector(
            primary=PitchWallNewProductsCollector(),
            fallback=pitchwall_fixture_collector(),
        ),
        betalist_fixture_collector(),
    ]


def collect_source_records(
    *, idea: str, observed_date: date, collectors: list[SourceCollector] | None = None
) -> list[NormalizedSourceRecord]:
    selected_collectors = collectors or default_collectors()
    records: list[NormalizedSourceRecord] = []
    for collector in selected_collectors:
        records.extend(collector.collect(idea=idea, observed_date=observed_date))
    return records

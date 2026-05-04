from datetime import date

import pytest

from services.api.app.integrations.source_collectors import (
    FallbackSourceCollector,
    PitchWallNewProductsCollector,
    SourceCollectorError,
    UrlFetchingSourceClient,
    clear_source_index_cache,
    collect_source_records,
    default_collectors,
    pitchwall_fixture_collector,
)


class FakeJsonClient:
    def __init__(self, payload: object) -> None:
        self.payload = payload
        self.requested_urls: list[str] = []

    def fetch_json(self, url: str, *, timeout_seconds: float) -> object:
        self.requested_urls.append(url)
        assert timeout_seconds > 0
        return self.payload


class FailingJsonClient:
    def fetch_json(self, url: str, *, timeout_seconds: float) -> object:
        raise SourceCollectorError("network disabled in deterministic tests")


@pytest.fixture(autouse=True)
def clear_public_source_cache():
    clear_source_index_cache()
    yield
    clear_source_index_cache()


def test_default_collectors_return_normalized_records(monkeypatch) -> None:
    observed = date(2026, 5, 3)
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", FailingJsonClient().fetch_json)

    records = collect_source_records(
        idea="동네 소상공인을 위한 AI 리뷰 분석 도구",
        observed_date=observed,
    )

    assert len(records) == 4
    assert {record.source_name for record in records} == {
        "Korean competitor research fixture",
        "Product Hunt",
        "PitchWall",
        "BetaList",
    }
    assert {record.market for record in records} == {"domestic_kr", "overseas"}
    assert all(record.url.startswith("https://") for record in records)
    assert all(record.observed_date == observed for record in records)
    assert all(record.confidence == "low" for record in records)
    assert all(record.category for record in records)
    assert all(record.access_method == "fixture" for record in records)


def test_fixture_records_embed_idea_without_todo_placeholders(monkeypatch) -> None:
    observed = date(2026, 5, 3)
    monkeypatch.setattr(UrlFetchingSourceClient, "fetch_json", FailingJsonClient().fetch_json)

    records = collect_source_records(idea="리뷰 분석", observed_date=observed)

    assert any("리뷰 분석" in record.summary for record in records)
    assert all("[TODO" not in record.title for record in records)
    assert all("placeholder" not in record.summary.lower() for record in records)


def test_default_collectors_expose_source_names() -> None:
    collectors = default_collectors()

    assert [collector.source_name for collector in collectors] == [
        "Korean competitor research fixture",
        "Product Hunt",
        "PitchWall",
        "BetaList",
    ]


def test_pitchwall_live_collector_normalizes_public_api_payload() -> None:
    observed = date(2026, 5, 3)
    fake_client = FakeJsonClient(
        {
            "data": [
                {
                    "title": "Qria",
                    "summary": "Customer feedback and review gathering with AI analysis.",
                    "page": "/product/qria",
                    "published_at": "2026-05-02T05:21:43.000000Z",
                    "ignored": "field",
                },
                {
                    "title": "Unrelated",
                    "summary": "A cooking notebook for home recipes.",
                    "page": "/product/unrelated",
                    "published_at": "2026-05-01T00:00:00.000000Z",
                },
            ]
        }
    )
    collector = PitchWallNewProductsCollector(client=fake_client)

    records = collector.collect(idea="AI 리뷰 분석 도구", observed_date=observed)

    assert len(records) == 1
    assert records[0].title == "Qria"
    assert records[0].url == "https://pitchwall.co/product/qria"
    assert records[0].market == "overseas"
    assert records[0].observed_date == observed
    assert records[0].confidence == "medium"
    assert records[0].source_name == "PitchWall"
    assert records[0].access_method == "live_http"
    assert "2026-05-02" in records[0].summary


def test_pitchwall_live_collector_does_not_forward_idea_as_query() -> None:
    fake_client = FakeJsonClient(
        {
            "data": [
                {
                    "title": "AI Review Desk",
                    "summary": "AI review analysis for customer feedback.",
                    "page": "/product/ai-review-desk",
                }
            ]
        }
    )
    collector = PitchWallNewProductsCollector(client=fake_client)

    collector.collect(idea="기밀 고객 리뷰 분석 도구", observed_date=date(2026, 5, 3))

    assert fake_client.requested_urls == ["https://auth.pitchwall.co/api/products/new?page=1"]
    assert "기밀" not in fake_client.requested_urls[0]
    assert "리뷰" not in fake_client.requested_urls[0]


def test_pitchwall_live_collector_reuses_cached_public_feed() -> None:
    observed = date(2026, 5, 3)
    fake_client = FakeJsonClient(
        {
            "data": [
                {
                    "title": "AI Review Desk",
                    "summary": "AI review analysis for customer feedback.",
                    "page": "/product/ai-review-desk",
                }
            ]
        }
    )
    collector = PitchWallNewProductsCollector(client=fake_client)

    first_records = collector.collect(idea="AI 리뷰 분석 도구", observed_date=observed)
    second_records = collector.collect(idea="AI 리뷰 분석 도구", observed_date=observed)

    assert fake_client.requested_urls == [
        "https://auth.pitchwall.co/api/products/new?page=1"
    ]
    assert first_records == second_records
    assert first_records[0].access_method == "live_http"


def test_pitchwall_fixture_fallback_remains_deterministic() -> None:
    observed = date(2026, 5, 3)
    live_collector = PitchWallNewProductsCollector(client=FailingJsonClient())
    fallback_collector = FallbackSourceCollector(
        primary=live_collector,
        fallback=pitchwall_fixture_collector(),
    )

    fallback_records = fallback_collector.collect(idea="리뷰 분석", observed_date=observed)
    direct_fixture_records = pitchwall_fixture_collector().collect(
        idea="리뷰 분석",
        observed_date=observed,
    )

    assert live_collector.source_name == "PitchWall"
    assert fallback_records == direct_fixture_records
    assert fallback_records[0].confidence == "low"
    assert fallback_records[0].access_method == "fixture"

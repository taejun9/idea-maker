from datetime import date

from services.api.app.integrations.source_collectors import NormalizedSourceRecord
from services.api.app.repositories.source_index import (
    SOURCE_INDEX_EMBEDDING_DIMENSIONS,
    InMemorySourceIndexRepository,
    SourceIndexQuery,
    source_record_embedding,
)


def source_record(
    *,
    title: str,
    summary: str,
    market: str = "overseas",
    observed_date: date = date(2026, 5, 4),
    confidence: str = "medium",
    access_method: str = "live_http",
) -> NormalizedSourceRecord:
    return NormalizedSourceRecord(
        title=title,
        url=f"https://example.com/{title.lower().replace(' ', '-')}",
        market=market,
        category="startup directory live HTTP record",
        summary=summary,
        strengths=("Useful public source record",),
        weaknesses=("Needs market-fit verification",),
        observed_date=observed_date,
        confidence=confidence,
        source_name="Test Directory",
        access_method=access_method,
    )


def test_source_index_retrieves_live_public_records_by_vector_similarity() -> None:
    repository = InMemorySourceIndexRepository()
    indexed_count = repository.upsert_records(
        [
            source_record(
                title="AI Review Desk",
                summary="Review analysis for customer feedback teams.",
            ),
            source_record(
                title="Recipe Notebook",
                summary="A home cooking planner.",
            ),
        ],
        sensitive_text="AI 리뷰 분석 도구",
    )

    result = repository.retrieve_records(
        SourceIndexQuery(
            idea="리뷰 분석",
            observed_date=date(2026, 5, 4),
        )
    )

    assert indexed_count == 2
    assert result.status == "success"
    assert result.method == "source_index_vector"
    assert [record.title for record in result.records] == ["AI Review Desk"]
    assert result.records[0].access_method == "source_index"


def test_source_index_builds_fixed_size_source_embeddings() -> None:
    embedding = source_record_embedding(
        source_record(
            title="AI Review Desk",
            summary="Review analysis for customer feedback teams.",
        )
    )

    assert len(embedding) == SOURCE_INDEX_EMBEDDING_DIMENSIONS
    assert any(value != 0 for value in embedding)


def test_source_index_does_not_store_fixture_or_raw_idea_records() -> None:
    repository = InMemorySourceIndexRepository()
    raw_idea = "비밀 고객 리뷰 분석 도구"
    indexed_count = repository.upsert_records(
        [
            source_record(
                title="Fixture Candidate",
                summary=f"{raw_idea} fixture-backed record",
                access_method="fixture",
            ),
            source_record(
                title="Raw Idea Echo",
                summary=f"{raw_idea} appears in a live summary",
                access_method="live_http",
            ),
        ],
        sensitive_text=raw_idea,
    )

    result = repository.retrieve_records(
        SourceIndexQuery(
            idea=raw_idea,
            observed_date=date(2026, 5, 4),
        )
    )

    assert indexed_count == 0
    assert result.status == "fallback"
    assert result.records == ()


def test_source_index_filters_by_market_and_freshness() -> None:
    repository = InMemorySourceIndexRepository()
    repository.upsert_records(
        [
            source_record(
                title="Domestic Review Ops",
                summary="Korean review analysis workflow.",
                market="domestic_kr",
                observed_date=date(2026, 5, 1),
            ),
            source_record(
                title="Old Review Ops",
                summary="Review analysis workflow.",
                observed_date=date(2026, 1, 1),
            ),
        ],
        sensitive_text="리뷰 분석",
    )

    result = repository.retrieve_records(
        SourceIndexQuery(
            idea="리뷰 분석",
            observed_date=date(2026, 5, 4),
            markets=("domestic_kr",),
            max_age_days=30,
        )
    )

    assert [record.title for record in result.records] == ["Domestic Review Ops"]

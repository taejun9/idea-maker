from datetime import date

from services.api.app.integrations.source_collectors import (
    collect_source_records,
    default_collectors,
)


def test_default_collectors_return_normalized_records() -> None:
    observed = date(2026, 5, 3)

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


def test_fixture_records_embed_idea_without_todo_placeholders() -> None:
    observed = date(2026, 5, 3)

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

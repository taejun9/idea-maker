from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from threading import Lock
from typing import Any, Literal

from services.api.app.integrations.source_collectors import (
    Market,
    NormalizedSourceRecord,
    normalized_idea_tokens,
    token_matches_text,
)

SourceIndexStatus = Literal["success", "partial", "fallback"]
SourceIndexMethod = Literal["source_index_token", "source_index_vector"]

SOURCE_INDEX_MAX_CANDIDATES = 100
SOURCE_INDEX_DEFAULT_MAX_AGE_DAYS = 90
SOURCE_INDEX_EMBEDDING_DIMENSIONS = 64
SOURCE_INDEX_VECTOR_MIN_SIMILARITY = 0.08
CONFIDENCE_SCORE = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


class SourceIndexError(RuntimeError):
    """Raised when source-index storage or retrieval cannot complete."""


@dataclass(frozen=True)
class SourceIndexQuery:
    idea: str
    observed_date: date
    markets: tuple[Market, ...] = ("domestic_kr", "overseas")
    max_records: int = 8
    max_age_days: int = SOURCE_INDEX_DEFAULT_MAX_AGE_DAYS


@dataclass(frozen=True)
class SourceIndexRetrievalResult:
    status: SourceIndexStatus
    method: SourceIndexMethod
    records: tuple[NormalizedSourceRecord, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class SourceIndexStoredRecord:
    record: NormalizedSourceRecord
    embedding: tuple[float, ...]


class InMemorySourceIndexRepository:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str, str, str], SourceIndexStoredRecord] = {}
        self._lock = Lock()

    def ensure_schema(self) -> None:
        return None

    def upsert_records(
        self,
        records: list[NormalizedSourceRecord],
        *,
        sensitive_text: str = "",
    ) -> int:
        indexable_records = [
            record for record in records if source_record_can_be_indexed(record, sensitive_text)
        ]
        with self._lock:
            for record in indexable_records:
                self._records[source_record_key(record)] = SourceIndexStoredRecord(
                    record=record,
                    embedding=source_record_embedding(record),
                )
        return len(indexable_records)

    def retrieve_records(self, query: SourceIndexQuery) -> SourceIndexRetrievalResult:
        with self._lock:
            records = list(self._records.values())
        return retrieve_source_records_from_candidates(records, query)

    def clear(self) -> None:
        with self._lock:
            self._records.clear()


class PostgresSourceIndexRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._schema_lock = Lock()
        self._schema_ready = False

    def upsert_records(
        self,
        records: list[NormalizedSourceRecord],
        *,
        sensitive_text: str = "",
    ) -> int:
        self.ensure_schema()
        indexable_records = [
            record for record in records if source_record_can_be_indexed(record, sensitive_text)
        ]
        if not indexable_records:
            return 0

        psycopg, _, jsonb = self._psycopg_modules()
        indexed_at = datetime.now(tz=UTC)
        try:
            with psycopg.connect(self._database_url) as connection:
                with connection.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO source_observations (
                            source_name,
                            source_url,
                            market,
                            category,
                            title,
                            summary,
                            strengths,
                            weaknesses,
                            observed_date,
                            confidence,
                            access_method,
                            embedding,
                            indexed_at
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (
                            source_name,
                            source_url,
                            observed_date,
                            access_method
                        )
                        DO UPDATE
                        SET market = EXCLUDED.market,
                            category = EXCLUDED.category,
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            strengths = EXCLUDED.strengths,
                            weaknesses = EXCLUDED.weaknesses,
                            confidence = EXCLUDED.confidence,
                            embedding = EXCLUDED.embedding,
                            indexed_at = EXCLUDED.indexed_at
                        """,
                        [
                            (
                                record.source_name,
                                record.url,
                                record.market,
                                record.category,
                                record.title,
                                record.summary,
                                jsonb(list(record.strengths)),
                                jsonb(list(record.weaknesses)),
                                record.observed_date,
                                record.confidence,
                                record.access_method,
                                jsonb(list(source_record_embedding(record))),
                                indexed_at,
                            )
                            for record in indexable_records
                        ],
                    )
        except psycopg.Error as exc:
            raise SourceIndexError("Unable to upsert source index records") from exc
        return len(indexable_records)

    def retrieve_records(self, query: SourceIndexQuery) -> SourceIndexRetrievalResult:
        self.ensure_schema()
        if not query.markets:
            return source_index_fallback("Source index retrieval skipped: no markets requested.")

        min_observed_date = query.observed_date - timedelta(days=max(0, query.max_age_days))
        market_placeholders = ", ".join(["%s"] * len(query.markets))
        candidate_limit = max(query.max_records * 12, SOURCE_INDEX_MAX_CANDIDATES)
        sql = f"""
            SELECT
                source_name,
                source_url,
                market,
                category,
                title,
                summary,
                strengths,
                weaknesses,
                observed_date,
                confidence,
                access_method,
                embedding
            FROM source_observations
            WHERE market IN ({market_placeholders})
              AND observed_date >= %s
            ORDER BY observed_date DESC, indexed_at DESC
            LIMIT %s
        """
        psycopg, dict_row, _ = self._psycopg_modules()
        try:
            with psycopg.connect(self._database_url, row_factory=dict_row) as connection:
                rows = connection.execute(
                    sql,
                    (*query.markets, min_observed_date, candidate_limit),
                ).fetchall()
        except psycopg.Error as exc:
            raise SourceIndexError("Unable to retrieve source index records") from exc

        records = [stored_source_record_from_row(row) for row in rows]
        return retrieve_source_records_from_candidates(records, query)

    def ensure_schema(self) -> None:
        if self._schema_ready:
            return

        with self._schema_lock:
            if self._schema_ready:
                return

            psycopg, _, _ = self._psycopg_modules()
            try:
                with psycopg.connect(self._database_url) as connection:
                    connection.execute(
                        """
                        CREATE TABLE IF NOT EXISTS source_observations (
                            id bigserial PRIMARY KEY,
                            source_name text NOT NULL,
                            source_url text NOT NULL,
                            market text NOT NULL,
                            category text NOT NULL,
                            title text NOT NULL,
                            summary text NOT NULL,
                            strengths jsonb NOT NULL DEFAULT '[]'::jsonb,
                            weaknesses jsonb NOT NULL DEFAULT '[]'::jsonb,
                            observed_date date NOT NULL,
                            confidence text NOT NULL,
                            access_method text NOT NULL,
                            embedding jsonb NOT NULL DEFAULT '[]'::jsonb,
                            indexed_at timestamptz NOT NULL
                        )
                        """,
                    )
                    connection.execute(
                        """
                        ALTER TABLE source_observations
                        ADD COLUMN IF NOT EXISTS
                        embedding jsonb NOT NULL DEFAULT '[]'::jsonb
                        """,
                    )
                    connection.execute(
                        """
                        CREATE UNIQUE INDEX IF NOT EXISTS
                        source_observations_source_url_observed_idx
                        ON source_observations (
                            source_name,
                            source_url,
                            observed_date,
                            access_method
                        )
                        """,
                    )
                    connection.execute(
                        """
                        CREATE INDEX IF NOT EXISTS
                        source_observations_market_observed_idx
                        ON source_observations (market, observed_date DESC)
                        """,
                    )
                    connection.execute(
                        """
                        CREATE INDEX IF NOT EXISTS
                        source_observations_source_name_idx
                        ON source_observations (source_name)
                        """,
                    )
            except psycopg.Error as exc:
                raise SourceIndexError("Unable to ensure source index schema") from exc
            self._schema_ready = True

    def _psycopg_modules(self) -> tuple[Any, Any, Any]:
        import psycopg
        from psycopg.rows import dict_row
        from psycopg.types.json import Jsonb

        return psycopg, dict_row, Jsonb


def source_record_key(record: NormalizedSourceRecord) -> tuple[str, str, str, str]:
    return (
        record.source_name,
        record.url,
        record.observed_date.isoformat(),
        record.access_method,
    )


def source_record_can_be_indexed(
    record: NormalizedSourceRecord,
    sensitive_text: str = "",
) -> bool:
    if record.access_method != "live_http":
        return False
    normalized_sensitive_text = sensitive_text.strip().lower()
    if not normalized_sensitive_text:
        return True
    return normalized_sensitive_text not in source_record_search_text(record)


def source_record_search_text(record: NormalizedSourceRecord) -> str:
    return " ".join(
        (
            record.title,
            record.category,
            record.summary,
            " ".join(record.strengths),
            " ".join(record.weaknesses),
            record.source_name,
        )
    ).lower()


def retrieve_source_records_from_candidates(
    records: list[SourceIndexStoredRecord],
    query: SourceIndexQuery,
) -> SourceIndexRetrievalResult:
    vector_result = retrieve_vector_source_records_from_candidates(records, query)
    if vector_result.records:
        return vector_result

    token_result = retrieve_token_source_records_from_candidates(records, query)
    if token_result.records:
        return SourceIndexRetrievalResult(
            status="partial",
            method="source_index_vector",
            records=token_result.records,
            notes=(
                "Source index vector retrieval returned no matches; token fallback used.",
                *token_result.notes,
            ),
        )
    return vector_result


def retrieve_vector_source_records_from_candidates(
    records: list[SourceIndexStoredRecord],
    query: SourceIndexQuery,
) -> SourceIndexRetrievalResult:
    query_embedding = text_embedding(query.idea)
    if not any(query_embedding):
        return source_index_fallback("Source index vector retrieval skipped: no query vector.")
    query_tokens = normalized_idea_tokens(query.idea)

    min_observed_date = query.observed_date - timedelta(days=max(0, query.max_age_days))
    ranked_records: list[tuple[float, int, date, str, NormalizedSourceRecord]] = []
    for stored_record in records:
        record = stored_record.record
        if record.market not in query.markets:
            continue
        if record.observed_date < min_observed_date:
            continue
        if query_tokens and source_record_match_score(record, query_tokens) <= 0:
            continue

        embedding = stored_record.embedding or source_record_embedding(record)
        similarity = cosine_similarity(query_embedding, embedding)
        if similarity < SOURCE_INDEX_VECTOR_MIN_SIMILARITY:
            continue
        ranked_records.append(
            (
                similarity,
                CONFIDENCE_SCORE.get(record.confidence, 0),
                record.observed_date,
                f"{record.source_name}:{record.title}",
                retrieved_source_record(record),
            )
        )

    ranked_records.sort(key=lambda item: (-item[0], -item[1], -item[2].toordinal(), item[3]))
    selected_records = tuple(record for *_, record in ranked_records[: query.max_records])
    if not selected_records:
        return source_index_fallback("Source index returned no vector-matched records.")

    return SourceIndexRetrievalResult(
        status="success",
        method="source_index_vector",
        records=selected_records,
        notes=(
            f"Source index returned {len(selected_records)} vector-matched records.",
        ),
    )


def retrieve_token_source_records_from_candidates(
    records: list[SourceIndexStoredRecord],
    query: SourceIndexQuery,
) -> SourceIndexRetrievalResult:
    tokens = normalized_idea_tokens(query.idea)
    if not tokens:
        return source_index_fallback(
            "Source index token retrieval skipped: no query tokens.",
            method="source_index_token",
        )

    min_observed_date = query.observed_date - timedelta(days=max(0, query.max_age_days))
    ranked_records: list[tuple[int, int, date, str, NormalizedSourceRecord]] = []
    for stored_record in records:
        record = stored_record.record
        if record.market not in query.markets:
            continue
        if record.observed_date < min_observed_date:
            continue

        score = source_record_match_score(record, tokens)
        if score <= 0:
            continue
        ranked_records.append(
            (
                score,
                CONFIDENCE_SCORE.get(record.confidence, 0),
                record.observed_date,
                f"{record.source_name}:{record.title}",
                retrieved_source_record(record),
            )
        )

    ranked_records.sort(key=lambda item: (-item[0], -item[1], -item[2].toordinal(), item[3]))
    selected_records = tuple(record for *_, record in ranked_records[: query.max_records])
    if not selected_records:
        return source_index_fallback(
            "Source index returned no token-matched records.",
            method="source_index_token",
        )

    return SourceIndexRetrievalResult(
        status="success",
        method="source_index_token",
        records=selected_records,
        notes=(
            f"Source index returned {len(selected_records)} token-matched records.",
        ),
    )


def source_record_match_score(record: NormalizedSourceRecord, tokens: set[str]) -> int:
    haystack = source_record_search_text(record)
    return sum(1 for token in tokens if token_matches_text(token, haystack))


def retrieved_source_record(record: NormalizedSourceRecord) -> NormalizedSourceRecord:
    return NormalizedSourceRecord(
        title=record.title,
        url=record.url,
        market=record.market,
        category=record.category,
        summary=record.summary,
        strengths=record.strengths,
        weaknesses=record.weaknesses,
        observed_date=record.observed_date,
        confidence=record.confidence,
        source_name=record.source_name,
        access_method="source_index",
    )


def source_record_embedding(record: NormalizedSourceRecord) -> tuple[float, ...]:
    return text_embedding(source_record_search_text(record))


def text_embedding(value: str) -> tuple[float, ...]:
    tokens = sorted(embedding_tokens(value))
    if not tokens:
        return tuple(0.0 for _ in range(SOURCE_INDEX_EMBEDDING_DIMENSIONS))

    vector = [0.0] * SOURCE_INDEX_EMBEDDING_DIMENSIONS
    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % SOURCE_INDEX_EMBEDDING_DIMENSIONS
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    return normalized_vector(vector)


def embedding_tokens(value: str) -> set[str]:
    tokens = normalized_idea_tokens(value)
    tokens.update(
        token
        for token in re.findall(r"[a-z0-9]+|[가-힣]+", value.lower())
        if len(token) >= 2
    )
    return tokens


def normalized_vector(vector: list[float]) -> tuple[float, ...]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return tuple(0.0 for _ in vector)
    return tuple(value / magnitude for value in vector)


def cosine_similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum(
        left_value * right_value
        for left_value, right_value in zip(left, right, strict=False)
    )


def stored_source_record_from_row(row: dict[str, Any]) -> SourceIndexStoredRecord:
    record = NormalizedSourceRecord(
        title=row["title"],
        url=row["source_url"],
        market=row["market"],
        category=row["category"],
        summary=row["summary"],
        strengths=tuple(row["strengths"] or ()),
        weaknesses=tuple(row["weaknesses"] or ()),
        observed_date=row["observed_date"],
        confidence=row["confidence"],
        source_name=row["source_name"],
        access_method=row["access_method"],
    )
    embedding = tuple(float(value) for value in (row["embedding"] or ()))
    return SourceIndexStoredRecord(record=record, embedding=embedding)


def source_index_fallback(
    note: str,
    *,
    method: SourceIndexMethod = "source_index_vector",
) -> SourceIndexRetrievalResult:
    return SourceIndexRetrievalResult(
        status="fallback",
        method=method,
        records=(),
        notes=(note,),
    )


SourceIndexRepository = InMemorySourceIndexRepository | PostgresSourceIndexRepository

from __future__ import annotations

from threading import Lock
from typing import Any

from services.api.app.schemas import IdeaReportResponse


class InMemoryIdeaReportRepository:
    def __init__(self) -> None:
        self._reports: dict[str, IdeaReportResponse] = {}
        self._lock = Lock()

    def ensure_schema(self) -> None:
        return None

    def save_report(self, report: IdeaReportResponse) -> None:
        with self._lock:
            self._reports[report.id] = report

    def list_reports(self, *, limit: int) -> list[IdeaReportResponse]:
        with self._lock:
            reports = sorted(
                self._reports.values(),
                key=lambda report: report.created_at,
                reverse=True,
            )
            return reports[:limit]

    def get_report(self, report_id: str) -> IdeaReportResponse | None:
        with self._lock:
            return self._reports.get(report_id)

    def delete_report(self, report_id: str) -> bool:
        with self._lock:
            return self._reports.pop(report_id, None) is not None


class PostgresIdeaReportRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._schema_lock = Lock()
        self._schema_ready = False

    def save_report(self, report: IdeaReportResponse) -> None:
        self.ensure_schema()
        psycopg, _, jsonb = self._psycopg_modules()
        with psycopg.connect(self._database_url) as connection:
            connection.execute(
                """
                INSERT INTO idea_reports (
                    id,
                    idea,
                    locale,
                    research_requested,
                    created_at,
                    report
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET idea = EXCLUDED.idea,
                    locale = EXCLUDED.locale,
                    research_requested = EXCLUDED.research_requested,
                    created_at = EXCLUDED.created_at,
                    report = EXCLUDED.report
                """,
                (
                    report.id,
                    report.idea,
                    report.locale,
                    report.research_status.requested,
                    report.created_at,
                    jsonb(report.model_dump(mode="json")),
                ),
            )

    def list_reports(self, *, limit: int) -> list[IdeaReportResponse]:
        self.ensure_schema()
        psycopg, dict_row, _ = self._psycopg_modules()
        with psycopg.connect(self._database_url, row_factory=dict_row) as connection:
            rows = connection.execute(
                """
                SELECT report
                FROM idea_reports
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            ).fetchall()
        return [IdeaReportResponse.model_validate(row["report"]) for row in rows]

    def get_report(self, report_id: str) -> IdeaReportResponse | None:
        self.ensure_schema()
        psycopg, dict_row, _ = self._psycopg_modules()
        with psycopg.connect(self._database_url, row_factory=dict_row) as connection:
            row = connection.execute(
                """
                SELECT report
                FROM idea_reports
                WHERE id = %s
                """,
                (report_id,),
            ).fetchone()
        if row is None:
            return None
        return IdeaReportResponse.model_validate(row["report"])

    def delete_report(self, report_id: str) -> bool:
        self.ensure_schema()
        psycopg, _, _ = self._psycopg_modules()
        with psycopg.connect(self._database_url) as connection:
            cursor = connection.execute(
                """
                DELETE FROM idea_reports
                WHERE id = %s
                """,
                (report_id,),
            )
            return cursor.rowcount > 0

    def ensure_schema(self) -> None:
        if self._schema_ready:
            return

        with self._schema_lock:
            if self._schema_ready:
                return

            psycopg, _, _ = self._psycopg_modules()
            with psycopg.connect(self._database_url) as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS idea_reports (
                        id uuid PRIMARY KEY,
                        idea text NOT NULL,
                        locale text NOT NULL,
                        research_requested boolean NOT NULL,
                        created_at timestamptz NOT NULL,
                        report jsonb NOT NULL
                    )
                    """,
                )
                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idea_reports_created_at_idx
                    ON idea_reports (created_at DESC)
                    """,
                )
            self._schema_ready = True

    def _psycopg_modules(self) -> tuple[Any, Any, Any]:
        import psycopg
        from psycopg.rows import dict_row
        from psycopg.types.json import Jsonb

        return psycopg, dict_row, Jsonb


IdeaReportRepository = InMemoryIdeaReportRepository | PostgresIdeaReportRepository

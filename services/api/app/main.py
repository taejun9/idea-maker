import os
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware

from services.api.app.core.settings import database_url
from services.api.app.repositories.idea_reports import (
    IdeaReportRepository,
    InMemoryIdeaReportRepository,
    PostgresIdeaReportRepository,
)
from services.api.app.schemas import (
    HealthResponse,
    IdeaRecommendationRequest,
    IdeaRecommendationResponse,
    IdeaReportListResponse,
    IdeaReportRequest,
    IdeaReportResponse,
    QuickIdeaExampleResponse,
)
from services.api.app.services import (
    create_idea_recommendations as build_idea_recommendations,
)
from services.api.app.services import (
    create_idea_report as build_idea_report,
)
from services.api.app.services import (
    create_quick_idea_examples as build_quick_idea_examples,
)
from services.api.app.services import (
    delete_idea_report as remove_idea_report,
)
from services.api.app.services import (
    get_idea_report as fetch_idea_report,
)
from services.api.app.services import (
    list_idea_reports as build_idea_report_list,
)


def allowed_cors_origins(environment: Mapping[str, str] = os.environ) -> list[str]:
    origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]
    web_port = environment.get("WEB_PORT")
    if web_port:
        origins.extend(
            [
                f"http://127.0.0.1:{web_port}",
                f"http://localhost:{web_port}",
            ]
        )

    configured_origins = environment.get("WEB_ORIGINS", "")
    origins.extend(
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    )
    return list(dict.fromkeys(origins))


def build_idea_report_repository(
    environment: Mapping[str, str] = os.environ,
) -> IdeaReportRepository:
    configured_database_url = database_url(environment)
    if configured_database_url:
        return PostgresIdeaReportRepository(configured_database_url)
    return InMemoryIdeaReportRepository()


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncIterator[None]:
    app_instance.state.idea_report_repository.ensure_schema()
    yield


app = FastAPI(title="Idea Maker API", lifespan=lifespan)
app.state.idea_report_repository = build_idea_report_repository()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def idea_report_repository() -> IdeaReportRepository:
    return app.state.idea_report_repository


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="idea-maker-api")


@app.get("/api/quick-idea-examples", response_model=QuickIdeaExampleResponse)
def list_quick_idea_examples(
    count: Annotated[int, Query(ge=1, le=10)] = 5,
) -> QuickIdeaExampleResponse:
    return build_quick_idea_examples(count=count)


@app.post("/api/idea-reports", response_model=IdeaReportResponse)
def create_idea_report(payload: IdeaReportRequest) -> IdeaReportResponse:
    report = build_idea_report(payload)
    idea_report_repository().save_report(report)
    return report


@app.get("/api/idea-reports", response_model=IdeaReportListResponse)
def list_idea_reports(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> IdeaReportListResponse:
    return build_idea_report_list(idea_report_repository(), limit=limit)


@app.get("/api/idea-reports/{report_id}", response_model=IdeaReportResponse)
def get_idea_report(report_id: str) -> IdeaReportResponse:
    report = fetch_idea_report(idea_report_repository(), report_id=report_id)
    if report is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "idea_report_not_found",
                "message": "보고서를 찾을 수 없습니다.",
            },
        )
    return report


@app.delete("/api/idea-reports/{report_id}", status_code=204)
def delete_idea_report(report_id: str) -> Response:
    deleted = remove_idea_report(idea_report_repository(), report_id=report_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": "idea_report_not_found",
                "message": "보고서를 찾을 수 없습니다.",
            },
        )
    return Response(status_code=204)


@app.post("/api/idea-recommendations", response_model=IdeaRecommendationResponse)
def create_idea_recommendations(
    payload: IdeaRecommendationRequest,
) -> IdeaRecommendationResponse:
    return build_idea_recommendations(payload)

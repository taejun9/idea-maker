import os
from collections.abc import Mapping

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.app.schemas import (
    HealthResponse,
    IdeaRecommendationRequest,
    IdeaRecommendationResponse,
    IdeaReportRequest,
    IdeaReportResponse,
)
from services.api.app.services import (
    create_idea_recommendations as build_idea_recommendations,
)
from services.api.app.services import (
    create_idea_report as build_idea_report,
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


app = FastAPI(title="Idea Maker API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_cors_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="idea-maker-api")


@app.post("/api/idea-reports", response_model=IdeaReportResponse)
def create_idea_report(payload: IdeaReportRequest) -> IdeaReportResponse:
    return build_idea_report(payload)


@app.post("/api/idea-recommendations", response_model=IdeaRecommendationResponse)
def create_idea_recommendations(
    payload: IdeaRecommendationRequest,
) -> IdeaRecommendationResponse:
    return build_idea_recommendations(payload)

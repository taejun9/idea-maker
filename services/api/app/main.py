from fastapi import FastAPI

from services.api.app.schemas import HealthResponse, IdeaReportRequest, IdeaReportResponse
from services.api.app.services import create_placeholder_report

app = FastAPI(title="Idea Maker API")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="idea-maker-api")


@app.post("/api/idea-reports", response_model=IdeaReportResponse)
def create_idea_report(payload: IdeaReportRequest) -> IdeaReportResponse:
    return create_placeholder_report(payload)


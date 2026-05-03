from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.api.app.schemas import HealthResponse, IdeaReportRequest, IdeaReportResponse
from services.api.app.services import create_idea_report as build_idea_report

app = FastAPI(title="Idea Maker API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
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

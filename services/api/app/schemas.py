from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class IdeaReportRequest(BaseModel):
    idea: str = Field(min_length=5, max_length=2000)
    locale: str = Field(default="ko-KR")


class Competitor(BaseModel):
    name: str
    market: Literal["domestic_kr", "overseas"]
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    source_url: str | None = None
    observed_date: date
    confidence: Literal["low", "medium", "high"]


class SourceReference(BaseModel):
    source_name: str
    source_url: str
    observed_date: date
    note: str
    confidence: Literal["low", "medium", "high"]


class IdeaReportResponse(BaseModel):
    overview: str
    target_users: list[str]
    strengths: list[str]
    weaknesses: list[str]
    domestic_competitors: list[Competitor]
    overseas_competitors: list[Competitor]
    source_references: list[SourceReference]
    next_validation_steps: list[str]


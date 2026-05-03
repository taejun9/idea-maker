from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class IdeaReportRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    idea: str = Field(min_length=5, max_length=2000)
    locale: str = Field(default="ko-KR")
    research: bool = Field(default=False)


class IdeaRecommendationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    keyword: str = Field(min_length=1, max_length=120)
    locale: str = Field(default="ko-KR")

    @field_validator("keyword")
    @classmethod
    def keyword_must_be_short(cls, value: str) -> str:
        tokens = value.split()
        if not tokens:
            raise ValueError("keyword must not be blank")
        if len(tokens) > 5 and len(value) > 40:
            raise ValueError("keyword must be a word or short sentence")
        return value


class IdeaRecommendation(BaseModel):
    title: str
    summary: str
    rationale: str
    report_seed: str


class IdeaRecommendationResponse(BaseModel):
    keyword: str
    recommendations: list[IdeaRecommendation]


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


class ResearchStatus(BaseModel):
    requested: bool
    search_provider: Literal["gemini_cli", "fallback", "not_requested"]
    search_status: Literal["success", "fallback", "skipped"]
    organization_provider: Literal["gemma4", "fallback", "not_requested"]
    organization_status: Literal["success", "fallback", "skipped"]
    notes: list[str]


class IdeaReportResponse(BaseModel):
    overview: str
    clarified_concept: str
    target_users: list[str]
    core_use_cases: list[str]
    strengths: list[str]
    weaknesses: list[str]
    differentiation_opportunities: list[str]
    key_risks: list[str]
    build_complexity: str
    recommended_mvp_scope: list[str]
    domestic_competitors: list[Competitor]
    overseas_competitors: list[Competitor]
    source_references: list[SourceReference]
    next_validation_steps: list[str]
    research_status: ResearchStatus

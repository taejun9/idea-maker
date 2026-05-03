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


class IdeaRecommendationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    keyword: str = Field(min_length=1, max_length=80)
    locale: str = Field(default="ko-KR")

    @field_validator("keyword")
    @classmethod
    def keyword_must_be_single_word(cls, value: str) -> str:
        if len(value.split()) != 1:
            raise ValueError("keyword must contain exactly one word")
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

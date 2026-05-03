from datetime import date, datetime
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


BUSINESS_FIELD_OPTIONS = (
    "IT",
    "교육",
    "금융",
    "운영관리",
    "네트워킹",
    "농축/수산업",
    "라이프스타일",
    "마케팅/PR",
    "모빌리티",
    "미디어/엔터테인먼트",
    "바이오/의류",
    "에너지/자원",
    "유통/물류",
    "임팩트",
    "재무",
    "프롭테크",
    "하드웨어",
    "기타",
)

IdeaIntakeCode = Literal["Q1", "Q2", "Q3", "Q4", "Q5"]


class IdeaIntakeAnswerInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    code: IdeaIntakeCode
    answer: str = Field(min_length=1, max_length=2000)


class IdeaIntakeQuestion(BaseModel):
    code: IdeaIntakeCode
    prompt: str
    requirement: str
    photo_guidance: str | None = None
    options: list[str] = Field(default_factory=list)
    answer: str = ""


def default_idea_intake_questions() -> list[IdeaIntakeQuestion]:
    return idea_intake_questions_from_answers([])


def idea_intake_questions_from_answers(
    answers: list[IdeaIntakeAnswerInput],
) -> list[IdeaIntakeQuestion]:
    answers_by_code = {answer.code: answer.answer for answer in answers}
    return [
        IdeaIntakeQuestion(
            code="Q1",
            prompt="나의 아이디어를 한 줄로 소개해주세요.",
            requirement="자동 생성",
            answer=answers_by_code.get("Q1", ""),
        ),
        IdeaIntakeQuestion(
            code="Q2",
            prompt="아이디어를 떠올린 배경 이야기를 들려주세요.",
            requirement="자동 생성",
            answer=answers_by_code.get("Q2", ""),
        ),
        IdeaIntakeQuestion(
            code="Q3",
            prompt="아이디어는 누구의 어떤 문제를 해결해주나요?",
            requirement="자동 생성",
            answer=answers_by_code.get("Q3", ""),
        ),
        IdeaIntakeQuestion(
            code="Q4",
            prompt="아이디어를 어떻게 실현하고 싶으신가요?",
            requirement="자동 생성",
            answer=answers_by_code.get("Q4", ""),
        ),
        IdeaIntakeQuestion(
            code="Q5",
            prompt="사업 분야를 선택해주세요.",
            requirement="필수",
            options=list(BUSINESS_FIELD_OPTIONS),
            answer=answers_by_code.get("Q5", ""),
        ),
    ]


class IdeaReportRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    idea: str = Field(min_length=5, max_length=2000)
    locale: str = Field(default="ko-KR")
    research: bool = Field(default=False)
    idea_intake_answers: list[IdeaIntakeAnswerInput] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_idea_intake_answers(self) -> Self:
        if not self.idea_intake_answers:
            return self

        answers_by_code = {answer.code: answer.answer for answer in self.idea_intake_answers}
        if len(answers_by_code) != len(self.idea_intake_answers):
            raise ValueError("idea_intake_answers must not contain duplicate question codes")
        q5_answer = answers_by_code.get("Q5")
        if q5_answer is not None and q5_answer not in BUSINESS_FIELD_OPTIONS:
            raise ValueError("Q5 answer must be one of the business field options")
        return self


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
    id: str
    idea: str
    locale: str
    created_at: datetime
    overview: str
    idea_intake_questions: list[IdeaIntakeQuestion] = Field(
        default_factory=default_idea_intake_questions
    )
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


class IdeaReportSummary(BaseModel):
    id: str
    idea: str
    created_at: datetime
    overview: str
    research_requested: bool
    domestic_competitor_count: int
    overseas_competitor_count: int
    source_reference_count: int


class IdeaReportListResponse(BaseModel):
    reports: list[IdeaReportSummary]

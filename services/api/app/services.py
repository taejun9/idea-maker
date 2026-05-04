import hashlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime
from random import Random, SystemRandom
from typing import Protocol
from uuid import uuid4

from services.api.app.core.settings import (
    ai_generation_cache_max_entries,
    ai_generation_cache_ttl_seconds,
)
from services.api.app.core.ttl_cache import TtlCache
from services.api.app.integrations.research_adapters import (
    BusinessContextGenerationResult,
    GeminiCliSearchAdapter,
    GeneratedIdeaRecommendation,
    IdeaRecommendationsGenerationResult,
    LocalGemmaBusinessContextGenerator,
    LocalGemmaIdeaRecommendationGenerator,
    LocalGemmaOrganizer,
    LocalGemmaQuickIdeaExampleGenerator,
    OrganizationResult,
    QuickIdeaExamplesGenerationResult,
    SearchAdapterResult,
    organization_fallback,
)
from services.api.app.integrations.source_collectors import (
    Market,
    NormalizedSourceRecord,
    collect_source_records,
)
from services.api.app.schemas import (
    BUSINESS_FIELD_OPTIONS,
    Competitor,
    IdeaIntakeAnswerInput,
    IdeaRecommendation,
    IdeaRecommendationRequest,
    IdeaRecommendationResponse,
    IdeaReportListResponse,
    IdeaReportRequest,
    IdeaReportResponse,
    IdeaReportSummary,
    QuickIdeaExample,
    QuickIdeaExampleResponse,
    ResearchStatus,
    SourceReference,
    idea_intake_questions_from_answers,
)

RECOMMENDATION_PATTERNS = (
    {
        "fields": ("마케팅/PR", "운영관리"),
        "title": "{keyword} 고객 반응 분석 도구",
        "summary": "{keyword} 관련 리뷰, 문의, 피드백을 모아 반복 이슈를 보여주는 운영 도구",
        "rationale": "고객 목소리를 구조화하면 초기 MVP 문제 정의와 경쟁 분석이 쉬워집니다.",
        "report_seed": (
            "{keyword} 관련 고객 리뷰와 문의를 자동으로 분석해 "
            "개선 우선순위를 제안하는 SaaS"
        ),
    },
    {
        "fields": ("운영관리", "IT"),
        "title": "{keyword} 업무 자동화 체크리스트",
        "summary": "{keyword} 업무를 단계별 체크리스트와 자동 알림으로 관리하는 팀 생산성 도구",
        "rationale": "한 단어 아이디어를 반복 업무 절감이라는 명확한 가치로 확장합니다.",
        "report_seed": "{keyword} 업무를 체크리스트와 자동 알림으로 표준화하는 팀 생산성 서비스",
    },
    {
        "fields": ("공통",),
        "title": "{keyword} 시장 기회 대시보드",
        "summary": "{keyword} 관련 경쟁 서비스, 가격, 사용자 반응을 한 화면에 정리하는 리서치 도구",
        "rationale": "시장 조사와 포지셔닝을 먼저 확인해야 보고서의 경쟁 분석 품질이 올라갑니다.",
        "report_seed": "{keyword} 분야의 경쟁 서비스와 사용자 반응을 추적하는 시장 기회 대시보드",
    },
    {
        "fields": ("공통", "라이프스타일", "미디어/엔터테인먼트"),
        "title": "{keyword} 맞춤 추천 큐레이터",
        "summary": (
            "사용자 상황을 받아 {keyword} 관련 콘텐츠, 서비스, 실행 과제를 추천하는 "
            "큐레이션 서비스"
        ),
        "rationale": (
            "넓은 키워드를 개인화 추천 문제로 좁히면 대상 사용자와 사용 사례를 잡기 쉽습니다."
        ),
        "report_seed": (
            "사용자 상황에 맞춰 {keyword} 관련 콘텐츠와 실행 과제를 추천하는 큐레이션 서비스"
        ),
    },
    {
        "fields": ("교육",),
        "title": "{keyword} 학습 루틴 코치",
        "summary": "{keyword} 학습 기록을 받아 다음 복습 과제와 피드백을 제안하는 교육 앱",
        "rationale": "학습 맥락으로 좁히면 사용자, 반복 행동, 성과 지표가 명확해집니다.",
        "report_seed": "{keyword} 학습 기록을 분석해 개인별 복습 루틴을 추천하는 교육 코치 앱",
    },
    {
        "fields": ("금융", "재무"),
        "title": "{keyword} 비용 알림 플래너",
        "summary": "{keyword} 관련 지출, 수수료, 갱신 일정을 모아 절약 행동을 알려주는 도구",
        "rationale": "금융/재무 아이디어는 비교와 알림 중심 MVP로 빠르게 검증할 수 있습니다.",
        "report_seed": "{keyword} 비용과 조건 변화를 추적해 절약 행동을 제안하는 재무 관리 서비스",
    },
    {
        "fields": ("유통/물류",),
        "title": "{keyword} 재고·반품 관리 보드",
        "summary": "{keyword} 판매 흐름에서 재고 부족, 반품 사유, 처리 상태를 관리하는 운영 보드",
        "rationale": "커머스 문제는 현장 운영자가 매일 보는 상태 관리 화면으로 시작하기 좋습니다.",
        "report_seed": (
            "{keyword} 판매자의 재고와 반품 이슈를 한 화면에서 관리하는 "
            "커머스 운영 도구"
        ),
    },
    {
        "fields": ("네트워킹",),
        "title": "{keyword} 목적 기반 매칭 서비스",
        "summary": "{keyword} 관심사와 목적을 입력하면 대화할 사람과 첫 메시지를 추천하는 서비스",
        "rationale": "네트워킹 아이디어는 매칭 기준과 후속 행동을 함께 검증해야 합니다.",
        "report_seed": (
            "{keyword} 관심사를 기반으로 적합한 사람과 첫 대화 주제를 "
            "추천하는 매칭 서비스"
        ),
    },
    {
        "fields": ("미디어/엔터테인먼트",),
        "title": "{keyword} 콘텐츠 기획 캘린더",
        "summary": "{keyword} 소재를 짧은 콘텐츠 기획안, 일정, 배포 체크리스트로 바꾸는 도구",
        "rationale": (
            "콘텐츠 분야는 반복 제작 과정을 줄이는 작은 워크플로우부터 "
            "검증할 수 있습니다."
        ),
        "report_seed": "{keyword} 소재를 숏폼 콘텐츠 기획안과 배포 일정으로 변환하는 제작 도구",
    },
    {
        "fields": ("라이프스타일",),
        "title": "{keyword} 생활 루틴 실험 앱",
        "summary": "{keyword} 목표를 작은 일일 실험과 기록 카드로 쪼개 지속 여부를 확인하는 앱",
        "rationale": "라이프스타일 아이디어는 가벼운 반복 사용과 성취 피드백이 핵심입니다.",
        "report_seed": "{keyword} 목표를 일일 실험과 기록 루틴으로 관리하는 라이프스타일 앱",
    },
    {
        "fields": ("IT",),
        "title": "{keyword} 노코드 워크플로우 봇",
        "summary": "{keyword} 관련 반복 입력, 분류, 알림을 노코드 규칙으로 자동화하는 SaaS",
        "rationale": "IT 아이디어는 좁은 반복 업무 자동화로 초기 가치를 빠르게 보여줄 수 있습니다.",
        "report_seed": "{keyword} 반복 업무를 노코드 규칙과 알림으로 자동화하는 워크플로우 SaaS",
    },
    {
        "fields": ("공통",),
        "title": "{keyword} 검증 랜딩 실험 키트",
        "summary": "{keyword} 가설, 랜딩 문구, 인터뷰 질문, 신청 폼을 한 번에 만드는 검증 도구",
        "rationale": "구현 전 수요를 확인할 수 있어 실제 MVP 범위를 줄이는 데 도움이 됩니다.",
        "report_seed": "{keyword} 아이디어의 랜딩 페이지 문구와 인터뷰 질문을 생성하는 검증 키트",
    },
    {
        "fields": ("공통",),
        "title": "{keyword} 전문가 상담 마켓",
        "summary": (
            "{keyword} 문제를 가진 사용자와 짧은 상담을 제공할 전문가를 "
            "연결하는 마켓플레이스"
        ),
        "rationale": "전문가 연결형 MVP는 공급자와 수요자의 반복 문제를 빠르게 확인할 수 있습니다.",
        "report_seed": (
            "{keyword} 문제 해결을 원하는 사용자와 전문가를 연결하는 "
            "짧은 상담 마켓플레이스"
        ),
    },
)

BUSINESS_FIELD_KEYWORDS = (
    ("교육", ("교육", "학습", "스터디", "강의", "출석", "학교", "학생")),
    ("금융", ("금융", "대출", "보험", "결제", "송금", "은행")),
    ("재무", ("재무", "회계", "세금", "정산", "예산", "비용")),
    ("마케팅/PR", ("리뷰", "마케팅", "광고", "홍보", "pr", "피드백", "고객 반응", "문의")),
    ("유통/물류", ("쇼핑몰", "반품", "배송", "재고", "물류", "유통", "커머스")),
    ("운영관리", ("운영", "업무", "자동화", "체크리스트", "관리", "매장", "소상공인")),
    ("네트워킹", ("네트워킹", "커뮤니티", "모임", "매칭", "연결")),
    ("모빌리티", ("모빌리티", "차량", "주차", "교통", "이동", "배달")),
    ("미디어/엔터테인먼트", ("콘텐츠", "미디어", "영상", "음악", "엔터테인먼트")),
    ("바이오/의류", ("바이오", "헬스케어", "의료", "건강", "의류", "패션")),
    ("에너지/자원", ("에너지", "전력", "자원", "탄소", "전기")),
    ("농축/수산업", ("농업", "축산", "수산", "농장", "어업")),
    ("라이프스타일", ("생활", "라이프스타일", "취미", "여행", "가정")),
    ("프롭테크", ("부동산", "임대", "주거", "건물", "프롭테크")),
    ("하드웨어", ("하드웨어", "기기", "센서", "로봇", "디바이스")),
    ("임팩트", ("임팩트", "환경", "기부", "복지", "사회문제")),
    ("IT", ("ai", "인공지능", "saas", "소프트웨어", "앱", "플랫폼", "데이터", "챗봇")),
)

AI_BUSINESS_CONTEXT_FIELDS = frozenset(
    (
        "IT",
        "교육",
        "금융",
        "라이프스타일",
        "마케팅/PR",
        "미디어/엔터테인먼트",
    )
)


@dataclass(frozen=True)
class BusinessFieldReportContext:
    users: tuple[str, str, str]
    job: str
    outcome: str
    adoption_risk: str
    differentiation_focus: str
    mvp_capability: str


@dataclass(frozen=True)
class ReportSections:
    target_users: tuple[str, ...]
    core_use_cases: tuple[str, ...]
    strengths: tuple[str, ...]
    weaknesses: tuple[str, ...]
    differentiation_opportunities: tuple[str, ...]
    key_risks: tuple[str, ...]
    recommended_mvp_scope: tuple[str, ...]
    next_validation_steps: tuple[str, ...]


BUSINESS_FIELD_REPORT_CONTEXTS = {
    "IT": BusinessFieldReportContext(
        users=(
            "개발자와 데이터 실무자",
            "사내 소프트웨어 도입 담당자",
            "반복 업무 자동화를 원하는 운영팀",
        ),
        job="데이터와 워크플로우를 연결해 반복 판단을 줄이는 일",
        outcome="업무 처리 시간과 오류 감소",
        adoption_risk="기존 시스템 연동, 데이터 품질, 보안 검토",
        differentiation_focus="빠른 설정, 기존 SaaS 연동, 한국어 업무 맥락",
        mvp_capability="핵심 워크플로우 자동화와 상태 대시보드",
    ),
    "교육": BusinessFieldReportContext(
        users=("학습자와 보호자", "강사와 학원 운영자", "교육 콘텐츠 기획자"),
        job="학습 상태를 파악하고 다음 학습 행동을 정하는 일",
        outcome="학습 지속률과 성취도 개선",
        adoption_risk="학습 데이터 신뢰도, 보호자 설득, 학교/학원 운영 방식 적합성",
        differentiation_focus="개인별 학습 맥락과 실행 루틴까지 연결하는 경험",
        mvp_capability="학습 기록 수집, 진단, 다음 학습 추천",
    ),
    "금융": BusinessFieldReportContext(
        users=("금융 상품을 비교하는 개인", "소상공인 자금 담당자", "금융 상담 실무자"),
        job="조건과 리스크를 비교해 안전한 금융 결정을 내리는 일",
        outcome="비용 절감과 의사결정 시간 단축",
        adoption_risk="규제 준수, 설명 책임, 최신 상품 조건 반영",
        differentiation_focus="이해하기 쉬운 조건 비교와 행동 가능한 안내",
        mvp_capability="상품 조건 입력, 비교표, 알림",
    ),
    "운영관리": BusinessFieldReportContext(
        users=("현장 운영 매니저", "소상공인과 점장", "반복 업무를 관리하는 팀 리더"),
        job="매일 반복되는 운영 업무를 누락 없이 관리하는 일",
        outcome="운영 누락 감소와 처리 속도 개선",
        adoption_risk="현장 사용 습관, 모바일 접근성, 기존 업무표와의 중복",
        differentiation_focus="현장 언어로 정리된 체크리스트와 실행 알림",
        mvp_capability="업무 체크리스트, 담당자 배정, 완료 기록",
    ),
    "네트워킹": BusinessFieldReportContext(
        users=("커뮤니티 운영자", "행사 참가자", "관심사 기반 연결이 필요한 전문가"),
        job="적절한 사람을 발견하고 관계 형성의 첫 행동을 만드는 일",
        outcome="유효 연결 수와 후속 대화율 증가",
        adoption_risk="프로필 신뢰도, 매칭 품질, 커뮤니티 안전 관리",
        differentiation_focus="관심사와 목적을 반영한 고신뢰 매칭",
        mvp_capability="프로필 수집, 관심사 태깅, 추천 연결",
    ),
    "농축/수산업": BusinessFieldReportContext(
        users=(
            "농장과 양식장 운영자",
            "농축수산 유통 담당자",
            "현장 데이터를 기록하는 작업자",
        ),
        job="생산 현장의 상태를 기록하고 이상 징후를 빠르게 판단하는 일",
        outcome="손실 감소와 생산 예측 정확도 개선",
        adoption_risk="현장 입력 부담, 센서/통신 환경, 계절성 데이터 편차",
        differentiation_focus="현장 친화적인 기록 방식과 조기 경보",
        mvp_capability="현장 기록, 이상 알림, 간단한 추세표",
    ),
    "라이프스타일": BusinessFieldReportContext(
        users=(
            "개인 생활 루틴을 관리하는 사용자",
            "가정과 취미 일정을 조율하는 사람",
            "맞춤 추천을 원하는 소비자",
        ),
        job="일상 선택과 루틴을 가볍게 관리하는 일",
        outcome="루틴 지속률과 만족도 개선",
        adoption_risk="사용 빈도 유지, 개인정보 민감도, 추천 피로도",
        differentiation_focus="생활 맥락에 맞춘 작은 행동 추천",
        mvp_capability="루틴 입력, 추천, 알림",
    ),
    "마케팅/PR": BusinessFieldReportContext(
        users=("마케팅 담당자", "브랜드 운영자", "고객 반응을 관리하는 소상공인"),
        job="고객 반응을 읽고 다음 커뮤니케이션을 정하는 일",
        outcome="반응률, 전환율, 부정 이슈 대응 속도 개선",
        adoption_risk="채널별 데이터 접근, 브랜드 톤 일관성, 성과 측정",
        differentiation_focus="고객 반응을 실행 가능한 메시지와 캠페인으로 연결",
        mvp_capability="반응 수집, 이슈 분류, 메시지 초안",
    ),
    "모빌리티": BusinessFieldReportContext(
        users=(
            "이동 서비스를 이용하는 사용자",
            "차량/주차 운영자",
            "배송과 이동 경로를 관리하는 팀",
        ),
        job="이동 자원과 경로를 더 효율적으로 배분하는 일",
        outcome="대기 시간, 이동 비용, 운영 공백 감소",
        adoption_risk="위치 데이터 정확도, 실시간성, 안전 책임",
        differentiation_focus="지역별 이동 맥락과 운영 제약을 반영한 추천",
        mvp_capability="위치 입력, 경로/자원 추천, 상태 알림",
    ),
    "미디어/엔터테인먼트": BusinessFieldReportContext(
        users=("콘텐츠 크리에이터", "팬 커뮤니티 운영자", "공연/미디어 기획자"),
        job="콘텐츠 반응을 읽고 다음 제작 또는 배포 결정을 내리는 일",
        outcome="콘텐츠 참여율과 재방문율 개선",
        adoption_risk="플랫폼 데이터 접근, 저작권, 팬덤 반응 변동성",
        differentiation_focus="팬 반응과 제작 루틴을 함께 보는 운영 경험",
        mvp_capability="콘텐츠 일정, 반응 수집, 다음 액션 추천",
    ),
    "바이오/의류": BusinessFieldReportContext(
        users=("건강 또는 패션 소비자", "브랜드 운영자", "상담과 추천을 제공하는 실무자"),
        job="개인 특성과 기록을 바탕으로 적합한 선택을 돕는 일",
        outcome="추천 만족도와 교환/재상담 감소",
        adoption_risk="개인정보 보호, 전문성 검증, 신뢰 형성",
        differentiation_focus="개인 상태와 취향을 함께 반영한 추천",
        mvp_capability="개인 프로필 입력, 추천, 결과 피드백",
    ),
    "에너지/자원": BusinessFieldReportContext(
        users=("건물 에너지 관리자", "상가 운영자", "자원 절감 목표를 가진 조직"),
        job="사용량을 파악하고 절감 행동을 우선순위화하는 일",
        outcome="비용 절감과 탄소 저감",
        adoption_risk="계량 데이터 접근, 설비 편차, 절감 효과 검증",
        differentiation_focus="비전문가도 이해하는 절감 행동 추천",
        mvp_capability="사용량 입력, 절감 포인트, 효과 추적",
    ),
    "유통/물류": BusinessFieldReportContext(
        users=("커머스 운영자", "물류 담당자", "재고와 배송을 관리하는 소규모 팀"),
        job="재고, 주문, 배송 흐름을 예측하고 병목을 줄이는 일",
        outcome="재고 부족, 배송 지연, 반품 비용 감소",
        adoption_risk="주문 데이터 연동, 예측 정확도, 예외 상황 처리",
        differentiation_focus="소규모 운영자가 바로 쓰는 예측과 알림",
        mvp_capability="주문/재고 입력, 위험 알림, 처리 우선순위",
    ),
    "임팩트": BusinessFieldReportContext(
        users=(
            "비영리 운영자",
            "사회문제 해결 프로젝트 팀",
            "임팩트 지표를 관리하는 기관",
        ),
        job="활동 결과를 측정하고 이해관계자에게 설명하는 일",
        outcome="참여율, 자원 배분 효율, 임팩트 설명력 개선",
        adoption_risk="성과 측정 기준 합의, 개인정보, 현장 입력 부담",
        differentiation_focus="사회적 성과와 실행 데이터를 함께 보여주는 방식",
        mvp_capability="활동 기록, 수혜/참여 지표, 리포트",
    ),
    "재무": BusinessFieldReportContext(
        users=("프리랜서와 소상공인", "팀 예산 담당자", "회계/정산 실무자"),
        job="돈의 흐름을 기록하고 다음 정산·예산 결정을 내리는 일",
        outcome="정산 누락, 비용 초과, 세무 준비 시간 감소",
        adoption_risk="거래 데이터 정확도, 회계 규칙, 책임 소재",
        differentiation_focus="비전문가도 이해하는 정산 흐름과 알림",
        mvp_capability="거래 입력, 분류, 정산 일정 알림",
    ),
    "프롭테크": BusinessFieldReportContext(
        users=("임대인과 건물 관리자", "부동산 중개팀", "주거/상업 공간 운영자"),
        job="공간 상태와 거래 정보를 최신으로 관리하는 일",
        outcome="공실 기간, 민원 처리 시간, 정보 누락 감소",
        adoption_risk="매물 정보 정확도, 현장 업데이트, 이해관계자 권한",
        differentiation_focus="현장 상태와 의사결정을 연결하는 공간 운영 경험",
        mvp_capability="매물/공간 상태 입력, 알림, 요약",
    ),
    "하드웨어": BusinessFieldReportContext(
        users=("기기 운영자", "제조/정비 담당자", "센서 데이터를 확인하는 현장팀"),
        job="장비 상태를 확인하고 고장을 예방하는 일",
        outcome="다운타임과 정비 비용 감소",
        adoption_risk="센서 신뢰도, 설치 비용, 현장 유지보수",
        differentiation_focus="설치와 해석이 쉬운 상태 진단",
        mvp_capability="기기 상태 입력, 이상 감지, 정비 로그",
    ),
    "기타": BusinessFieldReportContext(
        users=(
            "초기 문제를 직접 겪는 사용자",
            "문제 해결을 검토하는 운영자",
            "검증할 시장을 찾는 창업자",
        ),
        job="문제를 구체화하고 첫 실행 범위를 정하는 일",
        outcome="검증 속도와 문제 정의 선명도 개선",
        adoption_risk="대상 사용자 정의, 지불 의사, 반복 사용성",
        differentiation_focus="특정 사용자 맥락에 깊게 맞춘 문제 해결",
        mvp_capability="문제 입력, 우선순위 정리, 검증 체크리스트",
    ),
}

@dataclass(frozen=True)
class QuickExampleFallbackScenario:
    problem: str
    capability: str
    outcome: str


@dataclass(frozen=True)
class QuickExampleFallbackContext:
    users: tuple[str, ...]
    scenarios: tuple[QuickExampleFallbackScenario, ...]
    product_types: tuple[str, ...]


@dataclass(frozen=True)
class QuickExampleFallbackParts:
    user: str
    scenario: QuickExampleFallbackScenario
    product_type: str


QUICK_EXAMPLE_CONTEXT_TEMPLATES = (
    "{user} 대상 {mvp_capability} 기능을 바로 쓰는 {product_type}",
    "{field} 현장에서 {job}을 빠르게 처리하는 {product_type}",
    "{user} 대상 {outcome} 성과를 확인하는 {product_type}",
    "{field} 팀을 위한 {differentiation_focus} 중심 {product_type}",
    "도입 전 {adoption_risk} 항목을 점검하는 {field} {product_type}",
)

QUICK_EXAMPLE_PRODUCT_TYPES = (
    "SaaS",
    "앱",
    "대시보드",
    "워크플로우 도구",
    "알림 서비스",
    "리포트 자동화 도구",
)

QUICK_EXAMPLE_FALLBACK_TEMPLATES = (
    "{user} 대상 {capability} 기능으로 {problem} 문제를 줄이는 {product_type}",
    "{user}에게 {outcome} 성과를 안내하고 {problem} 문제를 정리하는 {product_type}",
    "{user}용 {product_type}: {capability} 기능으로 {problem} 문제를 관리",
    "{user} 대상 {outcome} 성과를 돕는 {capability} 기반 {product_type}",
)

QUICK_EXAMPLE_FALLBACK_CONTEXTS = {
    "IT": QuickExampleFallbackContext(
        users=(
            "사내 운영팀",
            "B2B SaaS 제품팀",
            "데이터 운영자",
            "개발 리드",
            "보안 담당자",
        ),
        scenarios=(
            QuickExampleFallbackScenario(
                problem="반복 승인 요청 누락",
                capability="승인 흐름 자동 분류와 담당자 알림",
                outcome="처리 우선순위 확인",
            ),
            QuickExampleFallbackScenario(
                problem="장애 원인 정리 지연",
                capability="로그 요약과 원인 후보 추적",
                outcome="장애 대응 시간 단축",
            ),
            QuickExampleFallbackScenario(
                problem="고객 문의 속 기능 요청 누락",
                capability="문의 태깅과 기능 요청 군집화",
                outcome="제품 개선 후보 선별",
            ),
            QuickExampleFallbackScenario(
                problem="배포 전 점검 항목 분산",
                capability="릴리스 체크리스트 자동 검수",
                outcome="배포 리스크 사전 점검",
            ),
            QuickExampleFallbackScenario(
                problem="권한 변경 이력 추적 부담",
                capability="권한 변경 알림과 감사 리포트",
                outcome="보안 검토 누락 감소",
            ),
        ),
        product_types=("SaaS", "대시보드", "워크플로우 도구", "알림 서비스"),
    ),
    "교육": QuickExampleFallbackContext(
        users=(
            "초등 학습자",
            "방과후 교사",
            "학원 운영자",
            "온라인 강의 튜터",
            "학부모 코치",
        ),
        scenarios=(
            QuickExampleFallbackScenario(
                problem="오답 원인 파악 지연",
                capability="오답 패턴 분석과 다음 문제 추천",
                outcome="개인별 복습 우선순위 제안",
            ),
            QuickExampleFallbackScenario(
                problem="출결과 과제 확인 반복",
                capability="출결·과제 자동 체크와 보호자 알림",
                outcome="수업 운영 시간 절감",
            ),
            QuickExampleFallbackScenario(
                problem="수준별 복습 계획 부족",
                capability="수준별 복습 루틴 생성",
                outcome="학습 공백 조기 발견",
            ),
            QuickExampleFallbackScenario(
                problem="질문 답변 대기 시간 증가",
                capability="질문 분류와 튜터 답변 초안",
                outcome="질문 응답 속도 개선",
            ),
            QuickExampleFallbackScenario(
                problem="학습 습관 유지 어려움",
                capability="짧은 학습 목표와 보상 루프",
                outcome="꾸준한 학습 루틴 형성",
            ),
        ),
        product_types=("학습 앱", "튜터 대시보드", "알림 서비스", "코칭 도구"),
    ),
}

QUICK_EXAMPLE_FIELDS = (
    "IT",
    "교육",
)

QUICK_EXAMPLE_DEFAULT_COUNT = 2


class IdeaReportRepository(Protocol):
    def save_report(self, report: IdeaReportResponse) -> None:
        ...

    def list_reports(self, *, limit: int) -> list[IdeaReportResponse]:
        ...

    def get_report(self, report_id: str) -> IdeaReportResponse | None:
        ...

    def delete_report(self, report_id: str) -> bool:
        ...


class BusinessContextGenerator(Protocol):
    def generate(
        self,
        *,
        business_field: str,
    ) -> BusinessContextGenerationResult:
        ...


class QuickIdeaExampleGenerator(Protocol):
    def generate(
        self,
        *,
        fields: tuple[str, ...],
    ) -> QuickIdeaExamplesGenerationResult:
        ...


class IdeaRecommendationGenerator(Protocol):
    def generate(
        self,
        *,
        keyword: str,
    ) -> IdeaRecommendationsGenerationResult:
        ...


_BUSINESS_CONTEXT_CACHE = TtlCache[BusinessContextGenerationResult](
    ttl_seconds=ai_generation_cache_ttl_seconds(),
    max_entries=ai_generation_cache_max_entries(),
)
_IDEA_RECOMMENDATIONS_CACHE = TtlCache[IdeaRecommendationsGenerationResult](
    ttl_seconds=ai_generation_cache_ttl_seconds(),
    max_entries=ai_generation_cache_max_entries(),
)


def create_quick_idea_examples(
    *,
    count: int = QUICK_EXAMPLE_DEFAULT_COUNT,
    random_source: Random | SystemRandom | None = None,
    context_generator: BusinessContextGenerator | None = None,
    example_generator: QuickIdeaExampleGenerator | None = None,
) -> QuickIdeaExampleResponse:
    randomizer = random_source or SystemRandom()
    example_fields = list(QUICK_EXAMPLE_FIELDS)
    randomizer.shuffle(example_fields)
    selected_fields = example_fields[: max(0, min(count, len(example_fields)))]
    if not selected_fields:
        return QuickIdeaExampleResponse(examples=[])

    generator = example_generator or LocalGemmaQuickIdeaExampleGenerator()
    requested_fields = tuple(selected_fields)
    generated_examples = generator.generate(fields=requested_fields)
    if generated_examples.status == "success":
        return QuickIdeaExampleResponse(
            examples=[
                QuickIdeaExample(field=example.field, idea=example.idea)
                for example in generated_examples.examples
            ],
        )

    return QuickIdeaExampleResponse(
        examples=[
            quick_idea_example_for_field(
                field,
                randomizer,
                context_generator=context_generator,
            )
            for field in selected_fields
        ],
    )


def quick_idea_example_for_field(
    field: str,
    randomizer: Random | SystemRandom,
    *,
    context_generator: BusinessContextGenerator | None = None,
) -> QuickIdeaExample:
    if context_generator is None and field in QUICK_EXAMPLE_FALLBACK_CONTEXTS:
        return quick_idea_example_from_fallback_context(
            field,
            randomizer,
            QUICK_EXAMPLE_FALLBACK_CONTEXTS[field],
        )

    context = (
        business_field_context(field, context_generator=context_generator)
        if context_generator is not None
        else BUSINESS_FIELD_REPORT_CONTEXTS.get(field, BUSINESS_FIELD_REPORT_CONTEXTS["기타"])
    )
    template = randomizer.choice(QUICK_EXAMPLE_CONTEXT_TEMPLATES)
    idea = template.format(
        field=field,
        user=randomizer.choice(context.users),
        job=context.job,
        outcome=context.outcome,
        adoption_risk=context.adoption_risk,
        differentiation_focus=context.differentiation_focus,
        mvp_capability=context.mvp_capability,
        product_type=randomizer.choice(QUICK_EXAMPLE_PRODUCT_TYPES),
    )
    return QuickIdeaExample(field=field, idea=idea)


def quick_idea_example_from_fallback_context(
    field: str,
    randomizer: Random | SystemRandom,
    context: QuickExampleFallbackContext,
) -> QuickIdeaExample:
    template = randomizer.choice(QUICK_EXAMPLE_FALLBACK_TEMPLATES)
    parts = QuickExampleFallbackParts(
        user=randomizer.choice(context.users),
        scenario=randomizer.choice(context.scenarios),
        product_type=randomizer.choice(context.product_types),
    )
    idea = template.format(
        user=parts.user,
        problem=parts.scenario.problem,
        capability=parts.scenario.capability,
        outcome=parts.scenario.outcome,
        product_type=parts.product_type,
    )
    return QuickIdeaExample(field=field, idea=idea)


def create_idea_report(
    payload: IdeaReportRequest,
    *,
    search_adapter: GeminiCliSearchAdapter | None = None,
    organizer: LocalGemmaOrganizer | None = None,
    context_generator: BusinessContextGenerator | None = None,
) -> IdeaReportResponse:
    created_at = datetime.now(tz=UTC)
    observed = created_at.date()
    normalized_idea = payload.idea.strip()
    search_result: SearchAdapterResult | None = None
    organization: OrganizationResult | None = None

    if payload.research:
        search = search_adapter or GeminiCliSearchAdapter()
        with ThreadPoolExecutor(max_workers=2) as executor:
            baseline_records_future = executor.submit(
                collect_source_records,
                idea=normalized_idea,
                observed_date=observed,
            )
            search_result_future = executor.submit(
                search.search,
                idea=normalized_idea,
                observed_date=observed,
            )
            baseline_records = baseline_records_future.result()
            search_result = search_result_future.result()
        source_records = merge_source_records(
            [*search_result.records, *baseline_records],
        )
        organization = (organizer or LocalGemmaOrganizer()).organize(
            idea=normalized_idea,
            records=source_records,
        )
    else:
        baseline_records = collect_source_records(
            idea=normalized_idea,
            observed_date=observed,
        )
        source_records = baseline_records
        organization = default_report_organization()

    organization = organization or organization_fallback(
        normalized_idea,
        "Research organization was not requested.",
    )
    business_field = submitted_business_field(
        payload.idea_intake_answers
    ) or infer_business_field(normalized_idea)
    sections = report_sections_for_idea(
        idea=normalized_idea,
        business_field=business_field,
        organization=organization,
        context_generator=context_generator,
    )
    idea_intake_answers = generated_idea_intake_answers(
        idea=normalized_idea,
        business_field=business_field,
        sections=sections,
    )

    return IdeaReportResponse(
        id=str(uuid4()),
        idea=normalized_idea,
        locale=payload.locale,
        created_at=created_at,
        overview=report_overview(normalized_idea, payload.research, organization),
        idea_intake_questions=idea_intake_questions_from_answers(idea_intake_answers),
        clarified_concept=(
            f"'{normalized_idea}' 아이디어를 {business_field} 영역에서 "
            f"{sections.target_users[0]}의 문제를 해결하는 초기 제품으로 정의합니다."
        ),
        target_users=list(sections.target_users),
        core_use_cases=list(sections.core_use_cases),
        strengths=list(sections.strengths),
        weaknesses=list(sections.weaknesses),
        differentiation_opportunities=list(sections.differentiation_opportunities),
        key_risks=list(sections.key_risks),
        build_complexity=(
            "중간: 핵심 보고서 생성은 단순하지만 "
            "최신 소스 검증과 신뢰도 관리는 별도 경계가 필요합니다."
        ),
        recommended_mvp_scope=list(sections.recommended_mvp_scope),
        domestic_competitors=competitors_for_market(source_records, "domestic_kr"),
        overseas_competitors=competitors_for_market(source_records, "overseas"),
        source_references=source_references_from_records(source_records),
        next_validation_steps=list(sections.next_validation_steps),
        research_status=research_status_from_results(
            requested=payload.research,
            search_result=search_result,
            organization=organization,
        ),
    )


def list_idea_reports(
    repository: IdeaReportRepository,
    *,
    limit: int = 50,
) -> IdeaReportListResponse:
    return IdeaReportListResponse(
        reports=[
            summarize_idea_report(report)
            for report in repository.list_reports(limit=limit)
        ],
    )


def get_idea_report(
    repository: IdeaReportRepository,
    *,
    report_id: str,
) -> IdeaReportResponse | None:
    return repository.get_report(report_id)


def delete_idea_report(
    repository: IdeaReportRepository,
    *,
    report_id: str,
) -> bool:
    return repository.delete_report(report_id)


def summarize_idea_report(report: IdeaReportResponse) -> IdeaReportSummary:
    return IdeaReportSummary(
        id=report.id,
        idea=report.idea,
        created_at=report.created_at,
        overview=report.overview,
        business_field=report_business_field(report),
        research_requested=report.research_status.requested,
        domestic_competitor_count=len(report.domestic_competitors),
        overseas_competitor_count=len(report.overseas_competitors),
        source_reference_count=len(report.source_references),
    )


def report_business_field(report: IdeaReportResponse) -> str:
    q5_answer = next(
        (
            question.answer.strip()
            for question in report.idea_intake_questions
            if question.code == "Q5"
        ),
        "",
    )
    return q5_answer


def create_idea_recommendations(
    payload: IdeaRecommendationRequest,
    *,
    recommendation_generator: IdeaRecommendationGenerator | None = None,
) -> IdeaRecommendationResponse:
    keyword = payload.keyword.strip()
    generator = recommendation_generator or LocalGemmaIdeaRecommendationGenerator()
    generation = (
        cached_idea_recommendations(
            generator,
            keyword=keyword,
            locale=payload.locale,
        )
        if recommendation_generator is None
        else generator.generate(keyword=keyword)
    )
    if generation.status == "success":
        return IdeaRecommendationResponse(
            keyword=keyword,
            recommendations=[
                idea_recommendation_from_generated(recommendation)
                for recommendation in generation.recommendations
            ],
        )

    return IdeaRecommendationResponse(
        keyword=keyword,
        recommendations=deterministic_idea_recommendations(keyword),
    )


def idea_recommendation_from_generated(
    recommendation: GeneratedIdeaRecommendation,
) -> IdeaRecommendation:
    return IdeaRecommendation(
        title=recommendation.title,
        summary=recommendation.summary,
        rationale=recommendation.rationale,
        report_seed=recommendation.report_seed,
    )


def cached_idea_recommendations(
    generator: LocalGemmaIdeaRecommendationGenerator,
    *,
    keyword: str,
    locale: str,
) -> IdeaRecommendationsGenerationResult:
    normalized_keyword = normalized_generation_cache_text(keyword)
    return _IDEA_RECOMMENDATIONS_CACHE.get_or_set(
        (
            "idea_recommendations",
            generator.base_url,
            generator.model,
            locale,
            hashlib.sha256(normalized_keyword.encode("utf-8")).hexdigest(),
        ),
        lambda: generator.generate(keyword=keyword),
        cacheable=lambda result: result.status == "success",
    )


def normalized_generation_cache_text(value: str) -> str:
    return " ".join(value.split()).casefold()


def deterministic_idea_recommendations(keyword: str) -> list[IdeaRecommendation]:
    business_field = infer_business_field(keyword)
    field_patterns = [
        pattern
        for pattern in RECOMMENDATION_PATTERNS
        if business_field in pattern["fields"]
    ]
    common_patterns = [
        pattern for pattern in RECOMMENDATION_PATTERNS if "공통" in pattern["fields"]
    ]
    other_patterns = [
        pattern
        for pattern in RECOMMENDATION_PATTERNS
        if business_field not in pattern["fields"] and "공통" not in pattern["fields"]
    ]

    selected_patterns: list[dict[str, object]] = []
    selected_patterns.extend(rotated_patterns(field_patterns, keyword)[:2])
    common_target = 4 - len(selected_patterns)
    selected_patterns.extend(rotated_patterns(common_patterns, keyword)[:common_target])
    if len(selected_patterns) < 4:
        selected_patterns.extend(
            rotated_patterns(other_patterns, keyword)[: 4 - len(selected_patterns)]
        )

    return [
        IdeaRecommendation(
            title=str(pattern["title"]).format(keyword=keyword),
            summary=str(pattern["summary"]).format(keyword=keyword),
            rationale=str(pattern["rationale"]).format(keyword=keyword),
            report_seed=str(pattern["report_seed"]).format(keyword=keyword),
        )
        for pattern in selected_patterns[:4]
    ]


def rotated_patterns(
    patterns: list[dict[str, object]],
    keyword: str,
) -> list[dict[str, object]]:
    if not patterns:
        return []
    offset = sum((index + 1) * ord(character) for index, character in enumerate(keyword))
    offset %= len(patterns)
    return [*patterns[offset:], *patterns[:offset]]


def report_overview(
    idea: str,
    research_requested: bool,
    organization: OrganizationResult,
) -> str:
    if research_requested:
        return (
            f"'{idea}' 아이디어를 추천 아이템 기반 검색과 자료 정리 흐름으로 "
            f"구체화합니다. {organization.summary}"
        )
    return f"'{idea}' 아이디어를 초기 검증 가능한 제품 개념으로 구체화합니다."


def default_report_organization() -> OrganizationResult:
    return OrganizationResult(
        provider="not_requested",
        status="skipped",
        summary="",
        target_users=("초기 창업자", "소규모 제품팀", "시장 조사가 필요한 기획자"),
        core_use_cases=(
            "짧은 아이디어를 입력해 검증 가능한 제품 콘셉트로 정리한다.",
            "국내/해외 유사 서비스를 나눠 보고 포지셔닝 빈틈을 찾는다.",
            "인터뷰와 MVP 실험에 바로 쓸 다음 행동을 정한다.",
        ),
        opportunities=(
            "국내 사용자의 업무 맥락과 언어를 우선 반영한다.",
            "경쟁사 목록보다 검증 질문과 MVP 범위를 함께 제시한다.",
            "출처, 관찰일, 신뢰도를 노출해 시장 사실과 가설을 분리한다.",
        ),
        risks=(
            "fixture-backed 소스는 현재 시장 사실로 주장할 수 없다.",
            "초기 사용자 문제가 충분히 날카롭지 않으면 기능 범위가 퍼질 수 있다.",
            "외부 데이터 접근 정책이 바뀌면 소스 수집 품질이 흔들릴 수 있다.",
        ),
        mvp_scope=(
            "아이디어 입력과 구체화된 콘셉트 생성",
            "국내/해외 경쟁 서비스 분리 표",
            "차별화 기회, 주요 리스크, 다음 검증 단계",
        ),
        notes=(),
    )


def submitted_business_field(submitted_answers: list[IdeaIntakeAnswerInput]) -> str:
    return next(
        (
            answer.answer.strip()
            for answer in submitted_answers
            if answer.code == "Q5" and answer.answer.strip()
        ),
        "",
    )


def report_sections_for_idea(
    *,
    idea: str,
    business_field: str,
    organization: OrganizationResult,
    context_generator: BusinessContextGenerator | None = None,
) -> ReportSections:
    context = business_field_context(
        business_field,
        context_generator=context_generator,
    )
    fallback_sections = deterministic_report_sections(
        idea=idea,
        business_field=business_field,
        context=context,
    )

    if organization.status != "success":
        return fallback_sections

    return ReportSections(
        target_users=tuple(organization.target_users) or fallback_sections.target_users,
        core_use_cases=tuple(organization.core_use_cases) or fallback_sections.core_use_cases,
        strengths=fallback_sections.strengths,
        weaknesses=fallback_sections.weaknesses,
        differentiation_opportunities=(
            tuple(organization.opportunities)
            or fallback_sections.differentiation_opportunities
        ),
        key_risks=tuple(organization.risks) or fallback_sections.key_risks,
        recommended_mvp_scope=tuple(organization.mvp_scope)
        or fallback_sections.recommended_mvp_scope,
        next_validation_steps=fallback_sections.next_validation_steps,
    )


def deterministic_report_sections(
    *,
    idea: str,
    business_field: str,
    context: BusinessFieldReportContext,
) -> ReportSections:
    return ReportSections(
        target_users=(
            f"{context.users[0]} 중 '{idea}'를 가장 먼저 써볼 사용자",
            f"{context.users[1]} 중 {context.job}을 맡는 의사결정자",
            f"{context.users[2]} 중 {context.outcome}을 성과로 확인해야 하는 초기 도입자",
        ),
        core_use_cases=(
            f"'{idea}' 관련 입력을 모아 현재 문제와 우선순위를 정리한다.",
            f"{business_field} 맥락에서 {context.job}을 더 빠르고 일관되게 처리한다.",
            f"{context.outcome}을 확인할 수 있는 요약과 다음 행동을 제공한다.",
        ),
        strengths=(
            f"'{idea}'처럼 구체적인 문제 문장에서 시작해 "
            f"{business_field} 사용자 맥락을 바로 반영할 수 있다.",
            f"{context.job}을 하나의 흐름으로 묶어 초기 MVP 가치가 명확하다.",
            f"{context.outcome}을 검증 지표로 삼아 인터뷰와 실험 결과를 비교하기 쉽다.",
        ),
        weaknesses=(
            f"초기에는 {context.adoption_risk} 때문에 도입 장벽이 생길 수 있다.",
            f"{business_field} 현장의 실제 데이터와 업무 방식이 충분히 "
            "반영되지 않으면 결과 품질이 흔들릴 수 있다.",
            "자동 추천이나 정리 결과는 사용자 검증 전까지 가설로 다뤄야 한다.",
        ),
        differentiation_opportunities=(
            f"{context.differentiation_focus}에 집중하면 범용 도구와 구분된다.",
            f"'{idea}'의 핵심 사용자를 좁혀 첫 워크플로우 완성도를 높인다.",
            f"경쟁 서비스 비교보다 {context.outcome} 검증 지표를 제품 안에 내장한다.",
        ),
        key_risks=(
            f"{context.adoption_risk} 검증이 늦어지면 MVP 사용성이 낮아질 수 있다.",
            f"사용자가 '{idea}' 문제를 자주 겪지 않거나 비용을 지불하지 않으면 "
            "시장성이 제한된다.",
            f"{business_field} 영역의 규정, 데이터 접근, 운영 책임 범위를 "
            "초기에 확인해야 한다.",
        ),
        recommended_mvp_scope=(
            context.mvp_capability,
            f"'{idea}'에 필요한 최소 입력 폼과 결과 요약",
            f"{context.outcome}을 확인하는 간단한 지표와 피드백 수집",
        ),
        next_validation_steps=(
            f"{context.users[0]} 5명에게 '{idea}' 문제 빈도와 현재 해결 방식을 인터뷰한다.",
            f"{business_field} 현장에서 {context.adoption_risk} 관련 도입 제약을 확인한다.",
            f"{context.mvp_capability}만 담은 클릭 가능한 시제품으로 "
            f"{context.outcome} 기대치를 검증한다.",
        ),
    )


def business_field_context(
    business_field: str,
    *,
    context_generator: BusinessContextGenerator | None = None,
) -> BusinessFieldReportContext:
    fallback_context = BUSINESS_FIELD_REPORT_CONTEXTS.get(
        business_field,
        BUSINESS_FIELD_REPORT_CONTEXTS["기타"],
    )
    if business_field not in AI_BUSINESS_CONTEXT_FIELDS:
        return fallback_context

    if context_generator is None:
        generator = LocalGemmaBusinessContextGenerator()
        generated_context = cached_business_context(
            generator,
            business_field=business_field,
        )
    else:
        generated_context = context_generator.generate(business_field=business_field)
    if generated_context.status != "success":
        return fallback_context

    return business_context_from_generation_result(
        generated_context,
        fallback_context=fallback_context,
    )


def business_context_from_generation_result(
    result: BusinessContextGenerationResult,
    *,
    fallback_context: BusinessFieldReportContext,
) -> BusinessFieldReportContext:
    users = tuple(value.strip() for value in result.users if value.strip())[:3]
    values = {
        "job": result.job.strip(),
        "outcome": result.outcome.strip(),
        "adoption_risk": result.adoption_risk.strip(),
        "differentiation_focus": result.differentiation_focus.strip(),
        "mvp_capability": result.mvp_capability.strip(),
    }
    if len(users) != 3 or any(not value for value in values.values()):
        return fallback_context

    return BusinessFieldReportContext(
        users=(users[0], users[1], users[2]),
        job=values["job"],
        outcome=values["outcome"],
        adoption_risk=values["adoption_risk"],
        differentiation_focus=values["differentiation_focus"],
        mvp_capability=values["mvp_capability"],
    )


def cached_business_context(
    generator: LocalGemmaBusinessContextGenerator,
    *,
    business_field: str,
) -> BusinessContextGenerationResult:
    return _BUSINESS_CONTEXT_CACHE.get_or_set(
        ("business_context", generator.base_url, generator.model, business_field),
        lambda: generator.generate(business_field=business_field),
        cacheable=lambda result: result.status == "success",
    )


def clear_ai_generation_caches() -> None:
    _BUSINESS_CONTEXT_CACHE.clear()
    _IDEA_RECOMMENDATIONS_CACHE.clear()


def generated_idea_intake_answers(
    *,
    idea: str,
    business_field: str,
    sections: ReportSections,
) -> list[IdeaIntakeAnswerInput]:
    answers = [
        IdeaIntakeAnswerInput(code="Q1", answer=generated_one_line_idea(idea)),
        IdeaIntakeAnswerInput(
            code="Q2",
            answer=generated_background_story(
                idea=idea,
                business_field=business_field,
                sections=sections,
            ),
        ),
        IdeaIntakeAnswerInput(
            code="Q3",
            answer=generated_user_problem(
                idea=idea,
                business_field=business_field,
                sections=sections,
            ),
        ),
        IdeaIntakeAnswerInput(
            code="Q4",
            answer=generated_realization_plan(
                idea=idea,
                sections=sections,
            ),
        ),
    ]
    answers.append(IdeaIntakeAnswerInput(code="Q5", answer=business_field))
    return answers


def generated_one_line_idea(idea: str) -> str:
    if len(idea) >= 10:
        return bounded_intake_answer(idea)
    return bounded_intake_answer(f"{idea}를 구체화한 초기 제품 아이디어")


def generated_background_story(
    *,
    idea: str,
    business_field: str,
    sections: ReportSections,
) -> str:
    target_user = section_item(sections.target_users, 0, "초기 사용자")
    mvp_capability = section_item(
        sections.recommended_mvp_scope,
        0,
        "핵심 문제를 해결하는 최소 기능",
    )
    return bounded_intake_answer(
        f"'{idea}'는 {business_field} 영역에서 {target_user}가 겪는 "
        f"반복 문제를 줄이기 위해 출발한 아이디어입니다. "
        f"특히 {mvp_capability}이 실제 불편을 줄이는지 "
        "초기 제품 가설로 검증합니다."
    )


def generated_user_problem(
    *,
    idea: str,
    business_field: str,
    sections: ReportSections,
) -> str:
    target_user = section_item(sections.target_users, 0, "초기 사용자")
    core_use_case = section_item(
        sections.core_use_cases,
        1,
        section_item(sections.core_use_cases, 0, "핵심 업무를 더 빠르게 처리한다."),
    )
    return bounded_intake_answer(
        f"핵심 사용자는 {target_user}입니다. "
        f"'{idea}'는 {sentence_fragment(core_use_case)} 과정의 "
        "시간 낭비, 누락, 우선순위 판단 부담을 줄이는 문제를 해결합니다."
    )


def generated_realization_plan(
    *,
    idea: str,
    sections: ReportSections,
) -> str:
    mvp_scope = ", ".join(sections.recommended_mvp_scope[:2])
    if not mvp_scope:
        mvp_scope = f"'{idea}'의 핵심 입력, 결과 요약, 다음 검증 단계 제안"
    first_validation_step = section_item(
        sections.next_validation_steps,
        0,
        "핵심 사용자 인터뷰를 진행한다.",
    )
    return bounded_intake_answer(
        f"MVP는 {mvp_scope}부터 시작합니다. 이후 {first_validation_step} "
        "그 결과를 기준으로 실제 사용 빈도와 지불 의사를 확인하고 "
        "다음 기능 범위를 좁힙니다."
    )


def section_item(values: tuple[str, ...], index: int, fallback: str) -> str:
    if len(values) > index and values[index].strip():
        return values[index]
    return fallback


def sentence_fragment(value: str) -> str:
    stripped = value.strip().rstrip(".。")
    if stripped.endswith("한다"):
        return f"{stripped[:-2]}하는"
    return stripped


def bounded_intake_answer(value: str) -> str:
    if len(value) <= 2000:
        return value
    return f"{value[:1997]}..."


def infer_business_field(idea: str) -> str:
    normalized = idea.lower()
    for field, keywords in BUSINESS_FIELD_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            return field
    return "기타" if "기타" in BUSINESS_FIELD_OPTIONS else BUSINESS_FIELD_OPTIONS[0]


def merge_source_records(records: list[NormalizedSourceRecord]) -> list[NormalizedSourceRecord]:
    deduped: dict[str, NormalizedSourceRecord] = {}
    for record in records:
        deduped[f"{record.source_name}:{record.url}"] = record
    return list(deduped.values())


def research_status_from_results(
    *,
    requested: bool,
    search_result: SearchAdapterResult | None,
    organization: OrganizationResult,
) -> ResearchStatus:
    if not requested:
        return ResearchStatus(
            requested=False,
            search_provider="not_requested",
            search_status="skipped",
            organization_provider="not_requested",
            organization_status="skipped",
            notes=[],
        )

    notes = [
        *(search_result.notes if search_result else ()),
        *organization.notes,
    ]
    return ResearchStatus(
        requested=True,
        search_provider=search_result.provider if search_result else "fallback",
        search_status=search_result.status if search_result else "fallback",
        organization_provider=organization.provider,
        organization_status=organization.status,
        notes=list(notes),
    )


def competitors_for_market(
    records: list[NormalizedSourceRecord], market: Market
) -> list[Competitor]:
    return [
        Competitor(
            name=record.title,
            market=record.market,
            summary=record.summary,
            strengths=list(record.strengths),
            weaknesses=list(record.weaknesses),
            source_url=record.url,
            observed_date=record.observed_date,
            confidence=record.confidence,
        )
        for record in records
        if record.market == market
    ]


def source_references_from_records(records: list[NormalizedSourceRecord]) -> list[SourceReference]:
    references: dict[str, SourceReference] = {}
    for record in records:
        references[f"{record.source_name}:{record.url}"] = SourceReference(
            source_name=record.source_name,
            source_url=record.url,
            observed_date=record.observed_date,
            note=source_reference_note(record),
            confidence=record.confidence,
        )
    return list(references.values())


def source_reference_note(record: NormalizedSourceRecord) -> str:
    if record.category == "Gemini CLI grounded search result":
        return (
            "Gemini CLI grounded search result. "
            "The selected recommendation seed was sent to Gemini CLI for public-source search; "
            "verify current facts before external claims."
        )

    if record.access_method == "live_http":
        return (
            f"{record.category} collector record. "
            "Live public source data was fetched without credentials or user-query forwarding; "
            "observed date and confidence describe collection time, not market fit."
        )

    return (
        f"{record.category} collector record. "
        "Fixture-backed data is for deterministic workflow validation; "
        "verify current facts before external claims."
    )

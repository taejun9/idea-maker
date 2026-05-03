export type QuickIdeaExample = {
  field: string;
  idea: string;
};

type QuickIdeaExampleGroup = {
  field: string;
  ideas: string[];
};

export const quickIdeaExampleGroups: QuickIdeaExampleGroup[] = [
  {
    field: "IT",
    ideas: [
      "개발자를 위한 AI 코드 품질 점검 플랫폼",
      "데이터 파이프라인 이상 징후를 알려주는 SaaS",
    ],
  },
  {
    field: "교육",
    ideas: [
      "초등학생 수학 오답을 학습 루틴으로 바꿔주는 앱",
      "스터디 모임 출석과 과제를 자동 정리하는 서비스",
    ],
  },
  {
    field: "금융",
    ideas: [
      "청년 대출 조건을 비교하고 상환 일정을 알려주는 서비스",
      "보험 청구 서류를 점검하고 진행 상태를 알려주는 앱",
    ],
  },
  {
    field: "운영관리",
    ideas: [
      "프랜차이즈 매장 체크리스트와 교대 업무를 자동 관리하는 도구",
      "소상공인 운영 일지를 매일 요약하는 서비스",
    ],
  },
  {
    field: "네트워킹",
    ideas: [
      "취미 모임 멤버를 관심사별로 매칭하는 커뮤니티",
      "컨퍼런스 참가자의 관심사를 기반으로 네트워킹을 추천하는 앱",
    ],
  },
  {
    field: "농축/수산업",
    ideas: [
      "소규모 농장의 작물 생육 데이터를 기록하는 서비스",
      "수산 양식장의 수질 변화를 조기에 알려주는 센서 로그 앱",
    ],
  },
  {
    field: "라이프스타일",
    ideas: [
      "가정 식단과 생활 루틴을 추천하는 앱",
      "여행 준비물과 취미 일정을 한곳에 모으는 서비스",
    ],
  },
  {
    field: "마케팅/PR",
    ideas: [
      "브랜드 리뷰와 고객 반응을 분석해 홍보 소재를 추천하는 도구",
      "1인 쇼핑몰의 반품 문의를 줄이는 챗봇",
    ],
  },
  {
    field: "모빌리티",
    ideas: [
      "아파트 단지 주차 빈자리를 실시간 공유하는 앱",
      "전기 자전거 이동 경로와 정비 시점을 추천하는 서비스",
    ],
  },
  {
    field: "미디어/엔터테인먼트",
    ideas: [
      "영상 크리에이터의 콘텐츠 일정과 팬 반응을 정리하는 도구",
      "음악 공연팀의 영상 티저와 콘텐츠 반응을 정리하는 서비스",
    ],
  },
  {
    field: "바이오/의류",
    ideas: [
      "개인 건강 기록으로 맞춤 운동과 의료 상담을 준비하는 서비스",
      "패션 브랜드의 의류 사이즈 추천과 교환 데이터를 정리하는 도구",
    ],
  },
  {
    field: "에너지/자원",
    ideas: [
      "상가 전력 사용량과 탄소 절감 포인트를 알려주는 대시보드",
      "태양광 설비의 에너지 생산량을 예측하는 서비스",
    ],
  },
  {
    field: "유통/물류",
    ideas: [
      "온라인 커머스 재고와 배송 지연을 예측하는 운영 도구",
      "동네 유통 매장의 물류 발주량을 자동 추천하는 서비스",
    ],
  },
  {
    field: "임팩트",
    ideas: [
      "지역 복지 기관의 기부 물품 배분 현황을 보여주는 플랫폼",
      "환경 캠페인의 참여 데이터를 임팩트 지표로 정리하는 서비스",
    ],
  },
  {
    field: "재무",
    ideas: [
      "프리랜서 세금과 정산 일정을 자동으로 계산하는 서비스",
      "팀 예산 사용과 비용 승인 흐름을 정리하는 도구",
    ],
  },
  {
    field: "프롭테크",
    ideas: [
      "임대 건물의 공실 현황과 주거 민원을 정리하는 도구",
      "부동산 중개팀의 매물 상태를 자동 갱신하는 프롭테크 서비스",
    ],
  },
  {
    field: "하드웨어",
    ideas: [
      "센서 디바이스로 냉장 설비 이상을 감지하는 알림 장치",
      "로봇 팔 기기의 점검 이력을 보여주는 하드웨어 대시보드",
    ],
  },
];

export const quickExampleBusinessFields = quickIdeaExampleGroups.map((group) => group.field);

export function createRandomQuickIdeaExamples({
  count = 3,
  random = Math.random,
}: {
  count?: number;
  random?: () => number;
} = {}): QuickIdeaExample[] {
  const visibleCount = Math.min(Math.max(count, 0), quickIdeaExampleGroups.length);

  return quickIdeaExampleGroups
    .map((group) => ({ group, rank: random() }))
    .sort((left, right) => left.rank - right.rank)
    .slice(0, visibleCount)
    .map(({ group }) => ({
      field: group.field,
      idea: group.ideas[randomIndex(group.ideas.length, random)],
    }));
}

function randomIndex(length: number, random: () => number) {
  if (length <= 1) {
    return 0;
  }

  return Math.min(Math.floor(random() * length), length - 1);
}

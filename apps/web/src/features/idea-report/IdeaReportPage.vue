<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import {
  createIdeaRecommendations,
  createIdeaReport,
} from '../../api/ideaReports';
import type {
  Competitor,
  IdeaIntakeAnswerInput,
  IdeaRecommendation,
  IdeaReportResponse,
  SourceConfidence,
} from '../../types/ideaReport';
import IdeaIntakeQuestions from './IdeaIntakeQuestions.vue';
import {
  createRandomQuickIdeaExamples,
  quickExampleBusinessFields,
  type QuickIdeaExample,
} from './quickExamples';

const minIdeaLength = 5;
const maxIdeaLength = 2000;
const businessFieldOptions: string[] = [...quickExampleBusinessFields, '기타'];
const businessFieldKeywordPatterns: Array<{
  field: string;
  keywords: string[];
}> = [
  {
    field: '교육',
    keywords: ['교육', '학습', '스터디', '강의', '출석', '학교', '학생'],
  },
  { field: '금융', keywords: ['금융', '대출', '보험', '결제', '송금', '은행'] },
  { field: '재무', keywords: ['재무', '회계', '세금', '정산', '예산', '비용'] },
  {
    field: '마케팅/PR',
    keywords: [
      '리뷰',
      '마케팅',
      '광고',
      '홍보',
      'pr',
      '피드백',
      '고객 반응',
      '문의',
    ],
  },
  {
    field: '유통/물류',
    keywords: ['쇼핑몰', '반품', '배송', '재고', '물류', '유통', '커머스'],
  },
  {
    field: '운영관리',
    keywords: [
      '운영',
      '업무',
      '자동화',
      '체크리스트',
      '관리',
      '매장',
      '소상공인',
    ],
  },
  {
    field: '네트워킹',
    keywords: ['네트워킹', '커뮤니티', '모임', '매칭', '연결'],
  },
  {
    field: '모빌리티',
    keywords: ['모빌리티', '차량', '주차', '교통', '이동', '배달'],
  },
  {
    field: '미디어/엔터테인먼트',
    keywords: ['콘텐츠', '미디어', '영상', '음악', '엔터테인먼트'],
  },
  {
    field: '바이오/의류',
    keywords: ['바이오', '헬스케어', '의료', '건강', '의류', '패션'],
  },
  {
    field: '에너지/자원',
    keywords: ['에너지', '전력', '자원', '탄소', '전기'],
  },
  { field: '농축/수산업', keywords: ['농업', '축산', '수산', '농장', '어업'] },
  {
    field: '라이프스타일',
    keywords: ['생활', '라이프스타일', '취미', '여행', '가정'],
  },
  {
    field: '프롭테크',
    keywords: ['부동산', '임대', '주거', '건물', '프롭테크'],
  },
  {
    field: '하드웨어',
    keywords: ['하드웨어', '기기', '센서', '로봇', '디바이스'],
  },
  { field: '임팩트', keywords: ['임팩트', '환경', '기부', '복지', '사회문제'] },
  {
    field: 'IT',
    keywords: [
      'ai',
      '인공지능',
      'saas',
      '소프트웨어',
      '앱',
      '플랫폼',
      '데이터',
      '챗봇',
    ],
  },
];

const idea = ref('');
const selectedBusinessField = ref('');
const lastAutoBusinessField = ref('');
const recommendations = ref<IdeaRecommendation[]>([]);
const recommendationKeyword = ref('');
const selectedRecommendationTitle = ref('');
const report = ref<IdeaReportResponse | null>(null);
const isLoading = ref(false);
const loadingMode = ref<'idle' | 'recommendations' | 'report'>('idle');
const errorMessage = ref('');
const hasTriedSubmit = ref(false);
const isIdeaTouched = ref(false);
const ideaExamples = ref(createRandomQuickIdeaExamples());

const normalizedIdea = computed(() => idea.value.trim());
const ideaLength = computed(() => normalizedIdea.value.length);
const ideaTokens = computed(() =>
  normalizedIdea.value.split(/\s+/).filter(Boolean),
);
const normalizedBusinessField = computed(() =>
  selectedBusinessField.value.trim(),
);
const isRecommendationInput = computed(
  () =>
    ideaLength.value > 0 &&
    (ideaTokens.value.length <= 5 || ideaLength.value <= 40),
);
const isIdeaValid = computed(() => {
  if (ideaLength.value === 0) {
    return false;
  }

  if (isRecommendationInput.value) {
    return true;
  }

  return ideaLength.value >= minIdeaLength;
});
const inputMinLength = computed(() =>
  isRecommendationInput.value ? 1 : minIdeaLength,
);
const shouldShowIdeaError = computed(
  () => (hasTriedSubmit.value || isIdeaTouched.value) && !isIdeaValid.value,
);
const ideaValidationMessage = computed(() => {
  if (isIdeaValid.value && isRecommendationInput.value) {
    return '관련 아이템을 추천한 뒤 검색과 자료 정리를 진행할 수 있습니다.';
  }

  if (isIdeaValid.value) {
    return '입력 조건을 충족했습니다.';
  }

  if (ideaLength.value === 0) {
    return `아이디어를 ${minIdeaLength}자 이상 입력하세요.`;
  }

  return `${minIdeaLength - ideaLength.value}자 더 입력하면 보고서를 만들 수 있습니다.`;
});
const ideaDescriptionIds = computed(() =>
  shouldShowIdeaError.value
    ? 'idea-help idea-count idea-error'
    : 'idea-help idea-count',
);
const isBusinessFieldValid = computed(() =>
  businessFieldOptions.includes(normalizedBusinessField.value),
);
const shouldShowIntakeError = computed(
  () => hasTriedSubmit.value && !isBusinessFieldValid.value,
);
const submitDisabledDescription = computed(() => {
  if (canSubmit.value) {
    return undefined;
  }

  if (
    isIdeaValid.value &&
    !isRecommendationInput.value &&
    !isBusinessFieldValid.value
  ) {
    return 'intake-validation';
  }

  return 'idea-count';
});
const intakeValidationMessage = computed(() => {
  if (isBusinessFieldValid.value) {
    return '사업 분야 선택이 완료되었습니다.';
  }

  return '사업 분야를 선택해주세요.';
});
const canSubmit = computed(
  () =>
    isIdeaValid.value &&
    !isLoading.value &&
    (isRecommendationInput.value || isBusinessFieldValid.value),
);
const canCreateReportFromRecommendation = computed(
  () => !isLoading.value && isBusinessFieldValid.value,
);
const submitButtonLabel = computed(() => {
  if (loadingMode.value === 'recommendations') {
    return '추천 찾는 중';
  }

  if (loadingMode.value === 'report') {
    return '보고서 생성 중';
  }

  return isRecommendationInput.value ? '아이템 추천' : '보고서 생성';
});

const confidenceLabel: Record<SourceConfidence, string> = {
  low: '낮음',
  medium: '보통',
  high: '높음',
};

function selectIdeaExample(example: QuickIdeaExample) {
  idea.value = example.idea;
  applyInferredBusinessField(example.idea, true);
  errorMessage.value = '';
  hasTriedSubmit.value = false;
  isIdeaTouched.value = true;
}

watch(normalizedIdea, () => {
  applyInferredBusinessField(normalizedIdea.value);
  recommendations.value = [];
  recommendationKeyword.value = '';
  selectedRecommendationTitle.value = '';
  errorMessage.value = '';
});

async function submitReport() {
  hasTriedSubmit.value = true;
  isIdeaTouched.value = true;

  if (!isIdeaValid.value) {
    return;
  }

  if (!isRecommendationInput.value && !isBusinessFieldValid.value) {
    return;
  }

  if (isRecommendationInput.value) {
    await loadRecommendations();
    return;
  }

  await generateReport(normalizedIdea.value, '', false);
}

async function loadRecommendations() {
  isLoading.value = true;
  loadingMode.value = 'recommendations';
  errorMessage.value = '';
  report.value = null;
  selectedRecommendationTitle.value = '';

  try {
    const response = await createIdeaRecommendations({
      keyword: normalizedIdea.value,
      locale: 'ko-KR',
    });
    recommendationKeyword.value = response.keyword;
    recommendations.value = response.recommendations;
  } catch (error) {
    errorMessage.value =
      error instanceof Error
        ? error.message
        : '추천 아이템을 생성하지 못했습니다.';
  } finally {
    isLoading.value = false;
    loadingMode.value = 'idle';
  }
}

async function createReportFromRecommendation(
  recommendation: IdeaRecommendation,
) {
  hasTriedSubmit.value = true;
  applyInferredBusinessField(recommendation.report_seed);
  if (!isBusinessFieldValid.value) {
    return;
  }

  selectedRecommendationTitle.value = recommendation.title;
  await generateReport(recommendation.report_seed, recommendation.title, true);
}

async function generateReport(
  ideaForReport: string,
  recommendationTitle = '',
  research = false,
) {
  isLoading.value = true;
  loadingMode.value = 'report';
  errorMessage.value = '';
  report.value = null;

  try {
    report.value = await createIdeaReport({
      idea: ideaForReport,
      locale: 'ko-KR',
      research,
      idea_intake_answers: ideaIntakeAnswerPayload(),
    });
    selectedRecommendationTitle.value = recommendationTitle;
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : '보고서를 생성하지 못했습니다.';
  } finally {
    isLoading.value = false;
    loadingMode.value = 'idle';
  }
}

function ideaIntakeAnswerPayload(): IdeaIntakeAnswerInput[] {
  if (!normalizedBusinessField.value) {
    return [];
  }

  return [{ code: 'Q5', answer: normalizedBusinessField.value }];
}

function applyInferredBusinessField(value: string, force = false) {
  const inferredField = inferBusinessField(value);
  if (!inferredField) {
    if (force) {
      selectedBusinessField.value = '';
      lastAutoBusinessField.value = '';
    }
    return;
  }

  if (
    force ||
    !selectedBusinessField.value ||
    selectedBusinessField.value === lastAutoBusinessField.value
  ) {
    selectedBusinessField.value = inferredField;
    lastAutoBusinessField.value = inferredField;
  }
}

function inferBusinessField(value: string) {
  const normalizedValue = value.trim().toLowerCase();
  if (!normalizedValue) {
    return '';
  }

  const matchedPattern = businessFieldKeywordPatterns.find((pattern) =>
    pattern.keywords.some((keyword) => normalizedValue.includes(keyword)),
  );
  return matchedPattern?.field ?? '기타';
}

function competitorMarketLabel(competitor: Competitor) {
  return competitor.market === 'domestic_kr' ? '국내' : '해외';
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}
</script>

<template>
  <div
    class="mx-auto flex w-full max-w-5xl flex-col gap-8 px-5 py-8 sm:px-6 lg:px-8"
  >
    <header class="mb-2">
      <p class="text-sm font-semibold tracking-wide text-emerald-600 uppercase">
        Idea Maker
      </p>
      <h1
        class="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl"
      >
        아이디어 보고서 생성
      </h1>
    </header>

    <form
      class="grid gap-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/60 sm:p-8"
      :aria-busy="isLoading"
      @submit.prevent="submitReport"
    >
      <div class="grid gap-2">
        <label class="text-base font-semibold" for="idea"
          >어떤 아이디어인가요?</label
        >
        <p id="idea-help" class="max-w-2xl text-sm leading-6 text-slate-600">
          단어 또는 짧은 문장으로 시작하면 관련 아이템을 먼저 추천합니다.
        </p>
      </div>

      <fieldset class="grid gap-2">
        <legend class="text-sm font-medium text-slate-700">빠른 예시</legend>
        <div class="flex flex-wrap gap-3">
          <button
            v-for="example in ideaExamples"
            :key="`${example.field}-${example.idea}`"
            class="grid gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-sm leading-5 text-slate-700 shadow-sm transition-all hover:border-emerald-500 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
            :data-business-field="example.field"
            data-testid="idea-example"
            type="button"
            @click="selectIdeaExample(example)"
          >
            <span class="text-xs font-bold text-emerald-600">{{
              example.field
            }}</span>
            <span class="font-medium text-slate-800">{{ example.idea }}</span>
          </button>
        </div>
      </fieldset>

      <div class="grid gap-2">
        <textarea
          id="idea"
          v-model="idea"
          data-testid="idea-input"
          class="min-h-40 resize-y rounded-xl border bg-slate-50 p-4 text-base leading-7 outline-none transition-all placeholder:text-slate-400 focus:bg-white focus:ring-4"
          :class="
            shouldShowIdeaError
              ? 'border-red-400 focus:border-red-500 focus:ring-red-500/20'
              : 'border-slate-200 focus:border-emerald-500 focus:ring-emerald-500/20'
          "
          :aria-describedby="ideaDescriptionIds"
          :aria-invalid="shouldShowIdeaError ? 'true' : 'false'"
          :maxlength="maxIdeaLength"
          :minlength="inputMinLength"
          placeholder="예: 동네 소상공인을 위한 AI 리뷰 분석 도구"
          required
          @blur="isIdeaTouched = true"
        />
        <div class="flex flex-wrap items-center justify-between gap-2">
          <p
            id="idea-count"
            data-testid="idea-count"
            class="text-sm text-slate-600"
            aria-live="polite"
          >
            {{ ideaLength }} / {{ maxIdeaLength }}자 ·
            {{ ideaValidationMessage }}
          </p>
        </div>
        <p
          v-if="shouldShowIdeaError"
          id="idea-error"
          class="text-sm font-medium text-red-700"
          role="alert"
        >
          {{ ideaValidationMessage }}
        </p>
      </div>

      <fieldset class="grid gap-4" data-testid="idea-intake-form">
        <legend class="text-base font-semibold">아이디어 보강 정보</legend>

        <div class="grid gap-2">
          <label class="text-sm font-medium text-slate-700" for="intake-q5">
            Q5. 사업 분야
          </label>
          <select
            id="intake-q5"
            v-model="selectedBusinessField"
            class="rounded-xl border border-slate-200 bg-white p-3.5 text-sm outline-none transition-all focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/20"
            data-testid="intake-q5"
            aria-describedby="intake-field-help intake-validation"
            :aria-invalid="shouldShowIntakeError ? 'true' : 'false'"
          >
            <!-- <option value="">자동 선택 대기</option> -->
            <option
              v-for="fieldOption in businessFieldOptions"
              :key="fieldOption"
              :value="fieldOption"
            >
              {{ fieldOption }}
            </option>
          </select>
          <p id="intake-field-help" class="text-xs leading-5 text-slate-500">
            입력한 아이디어에 맞춰 자동 선택되며, 필요하면 변경할 수 있습니다.
          </p>
        </div>

        <div
          class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-600"
          data-testid="auto-intake-note"
        >
          Q1~Q4 답변은 보고서 생성 시 아이디어 내용에 맞춰 자동 작성됩니다.
          이미지는 없어도 보고서를 생성할 수 있습니다.
        </div>

        <p
          id="intake-validation"
          class="text-sm"
          :class="
            isBusinessFieldValid ? 'text-slate-600' : 'font-medium text-red-700'
          "
          data-testid="intake-validation"
          :role="shouldShowIntakeError ? 'alert' : undefined"
        >
          {{ intakeValidationMessage }}
        </p>
      </fieldset>

      <div class="mt-2 flex flex-wrap items-center gap-4">
        <button
          data-testid="generate-report"
          class="min-h-12 w-full sm:w-auto rounded-xl bg-emerald-600 px-6 py-2.5 text-base font-semibold text-white shadow-sm transition-all hover:bg-emerald-700 focus:outline-none focus:ring-4 focus:ring-emerald-500/20 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none"
          type="submit"
          :aria-describedby="submitDisabledDescription"
          :disabled="!canSubmit"
        >
          {{ submitButtonLabel }}
        </button>
        <p
          v-if="isLoading && loadingMode === 'report'"
          class="text-sm text-slate-600"
          role="status"
          aria-live="polite"
        >
          보고서를 준비하고 있습니다.
        </p>
        <p
          v-if="isLoading && loadingMode === 'recommendations'"
          class="text-sm text-slate-600"
          role="status"
          aria-live="polite"
        >
          추천 아이템을 찾고 있습니다.
        </p>
        <p
          v-if="errorMessage"
          data-testid="report-error"
          class="text-sm font-medium text-red-700"
          role="alert"
        >
          {{ errorMessage }}
        </p>
      </div>
    </form>

    <section
      v-if="recommendations.length > 0"
      data-testid="recommendation-list"
      class="grid gap-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/60 sm:p-8"
      aria-live="polite"
    >
      <div
        class="flex flex-wrap items-end justify-between gap-3 border-b border-slate-100 pb-4"
      >
        <div class="grid gap-1">
          <p
            class="text-sm font-semibold uppercase tracking-wide text-emerald-600"
          >
            입력: {{ recommendationKeyword }}
          </p>
          <h2 class="text-2xl font-bold text-slate-900">추천 아이템</h2>
        </div>
      </div>

      <div class="grid gap-4 md:grid-cols-2">
        <article
          v-for="recommendation in recommendations"
          :key="recommendation.title"
          class="grid gap-4 rounded-xl border bg-slate-50 p-5 shadow-sm transition-all hover:shadow-md"
          :class="
            selectedRecommendationTitle === recommendation.title
              ? 'border-emerald-500 ring-2 ring-emerald-500/20'
              : 'border-slate-200'
          "
        >
          <div class="grid gap-2">
            <h3 class="text-lg font-bold leading-6 text-slate-900">
              {{ recommendation.title }}
            </h3>
            <p class="text-sm font-medium leading-6 text-slate-700">
              {{ recommendation.summary }}
            </p>
            <p class="text-sm leading-6 text-slate-600">
              {{ recommendation.rationale }}
            </p>
          </div>
          <button
            class="min-h-11 justify-self-start rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 focus:outline-none focus:ring-4 focus:ring-slate-500/20 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none"
            data-testid="recommendation-report"
            type="button"
            :disabled="!canCreateReportFromRecommendation"
            @click="createReportFromRecommendation(recommendation)"
          >
            {{
              isLoading &&
              loadingMode === 'report' &&
              selectedRecommendationTitle === recommendation.title
                ? '검색과 정리 진행 중'
                : '검색 후 보고서 생성'
            }}
          </button>
        </article>
      </div>
    </section>

    <section
      v-if="report"
      data-testid="report-summary"
      class="grid gap-8 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/60 sm:p-8"
      aria-live="polite"
    >
      <header
        class="flex flex-wrap items-end justify-between gap-4 border-b border-slate-100 pb-6"
      >
        <div class="grid gap-1.5">
          <p
            class="text-sm font-semibold uppercase tracking-wide text-emerald-600"
          >
            저장된 보고서 · {{ formatDateTime(report.created_at) }}
          </p>
          <h2 class="text-3xl font-extrabold leading-tight text-slate-900">
            {{ report.idea }}
          </h2>
        </div>
        <a
          class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-200 focus:outline-none focus:ring-4 focus:ring-slate-200"
          data-testid="open-report-detail"
          :href="`#/reports/${report.id}`"
        >
          상세 페이지 열기
        </a>
      </header>

      <section class="grid gap-3">
        <h2 class="text-xl font-semibold">요약</h2>
        <p
          class="rounded border border-slate-200 bg-white p-4 leading-7 text-slate-700"
        >
          {{ report.overview }}
        </p>
      </section>

      <IdeaIntakeQuestions :questions="report.idea_intake_questions" />

      <section
        v-if="report.research_status.requested"
        data-testid="research-status"
        class="grid gap-3"
      >
        <h2 class="text-lg font-semibold">검색 및 자료 정리 상태</h2>
        <div
          class="rounded border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-700"
        >
          <p>
            검색 {{ report.research_status.search_provider }} /
            {{ report.research_status.search_status }}
          </p>
          <p>
            정리 {{ report.research_status.organization_provider }} /
            {{ report.research_status.organization_status }}
          </p>
          <ul
            v-if="report.research_status.notes.length > 0"
            class="mt-2 grid gap-1"
          >
            <li v-for="note in report.research_status.notes" :key="note">
              {{ note }}
            </li>
          </ul>
        </div>
      </section>

      <section
        class="grid gap-4 md:grid-cols-[minmax(0,2fr)_minmax(16rem,1fr)]"
      >
        <div class="grid gap-3">
          <h2 class="text-lg font-semibold">구체화된 콘셉트</h2>
          <p
            data-testid="clarified-concept"
            class="rounded border border-slate-200 bg-white p-4 leading-7 text-slate-700"
          >
            {{ report.clarified_concept }}
          </p>
        </div>
        <div class="grid gap-3">
          <h2 class="text-lg font-semibold">빌드 난이도</h2>
          <p
            class="rounded border border-slate-200 bg-white p-4 leading-7 text-slate-700"
          >
            {{ report.build_complexity }}
          </p>
        </div>
      </section>

      <section class="grid gap-4 md:grid-cols-2">
        <div class="grid gap-3">
          <h2 class="text-lg font-semibold">대상 사용자</h2>
          <ul class="flex flex-wrap gap-2">
            <li
              v-for="user in report.target_users"
              :key="user"
              class="rounded border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700"
            >
              {{ user }}
            </li>
          </ul>
        </div>
        <div class="grid gap-3">
          <h2 class="text-lg font-semibold">핵심 사용 사례</h2>
          <ul data-testid="core-use-cases" class="grid gap-2">
            <li
              v-for="useCase in report.core_use_cases"
              :key="useCase"
              class="rounded border border-slate-200 bg-white p-3 text-sm text-slate-700"
            >
              {{ useCase }}
            </li>
          </ul>
        </div>
      </section>

      <section class="grid gap-4 md:grid-cols-2">
        <div class="grid gap-3">
          <h2 class="text-lg font-semibold">강점</h2>
          <ul class="grid gap-2">
            <li
              v-for="strength in report.strengths"
              :key="strength"
              class="rounded border border-emerald-200 bg-white p-3 text-sm text-slate-700"
            >
              {{ strength }}
            </li>
          </ul>
        </div>
        <div class="grid gap-3">
          <h2 class="text-lg font-semibold">약점</h2>
          <ul class="grid gap-2">
            <li
              v-for="weakness in report.weaknesses"
              :key="weakness"
              class="rounded border border-amber-200 bg-white p-3 text-sm text-slate-700"
            >
              {{ weakness }}
            </li>
          </ul>
        </div>
      </section>

      <section class="grid gap-4 md:grid-cols-2">
        <div class="grid gap-3">
          <h2 class="text-lg font-semibold">차별화 기회</h2>
          <ul data-testid="differentiation-opportunities" class="grid gap-2">
            <li
              v-for="opportunity in report.differentiation_opportunities"
              :key="opportunity"
              class="rounded border border-cyan-200 bg-white p-3 text-sm text-slate-700"
            >
              {{ opportunity }}
            </li>
          </ul>
        </div>
        <div class="grid gap-3">
          <h2 class="text-lg font-semibold">주요 리스크</h2>
          <ul data-testid="key-risks" class="grid gap-2">
            <li
              v-for="risk in report.key_risks"
              :key="risk"
              class="rounded border border-red-200 bg-white p-3 text-sm text-slate-700"
            >
              {{ risk }}
            </li>
          </ul>
        </div>
      </section>

      <section class="grid gap-4 lg:grid-cols-2">
        <div class="grid gap-3" data-testid="domestic-competitors">
          <h2 class="text-lg font-semibold">국내 경쟁 서비스</h2>
          <article
            v-for="competitor in report.domestic_competitors"
            :key="competitor.name"
            class="rounded border border-slate-200 bg-white p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <h3 class="font-semibold">{{ competitor.name }}</h3>
              <span
                class="shrink-0 rounded bg-slate-100 px-2 py-1 text-xs text-slate-600"
              >
                {{ competitorMarketLabel(competitor) }}
              </span>
            </div>
            <p class="mt-2 text-sm leading-6 text-slate-700">
              {{ competitor.summary }}
            </p>
            <p class="mt-3 text-xs text-slate-500">
              관찰일 {{ competitor.observed_date }} · 신뢰도
              {{ confidenceLabel[competitor.confidence] }}
            </p>
          </article>
        </div>

        <div class="grid gap-3" data-testid="overseas-competitors">
          <h2 class="text-lg font-semibold">해외 경쟁 서비스</h2>
          <article
            v-for="competitor in report.overseas_competitors"
            :key="competitor.name"
            class="rounded border border-slate-200 bg-white p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <h3 class="font-semibold">{{ competitor.name }}</h3>
              <span
                class="shrink-0 rounded bg-slate-100 px-2 py-1 text-xs text-slate-600"
              >
                {{ competitorMarketLabel(competitor) }}
              </span>
            </div>
            <p class="mt-2 text-sm leading-6 text-slate-700">
              {{ competitor.summary }}
            </p>
            <p class="mt-3 text-xs text-slate-500">
              관찰일 {{ competitor.observed_date }} · 신뢰도
              {{ confidenceLabel[competitor.confidence] }}
            </p>
          </article>
        </div>
      </section>

      <section class="grid gap-3" data-testid="source-references">
        <h2 class="text-lg font-semibold">추천 소스</h2>
        <div class="grid gap-3 md:grid-cols-3">
          <article
            v-for="source in report.source_references"
            :key="`${source.source_name}:${source.source_url}`"
            class="rounded border border-slate-200 bg-white p-4"
          >
            <a
              class="font-semibold text-emerald-800 underline-offset-4 hover:underline"
              :href="source.source_url"
              rel="noreferrer"
              target="_blank"
            >
              {{ source.source_name }}
            </a>
            <p class="mt-2 text-sm leading-6 text-slate-700">
              {{ source.note }}
            </p>
            <p class="mt-3 text-xs text-slate-500">
              {{ source.observed_date }} · 신뢰도
              {{ confidenceLabel[source.confidence] }}
            </p>
          </article>
        </div>
      </section>

      <section class="grid gap-3">
        <h2 class="text-lg font-semibold">추천 MVP 범위</h2>
        <ul
          data-testid="recommended-mvp-scope"
          class="grid gap-2 md:grid-cols-3"
        >
          <li
            v-for="scopeItem in report.recommended_mvp_scope"
            :key="scopeItem"
            class="rounded border border-slate-200 bg-white p-3 text-sm text-slate-700"
          >
            {{ scopeItem }}
          </li>
        </ul>
      </section>

      <section class="grid gap-3">
        <h2 class="text-lg font-semibold">다음 검증 단계</h2>
        <ol class="grid gap-2">
          <li
            v-for="(step, index) in report.next_validation_steps"
            :key="step"
            class="rounded border border-slate-200 bg-white p-3 text-sm text-slate-700"
          >
            {{ index + 1 }}. {{ step }}
          </li>
        </ol>
      </section>
    </section>

    <section
      v-else
      data-testid="report-empty"
      class="flex items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-12 text-center text-slate-500"
    >
      생성된 보고서가 여기에 표시됩니다.
    </section>
  </div>
</template>

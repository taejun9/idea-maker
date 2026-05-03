<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { createIdeaRecommendations, createIdeaReport } from "../../api/ideaReports";
import type {
  Competitor,
  IdeaRecommendation,
  IdeaReportResponse,
  SourceConfidence,
} from "../../types/ideaReport";
import IdeaIntakeQuestions from "./IdeaIntakeQuestions.vue";

const minIdeaLength = 5;
const maxIdeaLength = 2000;
const ideaExamples = [
  "동네 소상공인을 위한 AI 리뷰 분석 도구",
  "1인 쇼핑몰의 반품 문의를 줄이는 챗봇",
  "스터디 모임 출석과 과제를 자동 정리하는 서비스",
];

const idea = ref("");
const recommendations = ref<IdeaRecommendation[]>([]);
const recommendationKeyword = ref("");
const selectedRecommendationTitle = ref("");
const report = ref<IdeaReportResponse | null>(null);
const isLoading = ref(false);
const loadingMode = ref<"idle" | "recommendations" | "report">("idle");
const errorMessage = ref("");
const hasTriedSubmit = ref(false);
const isIdeaTouched = ref(false);

const normalizedIdea = computed(() => idea.value.trim());
const ideaLength = computed(() => normalizedIdea.value.length);
const ideaTokens = computed(() => normalizedIdea.value.split(/\s+/).filter(Boolean));
const isRecommendationInput = computed(
  () => ideaLength.value > 0 && (ideaTokens.value.length <= 5 || ideaLength.value <= 40),
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
const inputMinLength = computed(() => (isRecommendationInput.value ? 1 : minIdeaLength));
const shouldShowIdeaError = computed(
  () => (hasTriedSubmit.value || isIdeaTouched.value) && !isIdeaValid.value,
);
const ideaValidationMessage = computed(() => {
  if (isIdeaValid.value && isRecommendationInput.value) {
    return "관련 아이템을 추천한 뒤 검색과 자료 정리를 진행할 수 있습니다.";
  }

  if (isIdeaValid.value) {
    return "입력 조건을 충족했습니다.";
  }

  if (ideaLength.value === 0) {
    return `아이디어를 ${minIdeaLength}자 이상 입력하세요.`;
  }

  return `${minIdeaLength - ideaLength.value}자 더 입력하면 보고서를 만들 수 있습니다.`;
});
const ideaDescriptionIds = computed(() =>
  shouldShowIdeaError.value ? "idea-help idea-count idea-error" : "idea-help idea-count",
);
const canSubmit = computed(() => isIdeaValid.value && !isLoading.value);
const submitButtonLabel = computed(() => {
  if (loadingMode.value === "recommendations") {
    return "추천 찾는 중";
  }

  if (loadingMode.value === "report") {
    return "보고서 생성 중";
  }

  return isRecommendationInput.value ? "아이템 추천" : "보고서 생성";
});

const confidenceLabel: Record<SourceConfidence, string> = {
  low: "낮음",
  medium: "보통",
  high: "높음",
};

function selectIdeaExample(example: string) {
  idea.value = example;
  errorMessage.value = "";
  hasTriedSubmit.value = false;
  isIdeaTouched.value = true;
}

watch(normalizedIdea, () => {
  recommendations.value = [];
  recommendationKeyword.value = "";
  selectedRecommendationTitle.value = "";
  errorMessage.value = "";
});

async function submitReport() {
  hasTriedSubmit.value = true;
  isIdeaTouched.value = true;

  if (!canSubmit.value) {
    return;
  }

  if (isRecommendationInput.value) {
    await loadRecommendations();
    return;
  }

  await generateReport(normalizedIdea.value, "", false);
}

async function loadRecommendations() {
  isLoading.value = true;
  loadingMode.value = "recommendations";
  errorMessage.value = "";
  report.value = null;
  selectedRecommendationTitle.value = "";

  try {
    const response = await createIdeaRecommendations({
      keyword: normalizedIdea.value,
      locale: "ko-KR",
    });
    recommendationKeyword.value = response.keyword;
    recommendations.value = response.recommendations;
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "추천 아이템을 생성하지 못했습니다.";
  } finally {
    isLoading.value = false;
    loadingMode.value = "idle";
  }
}

async function createReportFromRecommendation(recommendation: IdeaRecommendation) {
  selectedRecommendationTitle.value = recommendation.title;
  await generateReport(recommendation.report_seed, recommendation.title, true);
}

async function generateReport(
  ideaForReport: string,
  recommendationTitle = "",
  research = false,
) {
  isLoading.value = true;
  loadingMode.value = "report";
  errorMessage.value = "";
  report.value = null;

  try {
    report.value = await createIdeaReport({
      idea: ideaForReport,
      locale: "ko-KR",
      research,
    });
    selectedRecommendationTitle.value = recommendationTitle;
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "보고서를 생성하지 못했습니다.";
  } finally {
    isLoading.value = false;
    loadingMode.value = "idle";
  }
}

function competitorMarketLabel(competitor: Competitor) {
  return competitor.market === "domestic_kr" ? "국내" : "해외";
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
</script>

<template>
  <main class="min-h-screen bg-slate-50 text-slate-950">
    <section class="mx-auto flex w-full max-w-6xl flex-col gap-6 px-5 py-6 sm:px-6 lg:px-8">
      <header class="border-b border-slate-200 pb-4">
        <p class="text-sm font-medium text-slate-500">Idea Maker</p>
        <h1 class="mt-2 text-3xl font-semibold">아이디어 보고서 생성</h1>
      </header>

      <form
        class="grid gap-5 border-b border-slate-200 pb-6"
        :aria-busy="isLoading"
        @submit.prevent="submitReport"
      >
        <div class="grid gap-2">
          <label class="text-base font-semibold" for="idea">어떤 아이디어인가요?</label>
          <p id="idea-help" class="max-w-2xl text-sm leading-6 text-slate-600">
            단어 또는 짧은 문장으로 시작하면 관련 아이템을 먼저 추천합니다.
          </p>
        </div>

        <fieldset class="grid gap-2">
          <legend class="text-sm font-medium text-slate-700">빠른 예시</legend>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="example in ideaExamples"
              :key="example"
              class="rounded border border-slate-300 bg-white px-3 py-2 text-left text-sm leading-5 text-slate-700 transition hover:border-emerald-500 hover:text-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              data-testid="idea-example"
              type="button"
              @click="selectIdeaExample(example)"
            >
              {{ example }}
            </button>
          </div>
        </fieldset>

        <div class="grid gap-2">
          <textarea
            id="idea"
            v-model="idea"
            data-testid="idea-input"
            class="min-h-40 resize-y rounded border bg-white p-3 text-base leading-7 outline-none transition focus:ring-2"
            :class="
              shouldShowIdeaError
                ? 'border-red-600 focus:border-red-700 focus:ring-red-100'
                : 'border-slate-300 focus:border-emerald-600 focus:ring-emerald-100'
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
              {{ ideaLength }} / {{ maxIdeaLength }}자 · {{ ideaValidationMessage }}
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

        <div class="flex flex-wrap items-center gap-3">
          <button
            data-testid="generate-report"
            class="min-h-11 rounded bg-emerald-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-200 disabled:cursor-not-allowed disabled:bg-slate-300"
            type="submit"
            :aria-describedby="canSubmit ? undefined : 'idea-count'"
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
        class="grid gap-4 border-b border-slate-200 pb-6"
        aria-live="polite"
      >
        <div class="flex flex-wrap items-end justify-between gap-3">
          <div class="grid gap-1">
            <p class="text-sm font-medium text-slate-500">입력: {{ recommendationKeyword }}</p>
            <h2 class="text-xl font-semibold">추천 아이템</h2>
          </div>
        </div>

        <div class="grid gap-3 md:grid-cols-2">
          <article
            v-for="recommendation in recommendations"
            :key="recommendation.title"
            class="grid gap-3 rounded border bg-white p-4"
            :class="
              selectedRecommendationTitle === recommendation.title
                ? 'border-emerald-500 ring-2 ring-emerald-100'
                : 'border-slate-200'
            "
          >
            <div class="grid gap-2">
              <h3 class="font-semibold leading-6 text-slate-950">{{ recommendation.title }}</h3>
              <p class="text-sm leading-6 text-slate-700">{{ recommendation.summary }}</p>
              <p class="text-sm leading-6 text-slate-600">{{ recommendation.rationale }}</p>
            </div>
            <button
              class="min-h-10 justify-self-start rounded bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-300 disabled:cursor-not-allowed disabled:bg-slate-300"
              data-testid="recommendation-report"
              type="button"
              :disabled="isLoading"
              @click="createReportFromRecommendation(recommendation)"
            >
              {{
                isLoading &&
                loadingMode === "report" &&
                selectedRecommendationTitle === recommendation.title
                  ? "검색과 정리 진행 중"
                  : "검색 후 보고서 생성"
              }}
            </button>
          </article>
        </div>
      </section>

      <section
        v-if="report"
        data-testid="report-summary"
        class="grid gap-6"
        aria-live="polite"
      >
        <header class="flex flex-wrap items-end justify-between gap-3 border-b border-slate-200 pb-4">
          <div class="grid gap-1">
            <p class="text-sm font-medium text-slate-500">
              저장된 보고서 · {{ formatDateTime(report.created_at) }}
            </p>
            <h2 class="text-2xl font-semibold leading-tight text-slate-950">
              {{ report.idea }}
            </h2>
          </div>
          <a
            class="rounded border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:border-emerald-500 hover:text-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-200"
            data-testid="open-report-detail"
            :href="`#/reports/${report.id}`"
          >
            상세 페이지 열기
          </a>
        </header>

        <section class="grid gap-3">
          <h2 class="text-xl font-semibold">요약</h2>
          <p class="rounded border border-slate-200 bg-white p-4 leading-7 text-slate-700">
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
          <div class="rounded border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-700">
            <p>
              검색 {{ report.research_status.search_provider }} /
              {{ report.research_status.search_status }}
            </p>
            <p>
              정리 {{ report.research_status.organization_provider }} /
              {{ report.research_status.organization_status }}
            </p>
            <ul v-if="report.research_status.notes.length > 0" class="mt-2 grid gap-1">
              <li v-for="note in report.research_status.notes" :key="note">
                {{ note }}
              </li>
            </ul>
          </div>
        </section>

        <section class="grid gap-4 md:grid-cols-[minmax(0,2fr)_minmax(16rem,1fr)]">
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
            <p class="rounded border border-slate-200 bg-white p-4 leading-7 text-slate-700">
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
                <span class="shrink-0 rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">
                  {{ competitorMarketLabel(competitor) }}
                </span>
              </div>
              <p class="mt-2 text-sm leading-6 text-slate-700">{{ competitor.summary }}</p>
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
                <span class="shrink-0 rounded bg-slate-100 px-2 py-1 text-xs text-slate-600">
                  {{ competitorMarketLabel(competitor) }}
                </span>
              </div>
              <p class="mt-2 text-sm leading-6 text-slate-700">{{ competitor.summary }}</p>
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
              <p class="mt-2 text-sm leading-6 text-slate-700">{{ source.note }}</p>
              <p class="mt-3 text-xs text-slate-500">
                {{ source.observed_date }} · 신뢰도 {{ confidenceLabel[source.confidence] }}
              </p>
            </article>
          </div>
        </section>

        <section class="grid gap-3">
          <h2 class="text-lg font-semibold">추천 MVP 범위</h2>
          <ul data-testid="recommended-mvp-scope" class="grid gap-2 md:grid-cols-3">
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
        class="rounded border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-600"
      >
        생성된 보고서가 여기에 표시됩니다.
      </section>
    </section>
  </main>
</template>

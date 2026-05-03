<script setup lang="ts">
import { computed, ref } from "vue";
import { createIdeaReport } from "../../api/ideaReports";
import type { Competitor, IdeaReportResponse, SourceConfidence } from "../../types/ideaReport";

const idea = ref("동네 소상공인을 위한 AI 리뷰 분석 도구");
const report = ref<IdeaReportResponse | null>(null);
const isLoading = ref(false);
const errorMessage = ref("");

const canSubmit = computed(() => idea.value.trim().length >= 5 && !isLoading.value);

const confidenceLabel: Record<SourceConfidence, string> = {
  low: "낮음",
  medium: "보통",
  high: "높음",
};

async function submitReport() {
  if (!canSubmit.value) {
    return;
  }

  isLoading.value = true;
  errorMessage.value = "";

  try {
    report.value = await createIdeaReport({
      idea: idea.value.trim(),
      locale: "ko-KR",
    });
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "보고서를 생성하지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

function competitorMarketLabel(competitor: Competitor) {
  return competitor.market === "domestic_kr" ? "국내" : "해외";
}
</script>

<template>
  <main class="min-h-screen bg-slate-50 text-slate-950">
    <section class="mx-auto flex w-full max-w-6xl flex-col gap-6 px-5 py-6 sm:px-6 lg:px-8">
      <header class="border-b border-slate-200 pb-4">
        <p class="text-sm font-medium text-slate-500">Idea Maker</p>
        <h1 class="mt-2 text-3xl font-semibold">아이디어 보고서 생성</h1>
      </header>

      <form class="grid gap-4 border-b border-slate-200 pb-6" @submit.prevent="submitReport">
        <label class="text-sm font-medium" for="idea">아이디어</label>
        <textarea
          id="idea"
          v-model="idea"
          data-testid="idea-input"
          class="min-h-36 resize-y rounded border border-slate-300 bg-white p-3 text-base leading-7 outline-none transition focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100"
          placeholder="예: 동네 소상공인을 위한 AI 리뷰 분석 도구"
        />
        <div class="flex flex-wrap items-center gap-3">
          <button
            data-testid="generate-report"
            class="min-h-10 rounded bg-emerald-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
            type="submit"
            :disabled="!canSubmit"
          >
            {{ isLoading ? "생성 중" : "보고서 생성" }}
          </button>
          <p v-if="idea.trim().length < 5" class="text-sm text-slate-500">
            아이디어를 5자 이상 입력하세요.
          </p>
          <p v-if="errorMessage" data-testid="report-error" class="text-sm font-medium text-red-700">
            {{ errorMessage }}
          </p>
        </div>
      </form>

      <section
        v-if="report"
        data-testid="report-summary"
        class="grid gap-6"
        aria-live="polite"
      >
        <section class="grid gap-3">
          <h2 class="text-xl font-semibold">요약</h2>
          <p class="rounded border border-slate-200 bg-white p-4 leading-7 text-slate-700">
            {{ report.overview }}
          </p>
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

        <section class="grid gap-3">
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
        </section>

        <section class="grid gap-4 lg:grid-cols-2">
          <div class="grid gap-3">
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

          <div class="grid gap-3">
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

        <section class="grid gap-3">
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

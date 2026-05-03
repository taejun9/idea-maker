<script setup lang="ts">
import type {
  Competitor,
  IdeaReportResponse,
  SourceConfidence,
} from '../../types/ideaReport';
import IdeaIntakeQuestions from './IdeaIntakeQuestions.vue';

defineProps<{
  report: IdeaReportResponse;
}>();

const confidenceLabel: Record<SourceConfidence, string> = {
  low: '낮음',
  medium: '보통',
  high: '높음',
};

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
  <section data-testid="report-summary" class="grid gap-6" aria-live="polite">
    <header class="grid gap-2 border-b border-slate-200 pb-4">
      <p class="text-sm font-medium text-slate-500">보고서 상세</p>
      <h2 class="text-2xl font-semibold leading-tight text-slate-950">
        {{ report.idea }}
      </h2>
      <p class="text-sm text-slate-600">
        생성 {{ formatDateTime(report.created_at) }}
      </p>
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

    <!-- <section
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
    </section> -->

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
          <p class="mt-2 text-sm leading-6 text-slate-700">{{ source.note }}</p>
          <p class="mt-3 text-xs text-slate-500">
            {{ source.observed_date }} · 신뢰도
            {{ confidenceLabel[source.confidence] }}
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
</template>

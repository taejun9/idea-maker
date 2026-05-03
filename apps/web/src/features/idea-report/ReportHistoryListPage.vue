<script setup lang="ts">
import { onMounted, ref } from "vue";
import { deleteIdeaReport, listIdeaReports } from "../../api/ideaReports";
import type { IdeaReportSummary } from "../../types/ideaReport";

const reports = ref<IdeaReportSummary[]>([]);
const isLoading = ref(true);
const deletingReportId = ref("");
const errorMessage = ref("");
const deleteErrorMessage = ref("");

onMounted(() => {
  void loadReports();
});

async function loadReports() {
  isLoading.value = true;
  errorMessage.value = "";
  deleteErrorMessage.value = "";

  try {
    const response = await listIdeaReports();
    reports.value = response.reports;
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "보고서 목록을 조회하지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}

async function deleteReport(reportId: string) {
  deletingReportId.value = reportId;
  deleteErrorMessage.value = "";

  try {
    await deleteIdeaReport(reportId);
    reports.value = reports.value.filter((report) => report.id !== reportId);
  } catch (error) {
    deleteErrorMessage.value =
      error instanceof Error ? error.message : "보고서를 삭제하지 못했습니다.";
  } finally {
    deletingReportId.value = "";
  }
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function businessFieldLabel(value: string | null | undefined) {
  return value?.trim() || "분야 미정";
}
</script>

<template>
  <div class="mx-auto flex w-full max-w-5xl flex-col gap-8 px-5 py-8 sm:px-6 lg:px-8">
    <header class="mb-2">
      <p class="text-sm font-semibold tracking-wide text-emerald-600 uppercase">Idea Maker</p>
      <h1 class="mt-2 text-3xl font-extrabold tracking-tight text-slate-900 sm:text-4xl">조회한 보고서</h1>
    </header>

      <p
        v-if="isLoading"
        class="flex items-center justify-center rounded-2xl bg-white p-12 text-sm font-medium text-slate-500 shadow-sm ring-1 ring-slate-200/60"
        role="status"
      >
        보고서 목록을 불러오고 있습니다.
      </p>

      <p
        v-else-if="errorMessage"
        class="rounded-xl border border-red-200 bg-red-50 p-6 text-sm font-medium text-red-700 shadow-sm"
        data-testid="history-error"
        role="alert"
      >
        {{ errorMessage }}
      </p>

      <section
        v-else-if="reports.length > 0"
        class="grid gap-4"
        data-testid="report-history-list"
      >
        <p
          v-if="deleteErrorMessage"
          class="rounded border border-red-200 bg-white p-4 text-sm font-medium text-red-700"
          data-testid="history-delete-error"
          role="alert"
        >
          {{ deleteErrorMessage }}
        </p>

        <article
          v-for="report in reports"
          :key="report.id"
          class="grid gap-4 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200/60 transition-shadow hover:shadow-md sm:p-8"
        >
          <div class="flex flex-wrap items-start justify-between gap-4">
            <div class="grid gap-2">
              <p class="text-xs font-semibold text-slate-500">{{ formatDateTime(report.created_at) }}</p>
              <h2 class="text-xl font-bold leading-tight text-slate-900">
                {{ report.idea }}
              </h2>
            </div>
            <div class="flex shrink-0 flex-wrap gap-2">
              <a
                class="rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700 focus:outline-none focus:ring-4 focus:ring-slate-500/20"
                data-testid="history-detail-link"
                :href="`#/reports/${report.id}`"
              >
                열기
              </a>
              <button
                class="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-red-600 shadow-sm ring-1 ring-inset ring-red-200 transition-all hover:bg-red-50 focus:outline-none focus:ring-4 focus:ring-red-500/20 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-400 disabled:ring-slate-200"
                data-testid="history-delete-report"
                type="button"
                :disabled="deletingReportId === report.id"
                @click="deleteReport(report.id)"
              >
                {{ deletingReportId === report.id ? "삭제 중" : "삭제" }}
              </button>
            </div>
          </div>
          <p class="text-sm leading-6 text-slate-700">{{ report.overview }}</p>
          <dl class="flex flex-wrap gap-2 text-xs text-slate-600">
            <div
              class="rounded bg-emerald-50 px-2 py-1 text-emerald-800"
              data-testid="history-business-field"
            >
              <dt class="sr-only">사업 분야</dt>
              <dd>Q5 {{ businessFieldLabel(report.business_field) }}</dd>
            </div>
            <div class="rounded bg-slate-100 px-2 py-1">
              <dt class="sr-only">국내 경쟁 서비스 수</dt>
              <dd>국내 {{ report.domestic_competitor_count }}</dd>
            </div>
            <div class="rounded bg-slate-100 px-2 py-1">
              <dt class="sr-only">해외 경쟁 서비스 수</dt>
              <dd>해외 {{ report.overseas_competitor_count }}</dd>
            </div>
            <div class="rounded bg-slate-100 px-2 py-1">
              <dt class="sr-only">소스 수</dt>
              <dd>소스 {{ report.source_reference_count }}</dd>
            </div>
            <div
              v-if="report.research_requested"
              class="rounded bg-emerald-50 px-2 py-1 text-emerald-800"
            >
              <dt class="sr-only">검색 사용 여부</dt>
              <dd>검색 정리 포함</dd>
            </div>
          </dl>
        </article>
      </section>

      <section
        v-else
        class="flex items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-12 text-center text-slate-500"
        data-testid="report-history-empty"
      >
        아직 조회한 보고서가 없습니다.
      </section>
  </div>
</template>

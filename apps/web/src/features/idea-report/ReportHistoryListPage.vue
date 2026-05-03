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
</script>

<template>
  <main class="min-h-screen bg-slate-50 text-slate-950">
    <section class="mx-auto grid w-full max-w-6xl gap-6 px-5 py-6 sm:px-6 lg:px-8">
      <header class="grid gap-2 border-b border-slate-200 pb-4">
        <p class="text-sm font-medium text-slate-500">Idea Maker</p>
        <h1 class="text-3xl font-semibold">조회한 보고서</h1>
      </header>

      <p
        v-if="isLoading"
        class="rounded border border-slate-200 bg-white p-4 text-sm text-slate-600"
        role="status"
      >
        보고서 목록을 불러오고 있습니다.
      </p>

      <p
        v-else-if="errorMessage"
        class="rounded border border-red-200 bg-white p-4 text-sm font-medium text-red-700"
        data-testid="history-error"
        role="alert"
      >
        {{ errorMessage }}
      </p>

      <section
        v-else-if="reports.length > 0"
        class="grid gap-3"
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
          class="grid gap-3 rounded border border-slate-200 bg-white p-4"
        >
          <div class="flex flex-wrap items-start justify-between gap-3">
            <div class="grid gap-2">
              <p class="text-sm text-slate-500">{{ formatDateTime(report.created_at) }}</p>
              <h2 class="text-lg font-semibold leading-6 text-slate-950">
                {{ report.idea }}
              </h2>
            </div>
            <div class="flex shrink-0 flex-wrap gap-2">
              <a
                class="rounded bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-300"
                data-testid="history-detail-link"
                :href="`#/reports/${report.id}`"
              >
                열기
              </a>
              <button
                class="rounded border border-red-200 bg-white px-3 py-2 text-sm font-semibold text-red-700 transition hover:border-red-400 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-100 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
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
        class="rounded border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-600"
        data-testid="report-history-empty"
      >
        아직 조회한 보고서가 없습니다.
      </section>
    </section>
  </main>
</template>

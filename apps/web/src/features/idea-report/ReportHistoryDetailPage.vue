<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { getIdeaReport } from "../../api/ideaReports";
import type { IdeaReportResponse } from "../../types/ideaReport";
import IdeaReportDetail from "./IdeaReportDetail.vue";

const props = defineProps<{
  reportId: string;
}>();

const report = ref<IdeaReportResponse | null>(null);
const isLoading = ref(true);
const errorMessage = ref("");

onMounted(() => {
  void loadReport();
});

watch(
  () => props.reportId,
  () => {
    void loadReport();
  },
);

async function loadReport() {
  isLoading.value = true;
  errorMessage.value = "";
  report.value = null;

  try {
    report.value = await getIdeaReport(props.reportId);
  } catch (error) {
    errorMessage.value =
      error instanceof Error ? error.message : "보고서 상세를 조회하지 못했습니다.";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="mx-auto flex w-full max-w-5xl flex-col gap-6 px-5 py-8 sm:px-6 lg:px-8">
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
      <a
        class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-200 focus:outline-none focus:ring-4 focus:ring-slate-200"
        href="#/reports"
      >
        목록으로
      </a>
    </div>

    <p
      v-if="isLoading"
      class="flex items-center justify-center rounded-2xl bg-white p-12 text-sm font-medium text-slate-500 shadow-sm ring-1 ring-slate-200/60"
      role="status"
    >
      보고서를 불러오고 있습니다.
    </p>

    <p
      v-else-if="errorMessage"
      class="rounded-xl border border-red-200 bg-red-50 p-6 text-sm font-medium text-red-700 shadow-sm"
      data-testid="history-detail-error"
      role="alert"
    >
      {{ errorMessage }}
    </p>

    <IdeaReportDetail v-else-if="report" :report="report" />
  </div>
</template>

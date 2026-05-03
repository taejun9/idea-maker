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
  <main class="min-h-screen bg-slate-50 text-slate-950">
    <section class="mx-auto grid w-full max-w-6xl gap-6 px-5 py-6 sm:px-6 lg:px-8">
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 pb-4">
        <a
          class="rounded border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:border-emerald-500 hover:text-emerald-800 focus:outline-none focus:ring-2 focus:ring-emerald-200"
          href="#/reports"
        >
          목록으로
        </a>
      </div>

      <p
        v-if="isLoading"
        class="rounded border border-slate-200 bg-white p-4 text-sm text-slate-600"
        role="status"
      >
        보고서를 불러오고 있습니다.
      </p>

      <p
        v-else-if="errorMessage"
        class="rounded border border-red-200 bg-white p-4 text-sm font-medium text-red-700"
        data-testid="history-detail-error"
        role="alert"
      >
        {{ errorMessage }}
      </p>

      <IdeaReportDetail v-else-if="report" :report="report" />
    </section>
  </main>
</template>

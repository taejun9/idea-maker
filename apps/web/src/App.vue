<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import IdeaReportPage from "./features/idea-report/IdeaReportPage.vue";
import ReportHistoryDetailPage from "./features/idea-report/ReportHistoryDetailPage.vue";
import ReportHistoryListPage from "./features/idea-report/ReportHistoryListPage.vue";

function routeFromHash() {
  const route = window.location.hash.replace(/^#/, "") || "/";
  return route.startsWith("/") ? route : `/${route}`;
}

const currentRoute = ref(routeFromHash());
const reportDetailId = computed(() => {
  const match = currentRoute.value.match(/^\/reports\/([^/]+)$/);
  return match ? decodeURIComponent(match[1]) : "";
});
const currentPage = computed(() => {
  if (reportDetailId.value) {
    return "detail";
  }

  if (currentRoute.value === "/reports") {
    return "history";
  }

  return "create";
});

function updateRoute() {
  currentRoute.value = routeFromHash();
}

onMounted(() => {
  window.addEventListener("hashchange", updateRoute);
});

onBeforeUnmount(() => {
  window.removeEventListener("hashchange", updateRoute);
});
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <nav class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex w-full max-w-6xl flex-wrap items-center gap-2 px-5 py-3 sm:px-6 lg:px-8">
        <a
          class="rounded px-3 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-200"
          :class="
            currentPage === 'create'
              ? 'bg-emerald-700 text-white'
              : 'text-slate-700 hover:bg-slate-100'
          "
          data-testid="nav-create-report"
          href="#/"
        >
          보고서 생성
        </a>
        <a
          class="rounded px-3 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-200"
          :class="
            currentPage === 'history' || currentPage === 'detail'
              ? 'bg-emerald-700 text-white'
              : 'text-slate-700 hover:bg-slate-100'
          "
          data-testid="nav-report-history"
          href="#/reports"
        >
          조회한 보고서
        </a>
      </div>
    </nav>

    <ReportHistoryDetailPage
      v-if="reportDetailId"
      :key="reportDetailId"
      :report-id="reportDetailId"
    />
    <ReportHistoryListPage v-else-if="currentRoute === '/reports'" />
    <IdeaReportPage v-else />
  </div>
</template>

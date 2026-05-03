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
  <div class="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-emerald-200 selection:text-emerald-900">
    <nav class="sticky top-0 z-50 border-b border-slate-200/80 bg-white/80 backdrop-blur-md">
      <div class="mx-auto flex w-full max-w-6xl items-center justify-between px-5 py-3 sm:px-6 lg:px-8">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-2">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-sm">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M4.93 19.07l2.83-2.83"/><path d="M16.24 7.76l2.83-2.83"/></svg>
            </div>
            <span class="text-lg font-bold tracking-tight text-slate-900">Idea Maker</span>
          </div>
          <div class="flex items-center gap-1">
            <a
              class="rounded-lg px-4 py-2.5 text-sm font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-emerald-200"
              :class="
                currentPage === 'create'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              "
              data-testid="nav-create-report"
              href="#/"
            >
              보고서 생성
            </a>
            <a
              class="rounded-lg px-4 py-2.5 text-sm font-semibold transition-all focus:outline-none focus:ring-2 focus:ring-emerald-200"
              :class="
                currentPage === 'history' || currentPage === 'detail'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              "
              data-testid="nav-report-history"
              href="#/reports"
            >
              조회한 보고서
            </a>
          </div>
        </div>
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

<template>
  <main class="min-h-screen bg-white text-slate-950">
    <section class="mx-auto flex w-full max-w-5xl flex-col gap-6 px-6 py-8">
      <header class="border-b border-slate-200 pb-4">
        <p class="text-sm font-medium text-slate-500">Idea Maker</p>
        <h1 class="mt-2 text-3xl font-semibold">아이디어 보고서 생성</h1>
      </header>
      <section class="grid gap-4">
        <label class="text-sm font-medium" for="idea">아이디어</label>
        <textarea
          id="idea"
          data-testid="idea-input"
          class="min-h-36 rounded border border-slate-300 p-3"
          placeholder="예: 동네 소상공인을 위한 AI 리뷰 분석 도구"
        />
        <button
          data-testid="generate-report"
          class="w-fit rounded bg-slate-950 px-4 py-2 text-sm font-semibold text-white"
          type="button"
        >
          보고서 생성
        </button>
      </section>
      <section data-testid="report-summary" class="rounded border border-slate-200 p-4">
        <h2 class="text-lg font-semibold">MVP 보고서 영역</h2>
        <p class="mt-2 text-sm text-slate-600">
          PLAN-0001에서 API 연동, 국내/해외 경쟁사, 추천 소스 섹션을 연결한다.
        </p>
      </section>
    </section>
  </main>
</template>


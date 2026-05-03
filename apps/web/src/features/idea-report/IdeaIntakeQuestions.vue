<script setup lang="ts">
import type { IdeaIntakeQuestion } from "../../types/ideaReport";

defineProps<{
  questions: IdeaIntakeQuestion[];
}>();
</script>

<template>
  <section
    v-if="questions.length > 0"
    class="grid gap-3"
    data-testid="idea-intake-questions"
  >
    <h2 class="text-lg font-semibold">아이디어 입력 문항</h2>
    <div class="grid gap-3 lg:grid-cols-2">
      <article
        v-for="question in questions"
        :key="question.code"
        class="grid gap-3 rounded border border-slate-200 bg-white p-4"
      >
        <div class="flex flex-wrap items-start gap-3">
          <span class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
            {{ question.code }}
          </span>
          <div class="grid min-w-0 flex-1 gap-1">
            <h3 class="text-base font-semibold leading-6 text-slate-950">
              {{ question.prompt }}
            </h3>
            <p class="text-sm text-slate-600">{{ question.requirement }}</p>
          </div>
        </div>
        <p
          v-if="question.photo_guidance"
          class="text-sm leading-6 text-slate-700"
        >
          {{ question.photo_guidance }}
        </p>
        <p
          v-if="question.options.length > 0"
          class="break-words text-sm leading-6 text-slate-700"
        >
          선택지: {{ question.options.join(" | ") }}
        </p>
        <dl
          v-if="question.answer"
          class="grid gap-1 rounded border border-emerald-100 bg-emerald-50 p-3 text-sm"
          data-testid="idea-intake-answer"
        >
          <dt class="font-semibold text-emerald-900">입력값</dt>
          <dd class="break-words leading-6 text-slate-800">{{ question.answer }}</dd>
        </dl>
      </article>
    </div>
  </section>
</template>

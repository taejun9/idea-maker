<script setup lang="ts">
withDefaults(defineProps<{
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  layout?: 'col' | 'row';
}>(), {
  size: 'md',
  layout: 'col'
});
</script>

<template>
  <div 
    class="flex items-center"
    :class="{
      'flex-col justify-center py-8 px-4 gap-4': layout === 'col',
      'flex-row gap-3': layout === 'row'
    }"
    role="status" 
    aria-live="polite"
  >
    <div
      class="relative flex items-center justify-center shrink-0"
      :class="{
        'w-6 h-6': size === 'sm',
        'w-12 h-12': size === 'md',
        'w-16 h-16': size === 'lg'
      }"
    >
      <!-- Background track -->
      <div 
        class="absolute inset-0 rounded-full border-emerald-100"
        :class="size === 'sm' ? 'border-2' : 'border-[3px]'"
      ></div>
      
      <!-- Spinning gradient ring -->
      <div 
        class="absolute inset-0 rounded-full border-transparent border-t-emerald-600 border-r-emerald-500 animate-[spin_0.8s_linear_infinite]"
        :class="size === 'sm' ? 'border-2' : 'border-[3px]'"
      ></div>
      
      <!-- Inner pulsing dot -->
      <div 
        class="rounded-full bg-emerald-500 animate-pulse shadow-sm shadow-emerald-500/50"
        :class="{
          'w-1.5 h-1.5': size === 'sm',
          'w-2.5 h-2.5': size === 'md',
          'w-3 h-3': size === 'lg'
        }"
      ></div>
    </div>
    <p 
      v-if="message || $slots.default" 
      class="font-medium text-slate-600 animate-pulse"
      :class="{
        'text-sm': size === 'sm',
        'text-sm tracking-wide font-semibold': size !== 'sm'
      }"
    >
      <slot>{{ message }}</slot>
    </p>
  </div>
</template>

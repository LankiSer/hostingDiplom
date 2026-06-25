<script setup lang="ts">
import { computed } from 'vue';
import { classNames } from '../../../utils/class-names';

const props = withDefaults(
  defineProps<{
    message: string;
    title?: string;
    tone?: 'info' | 'preview' | 'warning';
  }>(),
  { tone: 'info' },
);

const boxClass = computed(() =>
  classNames(
    'rounded-xl border px-4 py-3 text-sm leading-6',
    props.tone === 'info' && 'border-sky-100 bg-sky-50 text-sky-900',
    props.tone === 'preview' && 'border-violet-100 bg-violet-50 text-violet-900',
    props.tone === 'warning' && 'border-amber-100 bg-amber-50 text-amber-900',
  ),
);
</script>

<template>
  <div :class="boxClass">
    <p v-if="title" class="mb-1 font-medium">{{ title }}</p>
    <p>{{ message }}</p>
  </div>
</template>

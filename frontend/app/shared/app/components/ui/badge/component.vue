<script setup lang="ts">
import { computed } from 'vue';
import { classNames } from '../../../utils/class-names';
import type { AppBadgeProps } from './interface';

const props = withDefaults(defineProps<AppBadgeProps>(), {
  tone: 'default'
});

const badgeClassName = computed(() =>
  classNames(
    'inline-flex rounded-full border px-2.5 py-0.5 text-xs font-medium',
    props.tone === 'default' && 'border-sky-200 bg-sky-50 text-sky-700',
    props.tone === 'success' && 'border-emerald-200 bg-emerald-50 text-emerald-700',
    props.tone === 'warning' && 'border-amber-200 bg-amber-50 text-amber-700',
    props.tone === 'danger' && 'border-rose-200 bg-rose-50 text-rose-700',
    props.tone === 'muted' && 'border-slate-200 bg-slate-100 text-slate-600'
  )
);
</script>

<template>
  <span :class="badgeClassName">{{ label }}</span>
</template>

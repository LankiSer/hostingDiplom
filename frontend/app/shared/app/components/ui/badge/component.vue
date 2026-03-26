<script setup lang="ts">
import { computed } from 'vue';
import { classNames } from '../../../utils/class-names';
import type { AppBadgeProps } from './interface';

const props = withDefaults(defineProps<AppBadgeProps>(), {
  tone: 'default'
});

const badgeClassName = computed(() =>
  classNames(
    'inline-flex rounded-full border px-3 py-1 text-xs font-medium',
    props.tone === 'default' && 'border-sky-400/20 bg-sky-400/10 text-sky-200',
    props.tone === 'success' && 'border-emerald-400/20 bg-emerald-400/10 text-emerald-200',
    props.tone === 'warning' && 'border-amber-400/20 bg-amber-400/10 text-amber-200',
    props.tone === 'danger' && 'border-rose-400/20 bg-rose-400/10 text-rose-200',
    props.tone === 'muted' && 'border-slate-700/40 bg-slate-800/40 text-slate-400'
  )
);
</script>

<template>
  <span :class="badgeClassName">{{ label }}</span>
</template>

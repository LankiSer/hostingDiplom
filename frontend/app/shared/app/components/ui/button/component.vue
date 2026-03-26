<script setup lang="ts">
import { computed } from 'vue';
import { classNames } from '../../../utils/class-names';
import type { AppButtonProps } from './interface';

const props = withDefaults(defineProps<AppButtonProps>(), {
  tone: 'primary',
  type: 'button'
});

const buttonClassName = computed(() =>
  classNames(
    'inline-flex items-center justify-center rounded-xl px-3.5 py-2.5 text-sm font-medium transition',
    props.disabled && 'cursor-not-allowed opacity-60',
    props.tone === 'primary' && 'bg-sky-500 text-slate-950 hover:bg-sky-400',
    props.tone === 'secondary' && 'border border-white/10 bg-white/5 text-slate-100 hover:bg-white/10'
  )
);
</script>

<template>
  <button :type="type" :disabled="disabled" :class="buttonClassName">
    {{ label }}
  </button>
</template>

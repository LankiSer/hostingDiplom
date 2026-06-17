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
    'inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-sm font-medium transition',
    props.disabled && 'cursor-not-allowed opacity-60',
    props.tone === 'primary' && 'bg-sky-600 text-white hover:bg-sky-700 shadow-sm',
    props.tone === 'secondary' && 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
  )
);
</script>

<template>
  <button :type="type" :disabled="disabled" :class="buttonClassName">
    {{ label }}
  </button>
</template>

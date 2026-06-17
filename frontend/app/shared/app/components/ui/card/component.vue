<script setup lang="ts">
import { computed } from 'vue';
import { classNames } from '../../../utils/class-names';
import type { AppCardProps } from './interface';

const props = withDefaults(defineProps<AppCardProps>(), {
  padded: true
});

const cardClassName = computed(() =>
  classNames(
    'overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm',
    props.padded && 'p-4'
  )
);
</script>

<template>
  <article :class="cardClassName">
    <slot />
  </article>
</template>

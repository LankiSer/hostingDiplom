<script setup lang="ts">
import { classNames } from '../../../../utils/class-names';
import type { AppSkeletonBoxProps } from './interface';

defineProps<AppSkeletonBoxProps>();
</script>

<template>
  <div
    :class="classNames(
      'animate-pulse rounded-2xl bg-white/10',
      className ?? 'h-4 w-full'
    )"
  />
</template>

<script setup lang="ts">
import type { AppSectionProps } from './interface';

defineProps<AppSectionProps>();
</script>

<template>
  <section class="grid gap-4">
    <div v-if="title || description">
      <h2 class="text-base font-semibold text-slate-900">{{ title }}</h2>
      <p v-if="description" class="mt-0.5 text-sm text-slate-500">{{ description }}</p>
    </div>
    <slot />
  </section>
</template>

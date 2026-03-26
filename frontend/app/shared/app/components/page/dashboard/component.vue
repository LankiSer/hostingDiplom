<script setup lang="ts">
import DashboardPageClient from './component.client.vue';
import DashboardPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <DashboardPageClient />
    <template #fallback>
      <DashboardPageSkeleton />
    </template>
  </ClientOnly>
</template>

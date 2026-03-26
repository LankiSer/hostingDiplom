<script setup lang="ts">
import ApplicationsPageClient from './component.client.vue';
import ApplicationsPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <ApplicationsPageClient />
    <template #fallback>
      <ApplicationsPageSkeleton />
    </template>
  </ClientOnly>
</template>

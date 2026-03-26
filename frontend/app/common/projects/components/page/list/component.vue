<script setup lang="ts">
import ProjectsListPageClient from './component.client.vue';
import ProjectsListPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <ProjectsListPageClient />
    <template #fallback>
      <ProjectsListPageSkeleton />
    </template>
  </ClientOnly>
</template>

<script setup lang="ts">
import ProjectDetailsPageClient from './component.client.vue';
import ProjectDetailsPageSkeleton from './skeleton.vue';
import type { ProjectDetailsPageProps } from './interface';

defineProps<ProjectDetailsPageProps>();
</script>

<template>
  <ClientOnly>
    <ProjectDetailsPageClient :project-id="projectId" />
    <template #fallback>
      <ProjectDetailsPageSkeleton />
    </template>
  </ClientOnly>
</template>

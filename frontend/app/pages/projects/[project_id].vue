<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from '#imports';
import ProjectDetailsPage from '../../common/projects/components/page/details/component.vue';
import { APP_PAGE_META } from '../../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.projectDetails.title,
  subtitle: APP_PAGE_META.projectDetails.subtitle
});

const route = useRoute();
const projectId = computed(() => String(route.params.project_id ?? 'unknown'));
</script>

<template>
  <ProjectDetailsPage :project-id="projectId" />
</template>

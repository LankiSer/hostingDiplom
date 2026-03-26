<script setup lang="ts">
import ProjectsListPage from '../../common/projects/components/page/list/component.vue';
import { APP_PAGE_META } from '../../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.projects.title,
  subtitle: APP_PAGE_META.projects.subtitle
});
</script>

<template>
  <ProjectsListPage />
</template>

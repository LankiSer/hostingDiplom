<script setup lang="ts">
import ApplicationsPage from '../../common/applications/components/page/component.vue';
import { APP_PAGE_META } from '../../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.applications.title,
  subtitle: APP_PAGE_META.applications.subtitle
});
</script>

<template>
  <ApplicationsPage />
</template>

<script setup lang="ts">
import DashboardPage from '../shared/app/components/page/dashboard/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.dashboard.title,
  subtitle: APP_PAGE_META.dashboard.subtitle
});
</script>

<template>
  <DashboardPage />
</template>

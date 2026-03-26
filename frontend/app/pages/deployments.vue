<script setup lang="ts">
import DeploymentsPage from '../common/deployments/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.deployments.title,
  subtitle: APP_PAGE_META.deployments.subtitle
});
</script>

<template>
  <DeploymentsPage />
</template>

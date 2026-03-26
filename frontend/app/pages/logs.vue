<script setup lang="ts">
import ObservabilityPage from '../common/observability/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.logs.title,
  subtitle: APP_PAGE_META.logs.subtitle
});
</script>

<template>
  <ObservabilityPage />
</template>

<script setup lang="ts">
import AccessPage from '../common/access/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.access.title,
  subtitle: APP_PAGE_META.access.subtitle
});
</script>

<template>
  <AccessPage />
</template>

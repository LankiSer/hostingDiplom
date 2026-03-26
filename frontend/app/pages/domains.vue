<script setup lang="ts">
import DomainsPage from '../common/domains/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.domains.title,
  subtitle: APP_PAGE_META.domains.subtitle
});
</script>

<template>
  <DomainsPage />
</template>

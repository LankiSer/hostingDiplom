<script setup lang="ts">
import DocumentsPage from '../common/documents/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.documents.title,
  subtitle: APP_PAGE_META.documents.subtitle
});
</script>

<template>
  <DocumentsPage />
</template>

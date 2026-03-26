<script setup lang="ts">
import BillingPage from '../common/billing/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.billing.title,
  subtitle: APP_PAGE_META.billing.subtitle
});
</script>

<template>
  <BillingPage />
</template>

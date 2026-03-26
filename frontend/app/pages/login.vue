<script setup lang="ts">
import AuthLoginPage from '../common/auth/components/page/login/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  layout: 'auth',
  middleware: 'guest',
  title: APP_PAGE_META.login.title,
  subtitle: APP_PAGE_META.login.subtitle
});
</script>

<template>
  <AuthLoginPage />
</template>

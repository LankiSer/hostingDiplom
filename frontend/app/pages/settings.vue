<script setup lang="ts">
import SettingsPage from '../common/settings/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.settings.title,
  subtitle: APP_PAGE_META.settings.subtitle
});
</script>

<template>
  <SettingsPage />
</template>

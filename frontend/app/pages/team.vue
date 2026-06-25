<script setup lang="ts">
import TeamPage from '../common/team/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.team.title,
  subtitle: APP_PAGE_META.team.subtitle,
  ssr: false  // Disable SSR for team page with Tldraw and real-time features
});
</script>

<template>
  <TeamPage />
</template>

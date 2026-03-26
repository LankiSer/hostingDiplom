<script setup lang="ts">
import TeamPage from '../common/team/components/page/component.vue';
import { APP_PAGE_META } from '../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.team.title,
  subtitle: APP_PAGE_META.team.subtitle
});
</script>

<template>
  <TeamPage />
</template>

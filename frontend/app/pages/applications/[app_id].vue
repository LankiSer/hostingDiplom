<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from '#imports';
import AppDetailClient from '../../common/applications/components/page/detail/component.client.vue';

definePageMeta({ middleware: 'auth' });
const route = useRoute();
const appId = computed(() => String(route.params.app_id ?? ''));
</script>

<template>
  <ClientOnly>
    <AppDetailClient :app-id="appId" />
    <template #fallback>
      <div class="h-32 animate-pulse rounded-xl bg-slate-800/40" />
    </template>
  </ClientOnly>
</template>

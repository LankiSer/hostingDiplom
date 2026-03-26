<script setup lang="ts">
import SettingsPageClient from './component.client.vue';
import SettingsPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <SettingsPageClient />
    <template #fallback>
      <SettingsPageSkeleton />
    </template>
  </ClientOnly>
</template>

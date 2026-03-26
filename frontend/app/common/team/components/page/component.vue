<script setup lang="ts">
import TeamPageClient from './component.client.vue';
import TeamPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <TeamPageClient />
    <template #fallback>
      <TeamPageSkeleton />
    </template>
  </ClientOnly>
</template>

<script setup lang="ts">
import DomainsPageClient from './component.client.vue';
import DomainsPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <DomainsPageClient />
    <template #fallback>
      <DomainsPageSkeleton />
    </template>
  </ClientOnly>
</template>

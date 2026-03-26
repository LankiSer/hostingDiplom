<script setup lang="ts">
import DeploymentsPageClient from './component.client.vue';
import DeploymentsPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <DeploymentsPageClient />
    <template #fallback>
      <DeploymentsPageSkeleton />
    </template>
  </ClientOnly>
</template>

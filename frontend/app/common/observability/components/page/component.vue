<script setup lang="ts">
import ObservabilityPageClient from './component.client.vue';
import ObservabilityPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <ObservabilityPageClient />
    <template #fallback>
      <ObservabilityPageSkeleton />
    </template>
  </ClientOnly>
</template>

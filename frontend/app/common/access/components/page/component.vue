<script setup lang="ts">
import AccessPageClient from './component.client.vue';
import AccessPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <AccessPageClient />
    <template #fallback>
      <AccessPageSkeleton />
    </template>
  </ClientOnly>
</template>

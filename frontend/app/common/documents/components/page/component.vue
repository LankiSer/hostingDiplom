<script setup lang="ts">
import DocumentsPageClient from './component.client.vue';
import DocumentsPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <DocumentsPageClient />
    <template #fallback>
      <DocumentsPageSkeleton />
    </template>
  </ClientOnly>
</template>

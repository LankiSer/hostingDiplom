<script setup lang="ts">
import AuthLoginPageClient from './component.client.vue';
import AuthLoginPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <AuthLoginPageClient />
    <template #fallback>
      <AuthLoginPageSkeleton />
    </template>
  </ClientOnly>
</template>

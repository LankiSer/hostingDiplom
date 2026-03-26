<script setup lang="ts">
import BillingPageClient from './component.client.vue';
import BillingPageSkeleton from './skeleton.vue';
</script>

<template>
  <ClientOnly>
    <BillingPageClient />
    <template #fallback>
      <BillingPageSkeleton />
    </template>
  </ClientOnly>
</template>

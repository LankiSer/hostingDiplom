<script setup lang="ts">
import MicroserviceDetailsPageClient from './component.client.vue';
import MicroserviceDetailsPageSkeleton from './skeleton.vue';
import type { MicroserviceDetailsPageProps } from './interface';

defineProps<MicroserviceDetailsPageProps>();
</script>

<template>
  <ClientOnly>
    <MicroserviceDetailsPageClient :service-id="serviceId" />
    <template #fallback>
      <MicroserviceDetailsPageSkeleton />
    </template>
  </ClientOnly>
</template>

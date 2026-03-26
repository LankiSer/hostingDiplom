<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from '#imports';
import MicroserviceDetailsPage from '../../common/microservices/components/page/details/component.vue';
import { APP_PAGE_META } from '../../shared/app/constants/page-meta';

definePageMeta({
  middleware: 'auth',
  title: APP_PAGE_META.serviceDetails.title,
  subtitle: APP_PAGE_META.serviceDetails.subtitle
});

const route = useRoute();
const serviceId = computed(() => String(route.params.service_id ?? 'unknown'));
</script>

<template>
  <MicroserviceDetailsPage :service-id="serviceId" />
</template>

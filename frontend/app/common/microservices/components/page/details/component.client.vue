<script setup lang="ts">
import WorkspaceRemotePage from '../../../../../shared/app/components/page/remote/component.vue';
import type { MicroserviceDetailsPageProps } from './interface';

const props = defineProps<MicroserviceDetailsPageProps>();
</script>

<template>
  <WorkspaceRemotePage :cache-key="`application-${props.serviceId}`" :path="`/api/v1/platform/applications/${props.serviceId}`" />
</template>

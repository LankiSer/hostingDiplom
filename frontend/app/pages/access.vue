<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
});

await navigateTo({ path: '/team', query: { tab: 'roles' } }, { replace: true });
</script>

<template>
  <div />
</template>

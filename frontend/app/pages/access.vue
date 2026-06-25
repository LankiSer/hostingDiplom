<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
});

await navigateTo('/team', { replace: true });
</script>

<template>
  <div />
</template>

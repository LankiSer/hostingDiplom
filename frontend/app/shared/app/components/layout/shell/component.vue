<script setup lang="ts">
import AppHeader from '../../navigation/header/component.vue';
import AppSidebar from '../../navigation/sidebar/component.vue';
import type { AppShellSlots } from './interface';

defineSlots<AppShellSlots>();
</script>

<template>
  <div class="flex h-screen overflow-hidden">
    <AppSidebar />
    <main class="flex flex-1 flex-col overflow-y-auto">
      <div class="flex flex-1 flex-col gap-5 px-6 py-5">
        <AppHeader />
        <slot />
      </div>
    </main>
  </div>
</template>

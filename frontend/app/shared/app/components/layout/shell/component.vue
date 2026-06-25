<script setup lang="ts">
import AppHeader from '../../navigation/header/component.vue';
import AppSidebar from '../../navigation/sidebar/component.vue';
import type { AppShellSlots } from './interface';

defineSlots<AppShellSlots>();
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.06),transparent_40%),radial-gradient(circle_at_bottom_right,rgba(245,158,11,0.05),transparent_35%),#f8fafc]">
    <AppSidebar />
    <main class="flex flex-1 flex-col overflow-y-auto">
      <div class="flex flex-1 flex-col gap-6 px-6 py-6 lg:px-8">
        <AppHeader />
        <div class="flex flex-1 flex-col gap-6 pb-6">
          <slot />
          <LegalFooter />
        </div>
      </div>
    </main>
  </div>
</template>

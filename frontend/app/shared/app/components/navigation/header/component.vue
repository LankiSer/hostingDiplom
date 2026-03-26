<script setup lang="ts">
import { computed } from 'vue';
import { navigateTo, useRoute } from '#imports';
import { useSession } from '../../../hooks/use-session';
import type { AppHeaderMeta } from './interface';

const route = useRoute();
const { clear, session } = useSession();

const meta = computed<AppHeaderMeta>(() => {
  const current = route.meta as AppHeaderMeta;
  return {
    title: current.title ?? 'Платформа',
    subtitle: current.subtitle ?? ''
  };
});

async function handleLogout() {
  clear();
  await navigateTo('/login');
}
</script>

<template>
  <header class="flex items-center justify-between border-b border-white/5 pb-4">
    <div>
      <h1 class="text-lg font-semibold text-slate-100">{{ meta.title }}</h1>
      <p v-if="meta.subtitle" class="mt-0.5 text-sm text-slate-500">{{ meta.subtitle }}</p>
    </div>
    <div class="flex items-center gap-3">
      <span class="hidden text-sm text-slate-500 sm:block">{{ session?.companyName }}</span>
      <button class="rounded-lg border border-white/10 px-3 py-1.5 text-xs text-slate-400 transition hover:border-white/20 hover:text-slate-200" @click="handleLogout">
        Выйти
      </button>
    </div>
  </header>
</template>

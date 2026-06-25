<script setup lang="ts">
import { computed, ref } from 'vue';
import { navigateTo, useRoute } from '#imports';
import { useSession } from '../../../hooks/use-session';
import type { AppHeaderMeta } from './interface';

const route = useRoute();
const { clear, session } = useSession();
const menuOpen = ref(false);

const meta = computed<AppHeaderMeta>(() => {
  const current = route.meta as AppHeaderMeta;
  return {
    title: current.title ?? 'Платформа',
    subtitle: current.subtitle ?? ''
  };
});

const roleLabel = computed(() => {
  const role = session.value?.role;
  if (role === 'owner') return 'Владелец';
  if (role === 'ops') return 'DevOps';
  if (role === 'finance') return 'Финансы';
  if (role === 'viewer') return 'Наблюдатель';
  return role ?? '';
});

function initials(name?: string) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? `${parts[0]![0]}${parts[1]![0]}`.toUpperCase() : name.slice(0, 2).toUpperCase();
}

async function handleLogout() {
  menuOpen.value = false;
  clear();
  await navigateTo('/login');
}

function toggleMenu() {
  menuOpen.value = !menuOpen.value;
}
</script>

<template>
  <header class="relative flex items-start justify-between gap-4 pb-1">
    <div class="min-w-0">
      <div class="mb-1 flex items-center gap-2 text-xs text-slate-400">
        <span>{{ session?.companyName }}</span>
        <span v-if="roleLabel" class="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-700">{{ roleLabel }}</span>
      </div>
      <h1 class="text-2xl font-semibold tracking-tight text-slate-900">{{ meta.title }}</h1>
      <p v-if="meta.subtitle" class="mt-1 max-w-2xl text-sm text-slate-500">{{ meta.subtitle }}</p>
    </div>

    <div class="relative shrink-0">
      <button
        class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 shadow-sm transition hover:border-sky-200 hover:shadow"
        type="button"
        @click="toggleMenu"
      >
        <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-xs font-semibold text-white">
          {{ initials(session?.displayName) }}
        </span>
        <span class="hidden text-left sm:block">
          <span class="block text-sm font-medium text-slate-800">{{ session?.displayName }}</span>
          <span class="block text-xs text-slate-500">{{ session?.email }}</span>
        </span>
      </button>

      <div
        v-if="menuOpen"
        class="absolute right-0 top-[calc(100%+8px)] z-20 w-52 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl"
      >
        <div class="border-b border-slate-100 px-4 py-3">
          <p class="truncate text-sm font-medium text-slate-900">{{ session?.displayName }}</p>
          <p class="truncate text-xs text-slate-500">{{ session?.email }}</p>
        </div>
        <div class="grid p-1">
          <NuxtLink class="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" to="/settings" @click="menuOpen = false">Настройки</NuxtLink>
          <NuxtLink class="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" to="/team" @click="menuOpen = false">Команда</NuxtLink>
          <NuxtLink class="rounded-lg px-3 py-2 text-sm text-slate-700 hover:bg-slate-50" to="/legal" @click="menuOpen = false">Юридическая информация</NuxtLink>
          <button class="rounded-lg px-3 py-2 text-left text-sm text-rose-600 hover:bg-rose-50" type="button" @click="handleLogout">Выйти</button>
        </div>
      </div>
    </div>
  </header>
</template>

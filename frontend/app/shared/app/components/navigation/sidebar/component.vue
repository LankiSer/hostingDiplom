<script setup lang="ts">
import { useRoute } from '#imports';
import NavIcon from '../nav-icon/component.vue';
import { useNavigation } from '../../../hooks/use-navigation';
import { useSession } from '../../../hooks/use-session';
import { classNames } from '../../../utils/class-names';

const route = useRoute();
const { grouped } = useNavigation();
const { session } = useSession();

function isActive(to: string) {
  return route.path === to || route.path.startsWith(`${to}/`);
}

function initials(name?: string) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  return parts.length >= 2 ? `${parts[0]![0]}${parts[1]![0]}`.toUpperCase() : name.slice(0, 2).toUpperCase();
}
</script>

<template>
  <aside class="app-sidebar flex h-screen w-[268px] shrink-0 flex-col border-r border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
    <div class="border-b border-slate-100 px-5 pb-5 pt-6">
      <div class="flex items-center gap-3">
        <div class="relative flex h-10 w-10 items-center justify-center rounded-xl bg-[linear-gradient(135deg,#0284c7_0%,#0369a1_100%)] text-sm font-bold text-white shadow-[0_8px_20px_-8px_rgba(2,132,199,0.8)]">
          G
          <span class="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-amber-400" />
        </div>
        <div class="min-w-0">
          <p class="truncate text-sm font-semibold tracking-tight text-slate-900">gcloude</p>
          <p class="truncate text-[11px] text-slate-500">Cloud deploy platform</p>
        </div>
      </div>

      <div v-if="session" class="mt-4 rounded-xl border border-sky-100 bg-sky-50/70 px-3 py-2.5">
        <p class="text-[10px] font-semibold uppercase tracking-widest text-sky-600/80">Рабочее пространство</p>
        <p class="mt-0.5 truncate text-sm font-medium text-slate-800">{{ session.companyName }}</p>
      </div>
    </div>

    <nav class="flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-5">
      <div v-for="group in grouped" :key="group.group">
        <p class="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
          {{ group.label }}
        </p>
        <div class="flex flex-col gap-1">
          <NuxtLink
            v-for="item in group.items"
            :key="item.to"
            :to="item.to"
            :class="classNames(
              'group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all duration-200',
              isActive(item.to)
                ? 'bg-white font-medium text-sky-700 shadow-[0_1px_0_rgba(15,23,42,0.04),0_8px_24px_-12px_rgba(2,132,199,0.35)] ring-1 ring-sky-100'
                : 'text-slate-600 hover:bg-white/70 hover:text-slate-900'
            )"
          >
            <span
              v-if="isActive(item.to)"
              class="absolute left-0 top-1/2 h-7 w-1 -translate-y-1/2 rounded-r-full bg-[linear-gradient(180deg,#0ea5e9_0%,#f59e0b_100%)]"
            />
            <span
              :class="classNames(
                'flex h-8 w-8 items-center justify-center rounded-lg transition-colors',
                isActive(item.to) ? 'bg-sky-100 text-sky-700' : 'bg-slate-100 text-slate-500 group-hover:bg-slate-200/70 group-hover:text-slate-700'
              )"
            >
              <NavIcon :icon="item.icon" :active="isActive(item.to)" />
            </span>
            <span>{{ item.label }}</span>
          </NuxtLink>
        </div>
      </div>
    </nav>

    <div v-if="session" class="border-t border-slate-100 p-4">
      <NuxtLink
        to="/legal"
        class="mb-3 flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-slate-500 transition hover:bg-slate-50 hover:text-sky-600"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-3.5 w-3.5 shrink-0">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
        </svg>
        Юридическая информация
      </NuxtLink>
      <NuxtLink
        to="/settings"
        class="flex items-center gap-3 rounded-xl border border-slate-100 bg-white px-3 py-2.5 transition hover:border-sky-100 hover:shadow-sm"
      >
        <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[linear-gradient(135deg,#e0f2fe_0%,#fef3c7_100%)] text-xs font-semibold text-slate-700">
          {{ initials(session.displayName) }}
        </span>
        <span class="min-w-0 flex-1">
          <span class="block truncate text-sm font-medium text-slate-800">{{ session.displayName }}</span>
          <span class="block truncate text-xs text-slate-500">{{ session.email }}</span>
        </span>
      </NuxtLink>
    </div>
  </aside>
</template>

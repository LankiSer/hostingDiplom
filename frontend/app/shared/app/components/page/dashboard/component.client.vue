<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from '#imports';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';

interface Project { id: string; name: string; app_count: number }
interface App { id: string; name: string; status: string; url: string; project_name: string }
interface Deployment { id: string; status: string; git_url: string; created_at: string; app_id: string }

const { get } = usePlatformApi();
const router = useRouter();

interface Invoice { id: string; status: string }

const { data: projects } = useAsyncData<Project[]>('dash-projects', () => get('/api/v1/hosting/projects'));
const { data: apps } = useAsyncData<App[]>('dash-apps', () => get('/api/v1/hosting/apps'));
const { data: deployments } = useAsyncData<Deployment[]>('dash-deploys', () => get('/api/v1/hosting/deployments'));
const { data: invoices } = useAsyncData<Invoice[]>('dash-invoices', () => get('/api/v1/billing/invoices'));

const stats = computed(() => [
  { label: 'Проектов', value: projects.value?.length ?? 0, to: '/projects' },
  { label: 'Приложений', value: apps.value?.length ?? 0, to: '/applications' },
  { label: 'Запущено', value: apps.value?.filter(a => a.status === 'running').length ?? 0, to: '/applications' },
  { label: 'Счётов', value: invoices.value?.length ?? 0, to: '/billing' },
  { label: 'Деплоев', value: deployments.value?.length ?? 0, to: '/deployments' },
]);

const runningApps = computed(() => apps.value?.filter(a => a.status === 'running').slice(0, 5) ?? []);
const recentDeploys = computed(() => deployments.value?.slice(0, 5) ?? []);

function deployStatus(s: string) {
  return s === 'running' ? 'text-emerald-400' : s === 'building' ? 'text-amber-400' : s === 'failed' ? 'text-rose-400' : 'text-slate-500';
}

function formatDate(iso: string) {
  return iso ? new Date(iso).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '';
}
</script>

<template>
  <div class="grid gap-6">
    <!-- Stats row -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      <button
        v-for="stat in stats"
        :key="stat.label"
        class="rounded-xl border border-white/5 bg-slate-900/60 p-4 text-left transition hover:border-white/10 hover:bg-slate-900"
        @click="router.push(stat.to)"
      >
        <p class="text-2xl font-bold text-slate-100">{{ stat.value }}</p>
        <p class="mt-1 text-sm text-slate-500">{{ stat.label }}</p>
      </button>
    </div>

    <!-- Quick actions -->
    <div>
      <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-600">Быстрые действия</p>
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <button
          class="flex flex-col gap-2 rounded-xl border border-sky-500/30 bg-sky-500/10 p-4 text-left transition hover:bg-sky-500/15"
          @click="router.push('/projects')"
        >
          <span class="text-lg">🚀</span>
          <span class="text-sm font-medium text-sky-300">Задеплоить</span>
          <span class="text-xs text-slate-500">Новое приложение</span>
        </button>
        <button
          class="flex flex-col gap-2 rounded-xl border border-white/5 bg-slate-900/60 p-4 text-left transition hover:bg-slate-900"
          @click="router.push('/projects')"
        >
          <span class="text-lg">📁</span>
          <span class="text-sm font-medium text-slate-200">Проект</span>
          <span class="text-xs text-slate-500">Создать проект</span>
        </button>
        <button
          class="flex flex-col gap-2 rounded-xl border border-white/5 bg-slate-900/60 p-4 text-left transition hover:bg-slate-900"
          @click="router.push('/billing')"
        >
          <span class="text-lg">💳</span>
          <span class="text-sm font-medium text-slate-200">Биллинг</span>
          <span class="text-xs text-slate-500">Счета и оплата</span>
        </button>
        <button
          class="flex flex-col gap-2 rounded-xl border border-white/5 bg-slate-900/60 p-4 text-left transition hover:bg-slate-900"
          @click="router.push('/logs')"
        >
          <span class="text-lg">📋</span>
          <span class="text-sm font-medium text-slate-200">Логи</span>
          <span class="text-xs text-slate-500">Активность</span>
        </button>
      </div>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <!-- Running apps -->
      <div>
        <div class="mb-3 flex items-center justify-between">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-600">Запущенные приложения</p>
          <button class="text-xs text-sky-400 hover:underline" @click="router.push('/applications')">Все →</button>
        </div>
        <div v-if="!runningApps.length" class="rounded-xl border border-white/5 px-4 py-6 text-center text-sm text-slate-600">
          Нет запущенных приложений
        </div>
        <div v-else class="overflow-hidden rounded-xl border border-white/5">
          <div v-for="(app, i) in runningApps" :key="app.id"
            :class="['flex cursor-pointer items-center justify-between px-4 py-3 transition hover:bg-white/5', i > 0 && 'border-t border-white/5']"
            @click="router.push(`/applications/${app.id}`)"
          >
            <div class="min-w-0">
              <p class="truncate text-sm text-slate-200">{{ app.name }}</p>
              <p class="truncate text-xs text-slate-500">{{ app.project_name }}</p>
            </div>
            <div class="flex shrink-0 items-center gap-2">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              <a v-if="app.url" :href="app.url" target="_blank" class="text-xs text-sky-400 hover:underline" @click.stop>↗</a>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent deployments -->
      <div>
        <div class="mb-3 flex items-center justify-between">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-600">Последние деплои</p>
          <button class="text-xs text-sky-400 hover:underline" @click="router.push('/deployments')">Все →</button>
        </div>
        <div v-if="!recentDeploys.length" class="rounded-xl border border-white/5 px-4 py-6 text-center text-sm text-slate-600">
          Нет деплоев. <button class="text-sky-400 hover:underline" @click="router.push('/projects')">Задеплоить первое →</button>
        </div>
        <div v-else class="overflow-hidden rounded-xl border border-white/5">
          <div v-for="(d, i) in recentDeploys" :key="d.id"
            :class="['flex cursor-pointer items-center justify-between px-4 py-3 transition hover:bg-white/5', i > 0 && 'border-t border-white/5']"
            @click="router.push(`/applications/${d.app_id}`)"
          >
            <p class="min-w-0 truncate text-sm text-slate-300">{{ d.git_url || d.id.slice(0, 8) }}</p>
            <div class="flex shrink-0 items-center gap-3">
              <span :class="['text-xs', deployStatus(d.status)]">{{ d.status }}</span>
              <span class="text-xs text-slate-600">{{ formatDate(d.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

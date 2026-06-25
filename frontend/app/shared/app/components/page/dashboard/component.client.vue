<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from '#imports';
import FeatureNotice from '~/shared/app/components/ui/feature-notice/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';

interface Project { id: string; name: string; app_count: number }
interface App { id: string; name: string; status: string; url: string; project_name: string }
interface Deployment { id: string; status: string; git_url: string; created_at: string; app_id: string }

const { get } = usePlatformApi();
const router = useRouter();

const { data: projects } = useAsyncData<Project[]>('dash-projects', () => get('/api/v1/hosting/projects'));
const { data: apps } = useAsyncData<App[]>('dash-apps', () => get('/api/v1/hosting/apps'));
const { data: deployments } = useAsyncData<Deployment[]>('dash-deploys', () => get('/api/v1/hosting/deployments'));

const stats = computed(() => [
  { label: 'Проектов', value: projects.value?.length ?? 0, to: '/projects' },
  { label: 'Приложений', value: apps.value?.length ?? 0, to: '/applications' },
  { label: 'Запущено', value: apps.value?.filter((a) => a.status === 'running').length ?? 0, to: '/applications' },
  { label: 'Деплоев', value: deployments.value?.length ?? 0, to: '/deployments' },
]);

const runningApps = computed(() => apps.value?.filter((a) => a.status === 'running').slice(0, 5) ?? []);
const recentDeploys = computed(() => deployments.value?.slice(0, 5) ?? []);

function deployStatus(s: string) {
  return s === 'running' ? 'text-emerald-600' : s === 'building' ? 'text-amber-600' : s === 'failed' ? 'text-rose-600' : 'text-slate-500';
}

function formatDate(iso: string) {
  return iso ? new Date(iso).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '';
}
</script>

<template>
  <div class="grid gap-6">
    <FeatureNotice
      tone="info"
      message="Создайте проект → укажите Git URL → задеплойте frontend и backend. Адрес приложения появится в карточке после успешной сборки."
    />

    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <button
        v-for="stat in stats"
        :key="stat.label"
        class="rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-sky-200 hover:shadow"
        type="button"
        @click="router.push(stat.to)"
      >
        <p class="text-2xl font-bold text-slate-900">{{ stat.value }}</p>
        <p class="mt-1 text-sm text-slate-500">{{ stat.label }}</p>
      </button>
    </div>

    <div>
      <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">С чего начать</p>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          class="rounded-xl border border-sky-200 bg-sky-50 p-4 text-left transition hover:bg-sky-100"
          type="button"
          @click="router.push('/projects')"
        >
          <span class="text-sm font-medium text-sky-800">Новый проект и деплой</span>
          <span class="mt-1 block text-xs text-slate-500">Git-репозиторий, Dockerfile, публикация на поддомен</span>
        </button>
        <button
          class="rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-sky-200"
          type="button"
          @click="router.push('/domains')"
        >
          <span class="text-sm font-medium text-slate-800">Домены платформы</span>
          <span class="mt-1 block text-xs text-slate-500">Кабинет, API и шаблон для приложений</span>
        </button>
      </div>
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <div>
        <div class="mb-3 flex items-center justify-between">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">Запущенные приложения</p>
          <button class="text-xs text-sky-600 hover:underline" type="button" @click="router.push('/applications')">Все →</button>
        </div>
        <div v-if="!runningApps.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-center text-sm text-slate-500">
          Нет запущенных приложений
        </div>
        <div v-else class="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <div
            v-for="(app, i) in runningApps"
            :key="app.id"
            :class="['flex cursor-pointer items-center justify-between px-4 py-3 transition hover:bg-slate-50', i > 0 && 'border-t border-slate-100']"
            @click="router.push(`/applications/${app.id}`)"
          >
            <div class="min-w-0">
              <p class="truncate text-sm font-medium text-slate-800">{{ app.name }}</p>
              <p class="truncate text-xs text-slate-500">{{ app.project_name }}</p>
            </div>
            <div class="flex shrink-0 items-center gap-2">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              <a v-if="app.url" :href="app.url" target="_blank" class="text-xs text-sky-600 hover:underline" @click.stop>↗</a>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div class="mb-3 flex items-center justify-between">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">Последние деплои</p>
          <button class="text-xs text-sky-600 hover:underline" type="button" @click="router.push('/deployments')">Все →</button>
        </div>
        <div v-if="!recentDeploys.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-center text-sm text-slate-500">
          Нет деплоев.
          <button class="text-sky-600 hover:underline" type="button" @click="router.push('/projects')">Задеплоить первое →</button>
        </div>
        <div v-else class="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <div
            v-for="(d, i) in recentDeploys"
            :key="d.id"
            :class="['flex cursor-pointer items-center justify-between px-4 py-3 transition hover:bg-slate-50', i > 0 && 'border-t border-slate-100']"
            @click="router.push(`/applications/${d.app_id}`)"
          >
            <p class="min-w-0 truncate text-sm text-slate-700">{{ d.git_url || d.id.slice(0, 8) }}</p>
            <div class="flex shrink-0 items-center gap-3">
              <span :class="['text-xs font-medium', deployStatus(d.status)]">{{ d.status }}</span>
              <span class="text-xs text-slate-400">{{ formatDate(d.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

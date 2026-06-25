<script setup lang="ts">
import { useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import FeatureNotice from '~/shared/app/components/ui/feature-notice/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';

interface Deployment {
  id: string;
  app_id: string;
  status: string;
  git_url: string;
  created_at: string;
  logs: string;
}

interface AppItem {
  id: string;
  name: string;
}

const { get } = usePlatformApi();
const router = useRouter();

const { data: deployments, pending, refresh } = useAsyncData<Deployment[]>('logs-deployments', () => get('/api/v1/hosting/deployments'));
const { data: apps } = useAsyncData<AppItem[]>('logs-apps', () => get('/api/v1/hosting/apps'));

function appName(appId: string) {
  return apps.value?.find((app) => app.id === appId)?.name ?? appId.slice(0, 8);
}

function statusTone(s: string) {
  return s === 'running' ? 'success' : s === 'building' ? 'warning' : s === 'failed' ? 'danger' : 'muted';
}

function formatDate(iso: string) {
  return iso ? new Date(iso).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—';
}
</script>

<template>
  <div class="grid gap-4">
    <FeatureNotice
      tone="info"
      title="Журнал событий"
      message="Показываем события деплоев из hosting-service: статус сборки, Git-источник, время и последние строки логов."
    />

    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 class="text-xl font-semibold text-slate-900">Активность деплоев</h2>
        <p class="text-sm text-slate-500">Реальные события из hosting-service</p>
      </div>
      <button class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50" type="button" @click="refresh">
        Обновить
      </button>
    </div>

    <div v-if="pending" class="text-sm text-slate-500">Загружаем...</div>

    <div v-else-if="!deployments?.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
      Событий пока нет. Запустите деплой в разделе
      <button class="text-sky-600 hover:underline" type="button" @click="router.push('/projects')">Проекты</button>.
    </div>

    <AppCard v-for="d in deployments" :key="d.id">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="min-w-0">
          <p class="text-sm font-medium text-slate-900">{{ appName(d.app_id) }}</p>
          <p class="truncate text-xs text-slate-500">{{ d.git_url || d.id }}</p>
          <p class="mt-1 text-xs text-slate-400">{{ formatDate(d.created_at) }}</p>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <AppBadge :label="d.status" :tone="statusTone(d.status)" />
          <button class="text-xs text-sky-600 hover:underline" type="button" @click="router.push(`/applications/${d.app_id}`)">
            Приложение
          </button>
        </div>
      </div>
      <pre v-if="d.logs" class="mt-3 max-h-32 overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-2 text-xs text-slate-600">{{ d.logs.slice(-500) }}</pre>
    </AppCard>
  </div>
</template>

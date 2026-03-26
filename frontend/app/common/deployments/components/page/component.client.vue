<script setup lang="ts">
import { useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';

interface Deployment { id: string; app_id: string; status: string; git_url: string; created_at: string; logs: string }

const { get } = usePlatformApi();
const router = useRouter();
const { data: deployments } = useAsyncData<Deployment[]>('hosting-deployments', () => get('/api/v1/hosting/deployments'));

function statusTone(s: string) {
  return s === 'running' ? 'success' : s === 'building' ? 'warning' : s === 'failed' ? 'danger' : 'muted';
}

function formatDate(iso: string) {
  return iso ? new Date(iso).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—';
}
</script>

<template>
  <div class="grid gap-4">
    <div>
      <h2 class="text-base font-semibold text-slate-100">История деплоев</h2>
      <p class="text-sm text-slate-400">Все сборки и публикации приложений</p>
    </div>

    <div v-if="!deployments?.length" class="rounded-xl border border-white/5 bg-slate-900/40 px-5 py-8 text-center text-sm text-slate-400">
      Нет деплоев. Задеплойте первое приложение через раздел Проекты.
    </div>

    <AppCard v-for="d in deployments" :key="d.id">
      <div class="flex items-center justify-between gap-4">
        <div class="min-w-0">
          <p class="truncate text-sm font-medium text-slate-100">{{ d.git_url || d.id }}</p>
          <p class="text-xs text-slate-400">{{ formatDate(d.created_at) }}</p>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <AppBadge :label="d.status" :tone="statusTone(d.status)" />
          <button class="text-xs text-sky-400 hover:underline" @click="router.push(`/applications/${d.app_id}`)">Приложение</button>
        </div>
      </div>
      <pre v-if="d.logs" class="mt-2 max-h-24 overflow-auto rounded-lg bg-slate-950 p-2 text-xs text-slate-400">{{ d.logs.slice(-400) }}</pre>
    </AppCard>
  </div>
</template>

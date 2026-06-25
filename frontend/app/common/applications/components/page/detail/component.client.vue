<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import { usePermissions } from '~/shared/app/hooks/use-permissions';

interface AppDetail { id: string; name: string; project_name: string; project_id: string; runtime: string; status: string; url: string; hostname?: string; git_url: string; slug: string; container_name: string }

const props = defineProps<{ appId: string }>();
const { get, post, del } = usePlatformApi();
const { can } = usePermissions();
const router = useRouter();

const { data: app, refresh: refreshApp } = useAsyncData<AppDetail>(`app-${props.appId}`, () => get(`/api/v1/hosting/apps/${props.appId}`));
const logs = ref('');
const loadingLogs = ref(false);
const actionState = ref('');
const actionError = ref('');

let pollTimer: ReturnType<typeof setInterval> | null = null;

function statusTone(s: string) {
  return s === 'running' ? 'success' : s === 'building' ? 'warning' : s === 'error' ? 'danger' : 'muted';
}

async function loadLogs() {
  loadingLogs.value = true;
  try {
    const res: any = await get(`/api/v1/hosting/apps/${props.appId}/logs`);
    logs.value = res?.logs ?? '';
  } finally {
    loadingLogs.value = false;
  }
}

async function doAction(action: string) {
  actionState.value = action;
  actionError.value = '';
  try {
    await post(`/api/v1/hosting/apps/${props.appId}/${action}`, {});
    await refreshApp();
    if (action === 'start' || action === 'stop') await loadLogs();
  } catch (error: any) {
    actionError.value = error?.data?.detail ?? 'Действие не выполнено.';
  } finally {
    actionState.value = '';
  }
}

async function deleteApp() {
  if (!can('projects:write')) return;
  if (!confirm(`Удалить приложение ${app.value?.name}? Контейнер и nginx-конфиг будут удалены.`)) return;
  await del(`/api/v1/hosting/apps/${props.appId}`);
  router.push(`/projects/${app.value?.project_id}`);
}

async function redeploy() {
  await doAction('redeploy');
  pollTimer && clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    await refreshApp();
    if (app.value?.status !== 'building') { clearInterval(pollTimer!); pollTimer = null; await loadLogs(); }
  }, 3000);
}

async function issueSsl() {
  await doAction('ssl');
}

onMounted(() => {
  loadLogs();
  if (app.value?.status === 'building') {
    pollTimer = setInterval(async () => {
      await refreshApp();
      if (app.value?.status !== 'building') { clearInterval(pollTimer!); pollTimer = null; await loadLogs(); }
    }, 3000);
  }
});
onUnmounted(() => { if (pollTimer) clearInterval(pollTimer); });
</script>

<template>
  <div class="grid gap-4">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <button class="mb-1 text-xs text-slate-500 hover:text-sky-600" @click="router.push(`/projects/${app?.project_id}`)">← {{ app?.project_name }}</button>
        <h2 class="text-xl font-semibold text-slate-900">{{ app?.name }}</h2>
        <p class="text-sm text-slate-500">{{ app?.git_url || app?.slug }}</p>
      </div>
      <div class="flex items-center gap-2">
        <AppBadge v-if="app?.status" :label="app.status" :tone="statusTone(app.status)" />
        <a v-if="app?.url" :href="app.url" target="_blank" class="text-xs text-sky-600 hover:underline">{{ app.url }} ↗</a>
      </div>
    </div>

    <AppCard>
      <div class="flex flex-wrap gap-2">
        <AppButton v-if="can('deploys:write') && app?.status === 'running'" :disabled="!!actionState" label="Остановить" tone="secondary" @click="doAction('stop')" />
        <AppButton v-if="can('deploys:write') && (app?.status === 'stopped' || app?.status === 'error')" :disabled="!!actionState" label="Запустить" @click="doAction('start')" />
        <AppButton v-if="can('deploys:write') && app?.git_url" :disabled="!!actionState || app?.status === 'building'" :label="app?.status === 'building' ? 'Деплоится...' : 'Передеплоить'" @click="redeploy" />
        <AppButton v-if="can('domains:write') && app?.status === 'running'" :disabled="!!actionState" :label="actionState === 'ssl' ? 'Выпускаем SSL...' : 'Выпустить SSL'" tone="secondary" @click="issueSsl" />
        <AppButton :disabled="!!actionState" label="Обновить логи" tone="secondary" @click="loadLogs" />
        <AppButton v-if="can('projects:write')" :disabled="!!actionState" label="Удалить" tone="secondary" @click="deleteApp" />
      </div>
      <p v-if="actionError" class="mt-3 text-sm text-rose-600">{{ actionError }}</p>
    </AppCard>

    <AppCard>
      <div class="grid gap-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-slate-500">Логи контейнера</span>
          <span v-if="loadingLogs" class="text-xs text-slate-400">загрузка...</span>
        </div>
        <pre class="h-72 overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-3 text-xs leading-5 text-slate-700 scrollbar-thin">{{ logs || 'Нет логов' }}</pre>
      </div>
    </AppCard>

    <AppCard>
      <div class="grid gap-2 text-sm">
        <div class="flex justify-between"><span class="text-slate-500">Runtime</span><span class="text-slate-800">{{ app?.runtime }}</span></div>
        <div class="flex justify-between"><span class="text-slate-500">Контейнер</span><span class="font-mono text-xs text-slate-700">{{ app?.container_name || '—' }}</span></div>
        <div class="flex justify-between"><span class="text-slate-500">Домен</span><span class="font-mono text-xs text-sky-700">{{ app?.hostname || app?.url?.replace(/^https?:\/\//, '') || '—' }}</span></div>
      </div>
    </AppCard>
  </div>
</template>

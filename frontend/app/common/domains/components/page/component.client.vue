<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import FeatureNotice from '~/shared/app/components/ui/feature-notice/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import type { SettingsFormEntity } from '../../../settings/entities/settings-form.entity';

interface AppHost {
  id: string;
  name: string;
  project_name: string;
  status: string;
  url?: string;
  hostname?: string;
}

const { get } = usePlatformApi();

const { data: settings, pending: settingsPending } = useAsyncData<SettingsFormEntity>(
  'domains-settings',
  () => get('/api/v1/platform/settings/form'),
);
const { data: apps, pending: appsPending } = useAsyncData<AppHost[]>(
  'domains-apps',
  () => get('/api/v1/hosting/apps'),
);

const platformDomains = computed(() => [
  {
    label: 'Кабинет',
    hostname: settings.value?.dashboard_host,
    description: 'Основной интерфейс управления платформой.',
    path: '/',
  },
  {
    label: 'API',
    hostname: settings.value?.api_host,
    description: 'Прямой адрес gateway-service для интеграций.',
    path: '/api/v1/routes',
  },
  {
    label: 'Приложения',
    hostname: settings.value?.default_app_domain ? `*.${settings.value.default_app_domain}` : '',
    description: 'Шаблон поддоменов для опубликованных приложений.',
    path: '',
  },
]);

const appDomains = computed(() => (apps.value ?? []).filter((app) => app.hostname || app.url));
const pending = computed(() => settingsPending.value || appsPending.value);

function domainUrl(hostname?: string, path = '') {
  if (!hostname || hostname.startsWith('*.')) return '';
  return `https://${hostname}${path}`;
}

function statusTone(status: string) {
  return status === 'running' ? 'success' : status === 'building' ? 'warning' : status === 'error' ? 'danger' : 'muted';
}
</script>

<template>
  <div class="grid gap-5">
    <FeatureNotice
      tone="info"
      message="Здесь показаны домены, которые сейчас использует платформа. Для production их значения берутся из настроек gateway и окружения setup.sh."
    />

    <div v-if="pending" class="text-sm text-slate-500">Загружаем домены...</div>

    <template v-else>
      <div>
        <h2 class="text-xl font-semibold text-slate-900">Домены платформы</h2>
        <p class="text-sm text-slate-500">Кабинет, API и шаблон адресов для приложений.</p>
      </div>

      <div class="grid gap-3 lg:grid-cols-3">
        <AppCard v-for="domain in platformDomains" :key="domain.label">
          <div class="grid gap-3">
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-medium text-slate-900">{{ domain.label }}</p>
                <p class="mt-1 text-sm text-slate-500">{{ domain.description }}</p>
              </div>
              <AppBadge label="platform" tone="default" />
            </div>
            <p class="rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 font-mono text-sm text-slate-700">
              {{ domain.hostname || 'не настроен' }}
            </p>
            <a
              v-if="domainUrl(domain.hostname, domain.path)"
              :href="domainUrl(domain.hostname, domain.path)"
              target="_blank"
              rel="noreferrer"
              class="text-sm font-medium text-sky-600 hover:underline"
            >
              Открыть →
            </a>
          </div>
        </AppCard>
      </div>

      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold text-slate-900">Домены приложений</h2>
          <p class="text-sm text-slate-500">Создаются после деплоя и ведут на контейнер приложения.</p>
        </div>
        <NuxtLink to="/projects" class="text-sm font-medium text-sky-600 hover:underline">
          Задеплоить приложение →
        </NuxtLink>
      </div>

      <div v-if="!appDomains.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
        Пока нет приложений с доменами. Создайте проект и запустите деплой.
      </div>

      <div v-else class="grid gap-3">
        <AppCard v-for="app in appDomains" :key="app.id">
          <div class="flex flex-wrap items-center justify-between gap-4">
            <div class="min-w-0">
              <p class="truncate font-medium text-slate-900">{{ app.name }}</p>
              <p class="truncate text-sm text-slate-500">{{ app.project_name }}</p>
              <p class="mt-1 truncate font-mono text-xs text-slate-500">{{ app.hostname || app.url }}</p>
            </div>
            <div class="flex shrink-0 items-center gap-2">
              <AppBadge :label="app.status" :tone="statusTone(app.status)" />
              <a
                v-if="app.url"
                :href="app.url"
                target="_blank"
                rel="noreferrer"
                class="text-sm font-medium text-sky-600 hover:underline"
              >
                Открыть →
              </a>
            </div>
          </div>
        </AppCard>
      </div>
    </template>
  </div>
</template>

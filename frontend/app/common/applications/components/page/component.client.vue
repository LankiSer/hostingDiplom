<script setup lang="ts">
import { useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';

interface App { id: string; name: string; project_name: string; runtime: string; status: string; url: string; slug: string }

const { get } = usePlatformApi();
const router = useRouter();
const { data: apps } = useAsyncData<App[]>('hosting-apps-all', () => get('/api/v1/hosting/apps'));

function statusTone(s: string) {
  return s === 'running' ? 'success' : s === 'building' ? 'warning' : s === 'error' ? 'danger' : 'muted';
}
</script>

<template>
  <div class="grid gap-4">
    <div>
      <h2 class="text-xl font-semibold text-slate-900">Приложения</h2>
      <p class="text-sm text-slate-500">Все задеплоенные сервисы на платформе</p>
    </div>

    <div v-if="!apps?.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
      Нет приложений. Создайте проект и задеплойте первое.
    </div>

    <AppCard v-for="a in apps" :key="a.id" class="cursor-pointer hover:border-sky-200" @click="router.push(`/applications/${a.id}`)">
      <div class="flex items-center justify-between gap-4">
        <div class="min-w-0">
          <p class="truncate font-medium text-slate-900">{{ a.name }}</p>
          <p class="truncate text-xs text-slate-500">{{ a.project_name }} · {{ a.slug }}</p>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <AppBadge :label="a.runtime" tone="muted" />
          <AppBadge :label="a.status" :tone="statusTone(a.status)" />
          <a v-if="a.url" :href="a.url" target="_blank" class="text-xs text-sky-600 hover:underline" @click.stop>↗</a>
        </div>
      </div>
    </AppCard>
  </div>
</template>

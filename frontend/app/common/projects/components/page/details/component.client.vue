<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import AppInput from '~/shared/app/components/ui/input/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import type { ProjectDetailsPageProps } from './interface';

interface App { id: string; name: string; slug: string; runtime: string; status: string; url: string; git_url: string }

const props = defineProps<ProjectDetailsPageProps>();
const { get, post } = usePlatformApi();
const router = useRouter();

const { data: project } = useAsyncData(`project-${props.projectId}`, () => get(`/api/v1/hosting/projects/${props.projectId}`));
const { data: apps, refresh } = useAsyncData<App[]>(`apps-${props.projectId}`, () => get(`/api/v1/hosting/apps?project_id=${props.projectId}`));

const showForm = ref(false);
const form = reactive({ name: '', git_url: '', runtime: 'node' });
const state = reactive({ saving: false, error: '' });

function statusTone(s: string) {
  return s === 'running' ? 'success' : s === 'building' ? 'warning' : s === 'error' ? 'danger' : 'muted';
}

async function createApp() {
  if (!form.name.trim()) return;
  state.saving = true;
  state.error = '';
  try {
    const app: any = await post('/api/v1/hosting/apps', { project_id: props.projectId, name: form.name, git_url: form.git_url, runtime: form.runtime });
    form.name = '';
    form.git_url = '';
    showForm.value = false;
    await refresh();
    if (app?.id) router.push(`/applications/${app.id}`);
  } catch (e: any) {
    state.error = e?.data?.detail ?? 'Ошибка создания приложения';
  } finally {
    state.saving = false;
  }
}
</script>

<template>
  <div class="grid gap-4">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-xs text-slate-500">Проект</p>
        <h2 class="text-base font-semibold text-slate-100">{{ (project as any)?.name ?? projectId }}</h2>
        <p class="text-sm text-slate-400">{{ (project as any)?.description }}</p>
      </div>
      <AppButton label="Новое приложение" @click="showForm = !showForm" />
    </div>

    <AppCard v-if="showForm">
      <div class="grid gap-3">
        <h3 class="text-sm font-medium text-slate-200">Деплой приложения</h3>
        <AppInput v-model="form.name" label="Имя" placeholder="my-api" />
        <AppInput v-model="form.git_url" label="Git URL" placeholder="https://github.com/user/repo" />
        <label class="grid gap-2">
          <span class="text-sm text-slate-300">Runtime</span>
          <select v-model="form.runtime" class="rounded-xl border border-white/10 bg-slate-950/70 px-3.5 py-2.5 text-sm text-slate-100 outline-none">
            <option value="node">Node.js</option>
            <option value="python">Python</option>
          </select>
        </label>
        <div class="flex items-center gap-2">
          <AppButton :disabled="state.saving" :label="state.saving ? 'Деплоим...' : 'Задеплоить'" @click="createApp" />
          <AppButton label="Отмена" tone="secondary" @click="showForm = false" />
        </div>
        <p v-if="state.error" class="text-sm text-rose-300">{{ state.error }}</p>
      </div>
    </AppCard>

    <div v-if="!apps?.length" class="rounded-xl border border-white/5 bg-slate-900/40 px-5 py-8 text-center text-sm text-slate-400">
      Нет приложений. Задеплойте первое.
    </div>

    <AppCard v-for="a in apps" :key="a.id" class="cursor-pointer hover:border-sky-400/20" @click="router.push(`/applications/${a.id}`)">
      <div class="flex items-center justify-between gap-4">
        <div class="min-w-0">
          <p class="truncate font-medium text-slate-100">{{ a.name }}</p>
          <p class="truncate text-xs text-slate-400">{{ a.git_url || a.slug }}</p>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <AppBadge :label="a.runtime" tone="muted" />
          <AppBadge :label="a.status" :tone="statusTone(a.status)" />
          <a v-if="a.url" :href="a.url" target="_blank" class="text-xs text-sky-400 hover:underline" @click.stop>Открыть ↗</a>
        </div>
      </div>
    </AppCard>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue';
import { useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import AppCheckbox from '~/shared/app/components/ui/checkbox/component.vue';
import AppInput from '~/shared/app/components/ui/input/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import type { ProjectDetailsPageProps } from './interface';

interface App {
  id: string;
  name: string;
  slug: string;
  runtime: string;
  app_type: string;
  status: string;
  url: string;
  git_url: string;
  root_path: string;
}

interface Project {
  id: string;
  name: string;
  description: string;
  git_url?: string;
  git_branch?: string;
  deploy_config?: {
    frontend?: { enabled?: boolean; name?: string; root_path?: string; runtime?: string };
    backend?: { enabled?: boolean; name?: string; root_path?: string; runtime?: string };
  };
}

const props = defineProps<ProjectDetailsPageProps>();
const { get, post, put } = usePlatformApi();
const router = useRouter();

const { data: project, refresh: refreshProject } = useAsyncData<Project>(
  `project-${props.projectId}`,
  () => get(`/api/v1/hosting/projects/${props.projectId}`),
);
const { data: apps, refresh: refreshApps } = useAsyncData<App[]>(
  `apps-${props.projectId}`,
  () => get(`/api/v1/hosting/apps?project_id=${props.projectId}`),
);

const showSingleForm = ref(false);
const singleForm = reactive({ name: '', git_url: '', runtime: 'node', root_path: '', branch: 'main' });

const deployForm = reactive({
  git_url: '',
  git_branch: 'main',
  frontend_enabled: true,
  frontend_name: 'web',
  frontend_root_path: 'frontend',
  frontend_runtime: 'node',
  backend_enabled: true,
  backend_name: 'api',
  backend_root_path: 'backend',
  backend_runtime: 'python',
});

const state = reactive({ saving: false, deploying: false, error: '', success: '' });

function applyProjectConfig(p: Project | null) {
  if (!p) return;
  deployForm.git_url = p.git_url || '';
  deployForm.git_branch = p.git_branch || 'main';
  const cfg = p.deploy_config || {};
  deployForm.frontend_enabled = cfg.frontend?.enabled ?? true;
  deployForm.frontend_name = cfg.frontend?.name || 'web';
  deployForm.frontend_root_path = cfg.frontend?.root_path || 'frontend';
  deployForm.frontend_runtime = cfg.frontend?.runtime || 'node';
  deployForm.backend_enabled = cfg.backend?.enabled ?? true;
  deployForm.backend_name = cfg.backend?.name || 'api';
  deployForm.backend_root_path = cfg.backend?.root_path || 'backend';
  deployForm.backend_runtime = cfg.backend?.runtime || 'python';
}

watch(project, (p) => applyProjectConfig(p), { immediate: true });

function statusTone(s: string) {
  return s === 'running' ? 'success' : s === 'building' ? 'warning' : s === 'error' ? 'danger' : 'muted';
}

function appTypeLabel(t: string) {
  return t === 'frontend' ? 'Frontend' : t === 'backend' ? 'Backend' : 'App';
}

async function persistDeployConfig() {
  await put(`/api/v1/hosting/projects/${props.projectId}/deploy-config`, {
    git_url: deployForm.git_url,
    git_branch: deployForm.git_branch,
    frontend: {
      enabled: deployForm.frontend_enabled,
      name: deployForm.frontend_name,
      root_path: deployForm.frontend_root_path,
      runtime: deployForm.frontend_runtime,
    },
    backend: {
      enabled: deployForm.backend_enabled,
      name: deployForm.backend_name,
      root_path: deployForm.backend_root_path,
      runtime: deployForm.backend_runtime,
    },
  });
  await refreshProject();
}

async function saveDeployConfig() {
  state.saving = true;
  state.error = '';
  state.success = '';
  try {
    await persistDeployConfig();
    state.success = 'Настройки деплоя сохранены';
  } catch (e: any) {
    state.error = e?.data?.detail ?? 'Ошибка сохранения настроек';
  } finally {
    state.saving = false;
  }
}

async function deployStack() {
  state.deploying = true;
  state.error = '';
  state.success = '';
  try {
    await persistDeployConfig();
    await post(`/api/v1/hosting/projects/${props.projectId}/deploy-stack`, {});
    state.success = 'Деплой запущен. Frontend и backend собираются из Git.';
    await refreshApps();
  } catch (e: any) {
    state.error = e?.data?.detail ?? 'Ошибка запуска деплоя';
  } finally {
    state.deploying = false;
  }
}

async function createSingleApp() {
  if (!singleForm.name.trim()) return;
  state.saving = true;
  state.error = '';
  try {
    const app: any = await post('/api/v1/hosting/apps', {
      project_id: props.projectId,
      name: singleForm.name,
      git_url: singleForm.git_url,
      runtime: singleForm.runtime,
      root_path: singleForm.root_path,
      branch: singleForm.branch,
    });
    Object.assign(singleForm, { name: '', git_url: '', runtime: 'node', root_path: '', branch: 'main' });
    showSingleForm.value = false;
    await refreshApps();
    if (app?.id) router.push(`/applications/${app.id}`);
  } catch (e: any) {
    state.error = e?.data?.detail ?? 'Ошибка создания приложения';
  } finally {
    state.saving = false;
  }
}
</script>

<template>
  <div class="grid gap-5">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <p class="text-xs font-medium uppercase tracking-wide text-slate-400">Проект</p>
        <h2 class="text-xl font-semibold text-slate-900">{{ project?.name ?? projectId }}</h2>
        <p class="text-sm text-slate-500">{{ project?.description || 'Настройте Git и задеплойте frontend и backend' }}</p>
      </div>
      <div class="flex gap-2">
        <AppButton label="Одно приложение" tone="secondary" @click="showSingleForm = !showSingleForm" />
        <AppButton :disabled="state.deploying" :label="state.deploying ? 'Деплоим...' : 'Задеплоить стек'" @click="deployStack" />
      </div>
    </div>

    <AppCard>
      <div class="grid gap-5">
        <div>
          <h3 class="text-base font-semibold text-slate-900">Деплой из Git</h3>
          <p class="mt-1 text-sm text-slate-500">Один репозиторий, отдельные правила для frontend и backend.</p>
        </div>

        <div class="grid gap-4 md:grid-cols-2">
          <AppInput v-model="deployForm.git_url" label="Git URL репозитория" placeholder="https://github.com/user/monorepo" />
          <AppInput v-model="deployForm.git_branch" label="Ветка" placeholder="main" />
        </div>

        <div class="grid gap-4 lg:grid-cols-2">
          <div class="rounded-xl border border-sky-100 bg-sky-50/50 p-4">
            <AppCheckbox v-model="deployForm.frontend_enabled">
              <span class="font-medium text-slate-800">Frontend</span>
            </AppCheckbox>
            <div class="mt-3 grid gap-3">
              <AppInput v-model="deployForm.frontend_name" label="Имя сервиса" placeholder="web" />
              <AppInput v-model="deployForm.frontend_root_path" label="Папка в репозитории" placeholder="frontend" />
              <label class="grid gap-1.5">
                <span class="text-sm font-medium text-slate-700">Runtime</span>
                <select v-model="deployForm.frontend_runtime" class="app-select">
                  <option value="node">Node.js</option>
                  <option value="python">Python</option>
                </select>
              </label>
            </div>
          </div>

          <div class="rounded-xl border border-amber-100 bg-amber-50/50 p-4">
            <AppCheckbox v-model="deployForm.backend_enabled">
              <span class="font-medium text-slate-800">Backend</span>
            </AppCheckbox>
            <div class="mt-3 grid gap-3">
              <AppInput v-model="deployForm.backend_name" label="Имя сервиса" placeholder="api" />
              <AppInput v-model="deployForm.backend_root_path" label="Папка в репозитории" placeholder="backend" />
              <label class="grid gap-1.5">
                <span class="text-sm font-medium text-slate-700">Runtime</span>
                <select v-model="deployForm.backend_runtime" class="app-select">
                  <option value="python">Python</option>
                  <option value="node">Node.js</option>
                </select>
              </label>
            </div>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <AppButton :disabled="state.saving" :label="state.saving ? 'Сохраняем...' : 'Сохранить правила'" tone="secondary" @click="saveDeployConfig" />
        </div>

        <p v-if="state.success" class="text-sm text-emerald-600">{{ state.success }}</p>
        <p v-if="state.error" class="text-sm text-rose-600">{{ state.error }}</p>
      </div>
    </AppCard>

    <AppCard v-if="showSingleForm">
      <div class="grid gap-3">
        <h3 class="text-sm font-semibold text-slate-900">Отдельное приложение</h3>
        <div class="grid gap-3 md:grid-cols-2">
          <AppInput v-model="singleForm.name" label="Имя" placeholder="worker" />
          <AppInput v-model="singleForm.git_url" label="Git URL" placeholder="https://github.com/user/repo" />
          <AppInput v-model="singleForm.root_path" label="Папка (опционально)" placeholder="services/worker" />
          <AppInput v-model="singleForm.branch" label="Ветка" placeholder="main" />
        </div>
        <label class="grid gap-1.5">
          <span class="text-sm font-medium text-slate-700">Runtime</span>
          <select v-model="singleForm.runtime" class="app-select">
            <option value="node">Node.js</option>
            <option value="python">Python</option>
          </select>
        </label>
        <div class="flex gap-2">
          <AppButton :disabled="state.saving" label="Задеплоить" @click="createSingleApp" />
          <AppButton label="Отмена" tone="secondary" @click="showSingleForm = false" />
        </div>
      </div>
    </AppCard>

    <div>
      <h3 class="mb-3 text-sm font-semibold text-slate-900">Приложения проекта</h3>
      <div v-if="!apps?.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
        Пока нет приложений. Сохраните правила и нажмите «Задеплоить стек».
      </div>

      <div v-else class="grid gap-3">
        <AppCard v-for="a in apps" :key="a.id" class="cursor-pointer hover:border-sky-200" @click="router.push(`/applications/${a.id}`)">
          <div class="flex items-center justify-between gap-4">
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <p class="truncate font-medium text-slate-900">{{ a.name }}</p>
                <AppBadge :label="appTypeLabel(a.app_type)" tone="default" />
              </div>
              <p class="truncate text-xs text-slate-500">
                {{ a.root_path ? `${a.root_path} · ` : '' }}{{ a.git_url || a.slug }}
              </p>
            </div>
            <div class="flex shrink-0 items-center gap-2">
              <AppBadge :label="a.runtime" tone="muted" />
              <AppBadge :label="a.status" :tone="statusTone(a.status)" />
              <a v-if="a.url" :href="a.url" target="_blank" class="text-xs text-sky-600 hover:underline" @click.stop>Открыть ↗</a>
            </div>
          </div>
        </AppCard>
      </div>
    </div>
  </div>
</template>

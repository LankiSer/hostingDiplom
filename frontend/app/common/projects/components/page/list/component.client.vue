<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import AppInput from '~/shared/app/components/ui/input/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';

interface Project { id: string; name: string; slug: string; description: string; app_count: number; created_at: string }

const { get, post, del } = usePlatformApi();
const router = useRouter();
const { data: projects, refresh } = useAsyncData<Project[]>('hosting-projects', () => get('/api/v1/hosting/projects'));
const showForm = ref(false);
const form = reactive({ name: '', description: '' });
const state = reactive({ saving: false, error: '' });

async function createProject() {
  if (!form.name.trim()) return;
  state.saving = true;
  state.error = '';
  try {
    await post('/api/v1/hosting/projects', { name: form.name, description: form.description });
    form.name = '';
    form.description = '';
    showForm.value = false;
    await refresh();
  } catch (e: any) {
    state.error = e?.data?.detail ?? 'Ошибка создания проекта';
  } finally {
    state.saving = false;
  }
}

async function removeProject(id: string) {
  if (!confirm('Удалить проект и все его приложения?')) return;
  await del(`/api/v1/hosting/projects/${id}`);
  await refresh();
}
</script>

<template>
  <div class="grid gap-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-slate-900">Проекты</h2>
        <p class="text-sm text-slate-500">Создайте проект и настройте деплой frontend/backend из Git</p>
      </div>
      <AppButton label="Новый проект" @click="showForm = !showForm" />
    </div>

    <AppCard v-if="showForm">
      <div class="grid gap-3">
        <h3 class="text-sm font-semibold text-slate-900">Создать проект</h3>
        <AppInput v-model="form.name" label="Название" placeholder="my-platform" />
        <AppInput v-model="form.description" label="Описание (опционально)" placeholder="Frontend + backend из одного репозитория" />
        <div class="flex items-center gap-2">
          <AppButton :disabled="state.saving" :label="state.saving ? 'Создаём...' : 'Создать'" @click="createProject" />
          <AppButton label="Отмена" tone="secondary" @click="showForm = false" />
        </div>
        <p v-if="state.error" class="text-sm text-rose-600">{{ state.error }}</p>
      </div>
    </AppCard>

    <div v-if="!projects?.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
      Нет проектов. Создайте первый.
    </div>

    <AppCard v-for="p in projects" :key="p.id" class="cursor-pointer hover:border-sky-200" @click="router.push(`/projects/${p.id}`)">
      <div class="flex items-center justify-between gap-4">
        <div class="min-w-0">
          <p class="truncate font-medium text-slate-900">{{ p.name }}</p>
          <p class="truncate text-xs text-slate-500">{{ p.description || p.slug }}</p>
        </div>
        <div class="flex shrink-0 items-center gap-2">
          <AppBadge :label="`${p.app_count ?? 0} приложений`" tone="muted" />
          <button class="p-1 text-xs text-slate-400 hover:text-rose-500" @click.stop="removeProject(p.id)">✕</button>
        </div>
      </div>
    </AppCard>
  </div>
</template>

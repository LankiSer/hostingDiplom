<script setup lang="ts">
import { reactive, watch } from 'vue';
import AppButton from '../../../../shared/app/components/ui/button/component.vue';
import AppCard from '../../../../shared/app/components/ui/card/component.vue';
import AppInput from '../../../../shared/app/components/ui/input/component.vue';
import AppSection from '../../../../shared/app/components/content/section/component.vue';
import { usePlatformApi } from '../../../../shared/app/hooks/use-platform-api';
import { useSession } from '../../../../shared/app/hooks/use-session';
import type { SettingsFormEntity } from '../../entities/settings-form.entity';

const { get, put } = usePlatformApi();
const { save, session } = useSession();
const { data, pending, refresh } = useAsyncData<SettingsFormEntity>('settings-form', () => get('/api/v1/platform/settings/form'));
const form = reactive<SettingsFormEntity>({ api_host: '', company_name: '', contact_email: '', contact_name: '', dashboard_host: '', default_app_domain: '', support_email: '', workspace_name: '' });
const state = reactive({ error: '', saved: false, saving: false });

watch(data, (value) => value && Object.assign(form, value), { immediate: true });

async function handleSave() {
  state.error = '';
  state.saved = false;
  state.saving = true;
  try {
    const updated = await put<SettingsFormEntity>('/api/v1/platform/settings/form', form);
    Object.assign(form, updated);
    session.value && save({ ...session.value, companyName: updated.company_name, displayName: updated.contact_name, email: updated.contact_email });
    state.saved = true;
    refresh();
  } catch {
    state.error = 'Не удалось сохранить настройки. Проверь локальный API и повтори попытку.';
  } finally {
    state.saving = false;
  }
}
</script>

<template>
  <AppSection title="Настройки" description="Редактируй компанию, контакты и локальные домены. Изменения сразу отражаются в кабинете.">
    <div v-if="pending" class="text-sm text-slate-400">Загружаем настройки...</div>
    <div v-else class="app-page-columns">
      <AppCard><div class="grid gap-4"><AppInput v-model="form.workspace_name" label="Название кабинета" /><AppInput v-model="form.company_name" label="Компания" /><AppInput v-model="form.contact_name" label="Контактное лицо" /><AppInput v-model="form.contact_email" label="Email кабинета" /></div></AppCard>
      <AppCard><div class="grid gap-4"><AppInput v-model="form.dashboard_host" label="Домен кабинета" /><AppInput v-model="form.api_host" label="Домен API" /><AppInput v-model="form.default_app_domain" label="Базовый домен приложений" /><AppInput v-model="form.support_email" label="Email поддержки" /></div></AppCard>
    </div>
    <div class="flex flex-wrap items-center gap-3">
      <AppButton :disabled="state.saving" :label="state.saving ? 'Сохраняем...' : 'Сохранить настройки'" @click="handleSave" />
      <span v-if="state.saved" class="text-sm text-emerald-300">Настройки сохранены.</span>
      <span v-if="state.error" class="text-sm text-rose-300">{{ state.error }}</span>
    </div>
  </AppSection>
</template>

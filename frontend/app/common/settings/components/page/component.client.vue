<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from '#imports';
import AppButton from '../../../../shared/app/components/ui/button/component.vue';
import AppCard from '../../../../shared/app/components/ui/card/component.vue';
import AppInput from '../../../../shared/app/components/ui/input/component.vue';
import FeatureNotice from '../../../../shared/app/components/ui/feature-notice/component.vue';
import { usePlatformApi } from '../../../../shared/app/hooks/use-platform-api';
import { usePermissions } from '../../../../shared/app/hooks/use-permissions';
import { useSession } from '../../../../shared/app/hooks/use-session';
import type { SettingsFormEntity } from '../../entities/settings-form.entity';

type SettingsTab = 'profile' | 'workspace' | 'legal' | 'domains';

const TABS: { id: SettingsTab; label: string; hint: string }[] = [
  { id: 'profile', label: 'Профиль', hint: 'Имя и email' },
  { id: 'workspace', label: 'Пространство', hint: 'Название в меню' },
  { id: 'legal', label: 'Юрлицо', hint: 'Для счетов' },
  { id: 'domains', label: 'Домены', hint: 'Адреса платформы' },
];

interface AppHost {
  id: string;
  name: string;
  status: string;
  url?: string;
  hostname?: string;
}

const route = useRoute();
const router = useRouter();
const { get, put } = usePlatformApi();
const { can } = usePermissions();
const { save, session } = useSession();

function tabFromQuery(value: unknown): SettingsTab {
  const raw = Array.isArray(value) ? value[0] : value;
  return TABS.some((item) => item.id === raw) ? (raw as SettingsTab) : 'profile';
}

const tab = ref<SettingsTab>(tabFromQuery(route.query.tab));
const { data, pending, refresh } = useAsyncData<SettingsFormEntity>('settings-form', () => get('/api/v1/platform/settings/form'));
const { data: apps } = useAsyncData<AppHost[]>('settings-apps', () => get('/api/v1/hosting/apps'));

const form = reactive<SettingsFormEntity>({
  api_host: '',
  company_name: '',
  contact_email: '',
  contact_name: '',
  dashboard_host: '',
  default_app_domain: '',
  support_email: '',
  workspace_name: '',
});
const state = reactive({ error: '', saved: false, saving: false });

watch(data, (value) => value && Object.assign(form, value), { immediate: true });

watch(tab, (value) => {
  router.replace({ query: value === 'profile' ? {} : { tab: value } });
});

onMounted(() => {
  tab.value = tabFromQuery(route.query.tab);
});

const deployedHosts = computed(() =>
  (apps.value ?? []).filter((app) => app.hostname || app.url),
);

async function handleSave() {
  if (!can('settings:write')) return;
  state.error = '';
  state.saved = false;
  state.saving = true;
  try {
    const updated = await put<SettingsFormEntity>('/api/v1/platform/settings/form', form);
    Object.assign(form, updated);
    session.value && save({
      ...session.value,
      companyName: updated.workspace_name,
      displayName: updated.contact_name,
      email: updated.contact_email,
    });
    state.saved = true;
    refresh();
  } catch {
    state.error = 'Не удалось сохранить настройки.';
  } finally {
    state.saving = false;
  }
}
</script>

<template>
  <div class="grid gap-5">
    <FeatureNotice
      tone="info"
      message="Здесь профиль, домены платформы и юридические данные. Деплой приложений — в разделах «Проекты» и «Приложения»."
    />

    <div class="grid gap-4 lg:grid-cols-[220px_1fr]">
      <div class="flex flex-row gap-2 overflow-x-auto lg:flex-col lg:overflow-visible">
        <button
          v-for="item in TABS"
          :key="item.id"
          type="button"
          class="min-w-[160px] rounded-xl border px-3 py-3 text-left transition lg:min-w-0"
          :class="tab === item.id ? 'border-sky-200 bg-sky-50 shadow-sm' : 'border-slate-200 bg-white hover:border-slate-300'"
          @click="tab = item.id"
        >
          <span class="flex items-center gap-2">
            <span class="block text-sm font-medium" :class="tab === item.id ? 'text-sky-800' : 'text-slate-800'">{{ item.label }}</span>
          </span>
          <span class="mt-0.5 block text-xs text-slate-500">{{ item.hint }}</span>
        </button>
      </div>

      <AppCard>
        <div v-if="pending" class="text-sm text-slate-500">Загружаем настройки...</div>
        <div v-else class="grid gap-4">
          <template v-if="tab === 'profile'">
            <AppInput v-model="form.contact_name" label="Имя в кабинете" placeholder="Александр Смирнов" />
            <AppInput v-model="form.contact_email" label="Email для уведомлений" placeholder="owner@company.ru" type="email" />
            <AppInput v-model="form.support_email" label="Email поддержки" placeholder="support@company.ru" type="email" />
          </template>

          <template v-else-if="tab === 'workspace'">
            <AppInput v-model="form.workspace_name" label="Название рабочего пространства" placeholder="North API team" />
            <p class="rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-500">Отображается в боковом меню и шапке кабинета.</p>
          </template>

          <template v-else-if="tab === 'legal'">
            <AppInput v-model="form.company_name" label="Юридическое название" placeholder="ООО Компания" />
            <p class="rounded-lg border border-amber-100 bg-amber-50 px-3 py-2 text-sm text-amber-900">Подставляется в счета в разделе «Биллинг».</p>
            <div class="grid gap-3 border-t border-slate-100 pt-4">
              <p class="text-sm font-medium text-slate-800">Реквизиты оператора платформы</p>
              <p class="text-sm text-slate-500">Эти данные отображаются в футере кабинета и на странице «Юридическая информация».</p>
              <LegalEntityInfo />
              <LegalFooterLinks />
            </div>
          </template>

          <template v-else>
            <FeatureNotice
              tone="warning"
              title="DNS и SSL настраиваются на сервере"
              message="Поля ниже отражают текущую конфигурацию платформы. Чтобы сменить домен в production, обновите переменные окружения и выполните setup.sh на сервере."
            />
            <AppInput v-model="form.dashboard_host" label="Домен кабинета" placeholder="app.kostricyn.ru" />
            <AppInput v-model="form.api_host" label="Домен API" placeholder="api.kostricyn.ru" />
            <AppInput v-model="form.default_app_domain" label="Базовый домен приложений" placeholder="apps.kostricyn.ru" />
            <div v-if="deployedHosts.length" class="grid gap-2 border-t border-slate-100 pt-4">
              <p class="text-sm font-medium text-slate-800">Задеплоенные приложения</p>
              <div
                v-for="app in deployedHosts"
                :key="app.id"
                class="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-100 bg-slate-50 px-3 py-2 text-sm"
              >
                <span class="font-medium text-slate-800">{{ app.name }}</span>
                <a
                  v-if="app.url"
                  :href="app.url"
                  target="_blank"
                  rel="noreferrer"
                  class="truncate text-sky-600 hover:underline"
                >
                  {{ app.hostname || app.url }}
                </a>
                <span v-else class="text-slate-500">{{ app.hostname || 'адрес назначается' }}</span>
              </div>
            </div>
            <p v-else class="text-sm text-slate-500">После первого деплоя здесь появятся адреса вида slug.apps.ваш-домен.ru</p>
          </template>

          <div class="flex flex-wrap items-center gap-3 border-t border-slate-100 pt-4">
            <AppButton v-if="can('settings:write')" :disabled="state.saving" :label="state.saving ? 'Сохраняем...' : 'Сохранить'" @click="handleSave" />
            <span v-if="state.saved" class="text-sm text-emerald-600">Сохранено</span>
            <span v-if="state.error" class="text-sm text-rose-600">{{ state.error }}</span>
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

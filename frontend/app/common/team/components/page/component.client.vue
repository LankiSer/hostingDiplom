<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import AppInput from '~/shared/app/components/ui/input/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import { useSession } from '~/shared/app/hooks/use-session';

interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  role_label: string;
  projects: number;
  status: string;
  initials: string;
}

interface TeamRole {
  id: string;
  name: string;
  description: string;
  members: number;
  permissions: string[];
}

interface TeamOverview {
  members: TeamMember[];
  roles: TeamRole[];
}

const PERMISSION_LABELS: Record<string, string> = {
  billing: 'Биллинг',
  deploys: 'Деплои',
  documents: 'Документы',
  logs: 'Логи',
  projects: 'Проекты',
  settings: 'Настройки',
  team: 'Команда',
};

const route = useRoute();
const router = useRouter();
const { get } = usePlatformApi();
const { session } = useSession();

const tab = ref<'members' | 'roles'>(route.query.tab === 'roles' ? 'roles' : 'members');
const showInvite = ref(false);
const invite = reactive({ email: '', role: 'ops' });
const inviteState = reactive({ sending: false, sent: false });

const { data, pending } = useAsyncData<TeamOverview>('team-overview', () => get('/api/v1/platform/team/overview'));

watch(tab, (value) => {
  router.replace({ query: value === 'roles' ? { tab: 'roles' } : {} });
});

function statusTone(status: string) {
  return status === 'active' ? 'success' : status === 'invited' ? 'warning' : 'muted';
}

function statusLabel(status: string) {
  return status === 'active' ? 'Активен' : status === 'invited' ? 'Приглашён' : status;
}

const activeMembers = computed(() => data.value?.members ?? []);
const roles = computed(() => data.value?.roles ?? []);

async function sendInvite() {
  if (!invite.email.trim()) return;
  inviteState.sending = true;
  inviteState.sent = false;
  await new Promise((r) => setTimeout(r, 600));
  inviteState.sending = false;
  inviteState.sent = true;
  invite.email = '';
  showInvite.value = false;
}
</script>

<template>
  <div class="grid gap-5">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <p class="text-sm text-slate-500">Управляйте доступом коллег к проектам, деплоям и биллингу.</p>
      </div>
      <AppButton v-if="tab === 'members'" label="Пригласить" @click="showInvite = !showInvite" />
    </div>

    <div class="inline-flex rounded-xl border border-slate-200 bg-slate-50 p-1">
      <button
        type="button"
        class="rounded-lg px-4 py-2 text-sm font-medium transition"
        :class="tab === 'members' ? 'bg-white text-sky-700 shadow-sm' : 'text-slate-500'"
        @click="tab = 'members'"
      >
        Участники
      </button>
      <button
        type="button"
        class="rounded-lg px-4 py-2 text-sm font-medium transition"
        :class="tab === 'roles' ? 'bg-white text-sky-700 shadow-sm' : 'text-slate-500'"
        @click="tab = 'roles'"
      >
        Роли и доступ
      </button>
    </div>

    <AppCard v-if="showInvite && tab === 'members'">
      <div class="grid gap-3 md:grid-cols-[1fr_auto_auto] md:items-end">
        <AppInput v-model="invite.email" label="Email коллеги" placeholder="colleague@company.ru" type="email" />
        <label class="grid gap-1.5">
          <span class="text-sm font-medium text-slate-700">Роль</span>
          <select v-model="invite.role" class="app-select">
            <option value="ops">DevOps</option>
            <option value="finance">Финансы</option>
            <option value="owner">Владелец</option>
          </select>
        </label>
        <AppButton :disabled="inviteState.sending" :label="inviteState.sending ? 'Отправляем...' : 'Отправить'" @click="sendInvite" />
      </div>
    </AppCard>

    <p v-if="inviteState.sent" class="text-sm text-emerald-600">Приглашение отправлено (демо).</p>

    <div v-if="pending" class="text-sm text-slate-500">Загружаем команду...</div>

    <div v-else-if="tab === 'members'" class="grid gap-3">
      <AppCard v-for="member in activeMembers" :key="member.id">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex min-w-0 items-center gap-3">
            <span
              class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-semibold"
              :class="member.email === session?.email ? 'bg-sky-100 text-sky-800 ring-2 ring-sky-200' : 'bg-slate-100 text-slate-700'"
            >
              {{ member.initials }}
            </span>
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <p class="truncate font-medium text-slate-900">{{ member.name }}</p>
                <span v-if="member.email === session?.email" class="text-[10px] font-semibold uppercase tracking-wide text-sky-600">Вы</span>
              </div>
              <p class="truncate text-sm text-slate-500">{{ member.email }}</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <AppBadge :label="member.role_label" tone="default" />
            <AppBadge :label="`${member.projects} проектов`" tone="muted" />
            <AppBadge :label="statusLabel(member.status)" :tone="statusTone(member.status)" />
          </div>
        </div>
      </AppCard>
    </div>

    <div v-else class="grid gap-4 lg:grid-cols-3">
      <AppCard v-for="role in roles" :key="role.id" class="flex flex-col">
        <div class="grid flex-1 gap-3">
          <div class="flex items-start justify-between gap-2">
            <h3 class="text-lg font-semibold text-slate-900">{{ role.name }}</h3>
            <AppBadge :label="`${role.members} чел.`" tone="muted" />
          </div>
          <p class="text-sm leading-6 text-slate-500">{{ role.description }}</p>
          <div class="flex flex-wrap gap-1.5">
            <span
              v-for="perm in role.permissions"
              :key="perm"
              class="rounded-md bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600"
            >
              {{ PERMISSION_LABELS[perm] ?? perm }}
            </span>
          </div>
        </div>
      </AppCard>
    </div>
  </div>
</template>

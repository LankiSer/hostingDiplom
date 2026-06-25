<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from '#imports';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import AppInput from '~/shared/app/components/ui/input/component.vue';
import FeatureNotice from '~/shared/app/components/ui/feature-notice/component.vue';
import { usePermissions } from '~/shared/app/hooks/use-permissions';
import { useSession } from '~/shared/app/hooks/use-session';
import type { AuditLog, TeamMember } from '../../entities/team.entity';
import { useTeam } from '../../hooks/use-team';
import { useCallWebSocket } from '../../hooks/use-call-websocket';
import { useLivekitRoom } from '../../hooks/use-livekit-room';
import TeamCallWhiteboard from '../team-call-whiteboard.client.vue';
import LivekitTile from '../livekit-tile.vue';

type TeamTab = 'members' | 'roles' | 'audit' | 'call';

const PERMISSION_LABELS: Record<string, string> = {
  'audit:read': 'Аудит',
  'billing:read': 'Биллинг: просмотр',
  'billing:write': 'Биллинг: изменения',
  'calls:read': 'Созвоны',
  'calls:write': 'Созвоны: управление',
  'deploys:read': 'Деплои: просмотр',
  'deploys:write': 'Деплои: запуск',
  'documents:read': 'Документы',
  'domains:read': 'Домены: просмотр',
  'domains:write': 'Домены/SSL',
  'logs:read': 'Логи',
  'projects:read': 'Проекты: просмотр',
  'projects:write': 'Проекты: изменения',
  'settings:read': 'Настройки',
  'settings:write': 'Настройки: изменения',
  'team:read': 'Команда',
  'team:write': 'Команда: изменения',
};

const route = useRoute();
const router = useRouter();
const teamApi = useTeam();
const { session } = useSession();
const { can } = usePermissions();

const tab = ref<TeamTab>(['members', 'roles', 'audit', 'call'].includes(String(route.query.tab)) ? route.query.tab as TeamTab : 'members');
const showInvite = ref(false);
const invite = reactive({ email: '', role: 'ops' });
const inviteState = reactive({ sending: false, sent: false, error: '' });
const memberAction = ref<string | null>(null);
const roleFilter = ref('all');
const statusFilter = ref('all');
const callTitle = ref('Разбор проекта');
const chatBody = ref('');
const callError = ref('');

const { data, pending, refresh } = useAsyncData('team-overview', () => teamApi.getOverview());
const { data: auditData, refresh: refreshAudit } = useAsyncData('team-audit', () => teamApi.getAudit(), { lazy: true });
const { data: activeCall, refresh: refreshCall } = useAsyncData('team-call', () => teamApi.getActiveCall(), { lazy: true });

const callWs = useCallWebSocket();
const livekit = useLivekitRoom();
const realtimeSessionId = ref<string | null>(null);
const realtimeConnecting = ref(false);
const pinnedIdentity = ref<string | null>(null);

// Computed speaker layout helpers
const screenTile = computed(() => livekit.tiles.value.find((t) => t.isScreenShare) ?? null);
const effectivePinned = computed(() => {
  if (pinnedIdentity.value && livekit.tiles.value.some((t) => t.identity === pinnedIdentity.value)) return pinnedIdentity.value;
  if (screenTile.value) return screenTile.value.identity;
  return null;
});
const pinnedTile = computed(() => livekit.tiles.value.find((t) => t.identity === effectivePinned.value) ?? null);
const thumbnailTiles = computed(() => livekit.tiles.value.filter((t) => t.identity !== effectivePinned.value));

function pinTile(identity: string) {
  pinnedIdentity.value = pinnedIdentity.value === identity ? null : identity;
}

async function connectRealtime() {
  if (!activeCall.value?.id || !session.value?.email) return;
  if (realtimeConnecting.value) return;
  if (realtimeSessionId.value === activeCall.value.id && callWs.isConnected.value) return;

  realtimeConnecting.value = true;
  try {
    // Pre-populate chat history from REST before opening WS
    const historicMessages = (activeCall.value?.messages ?? [])
      .filter((m: any) => m.kind === 'chat')
      .map((m: any) => ({
        id: String(m.id),
        body: String(m.body),
        author_name: String(m.author_name || 'Участник'),
        created_at: String(m.created_at || ''),
      }));
    callWs.initMessages(historicMessages);

    callWs.connect(
      activeCall.value.id,
      session.value.email,
      session.value.displayName || session.value.email,
    );
    realtimeSessionId.value = activeCall.value.id;

    try {
      const connection = await teamApi.getLivekitConnection(activeCall.value.id);
      await livekit.connect(connection);
    } catch (error: any) {
      callError.value = error?.data?.detail || livekit.errorMessage.value || 'LiveKit недоступен — signaling и локальная камера всё ещё работают.';
    }
  } finally {
    realtimeConnecting.value = false;
  }
}

watch(tab, async (value) => {
  router.replace({ query: value === 'members' ? {} : { tab: value } });
  if (value === 'audit') refreshAudit();
  if (value === 'call') {
    await refreshCall();
    if (activeCall.value?.id) await connectRealtime();
  }
});

watch(activeCall, async (call, prev) => {
  if (tab.value !== 'call') return;
  if (call?.id && call.id !== prev?.id) {
    await connectRealtime();
  }
  if (!call?.id) {
    realtimeSessionId.value = null;
  }
});

const allMembers = computed(() => data.value?.members ?? []);
const activeMembers = computed(() => allMembers.value.filter((member) => {
  const roleMatches = roleFilter.value === 'all' || member.role === roleFilter.value;
  const statusMatches = statusFilter.value === 'all' || member.status === statusFilter.value;
  return roleMatches && statusMatches;
}));
const roles = computed(() => data.value?.roles ?? []);
const auditItems = computed(() => auditData.value?.items ?? []);
const chatMessages = computed(() => callWs.chatMessages.value);

const mediaError = ref('');
const localVideoRef = ref<HTMLVideoElement | null>(null);
const screenVideoRef = ref<HTMLVideoElement | null>(null);
const cameraStream = ref<MediaStream | null>(null);
const screenStream = ref<MediaStream | null>(null);
const micEnabled = ref(true);
const cameraEnabled = ref(true);

// When LiveKit is connected, use its state. Otherwise fall back to local raw streams.
const hasCamera = computed(() => livekit.isConnected.value ? livekit.isCameraEnabled.value : Boolean(cameraStream.value));
const hasScreen = computed(() => livekit.isConnected.value ? livekit.isScreenEnabled.value : Boolean(screenStream.value));
const isMicActive = computed(() => livekit.isConnected.value ? livekit.isMicEnabled.value : micEnabled.value);

const stats = computed(() => {
  const members = allMembers.value;
  const invited = members.filter((member) => member.status === 'invited').length;
  const active = members.filter((member) => member.status === 'active').length;
  const risky = members.filter((member) => member.role === 'finance' || member.status === 'invited').length;
  return [
    { label: 'Активные', value: active, tone: 'success' },
    { label: 'Приглашения', value: invited, tone: 'warning' },
    { label: 'Событий 24ч', value: auditData.value?.stats?.last_24h ?? 0, tone: 'default' },
    { label: 'Риск-сигналы', value: risky, tone: risky ? 'warning' : 'muted' },
  ];
});

function statusTone(status: string) {
  return status === 'active' ? 'success' : status === 'invited' ? 'warning' : status === 'disabled' ? 'danger' : 'muted';
}

function statusLabel(status: string) {
  return status === 'active' ? 'Активен' : status === 'invited' ? 'Приглашён' : status === 'disabled' ? 'Отключён' : status === 'cancelled' ? 'Отменён' : status;
}

function formatDate(value?: string) {
  return value ? new Date(value).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—';
}

function actionLabel(action: string) {
  return action.replace('team.', 'Команда: ').replace('hosting.', 'Хостинг: ').replace('billing.', 'Биллинг: ').replace('settings.', 'Настройки: ');
}

function auditTone(item: AuditLog) {
  return item.action.includes('delete') || item.action.includes('cancel') ? 'danger' : item.action.includes('invite') ? 'warning' : 'default';
}

async function syncTeam() {
  await refresh();
  await refreshAudit();
}

async function sendInvite() {
  if (!invite.email.trim() || !can('team:write')) return;
  inviteState.sending = true;
  inviteState.sent = false;
  inviteState.error = '';
  try {
    data.value = await teamApi.inviteMember(invite.email, invite.role);
    inviteState.sent = true;
    invite.email = '';
    showInvite.value = false;
    await syncTeam();
  } catch (error: any) {
    inviteState.error = error?.data?.detail ?? 'Не удалось отправить приглашение.';
  } finally {
    inviteState.sending = false;
  }
}

async function updateMember(member: TeamMember, payload: Partial<Pick<TeamMember, 'role' | 'status'>>) {
  if (member.role === 'owner' || !can('team:write')) return;
  memberAction.value = member.id;
  inviteState.error = '';
  try {
    if (payload.role) data.value = await teamApi.updateRole(member.id, payload.role);
    if (payload.status === 'active') data.value = await teamApi.activateMember(member.id);
    if (payload.status === 'disabled') data.value = await teamApi.disableMember(member.id);
    await syncTeam();
  } catch (error: any) {
    inviteState.error = error?.data?.detail ?? 'Не удалось обновить участника.';
  } finally {
    memberAction.value = null;
  }
}

async function deleteMember(member: TeamMember) {
  if (member.role === 'owner' || !can('team:write')) return;
  memberAction.value = member.id;
  inviteState.error = '';
  try {
    data.value = await teamApi.deleteMember(member.id);
    await syncTeam();
  } catch (error: any) {
    inviteState.error = error?.data?.detail ?? 'Не удалось удалить участника.';
  } finally {
    memberAction.value = null;
  }
}

async function resendInvite(member: TeamMember) {
  memberAction.value = member.id;
  try {
    data.value = await teamApi.resendInvite(member.id);
    await syncTeam();
  } finally {
    memberAction.value = null;
  }
}

async function cancelInvite(member: TeamMember) {
  memberAction.value = member.id;
  try {
    data.value = await teamApi.cancelInvite(member.id);
    await syncTeam();
  } finally {
    memberAction.value = null;
  }
}

async function copyInvite(member: TeamMember) {
  if (!member.invite_url) return;
  await navigator.clipboard.writeText(`${window.location.origin}${member.invite_url}`);
  inviteState.sent = true;
}

async function createCall() {
  if (!can('calls:write')) {
    callError.value = 'Нет прав на создание созвона.';
    return;
  }
  callError.value = '';
  try {
    // Refresh first — if another user already started a call, join it instead
    await refreshCall();
    if (activeCall.value?.id) {
      await connectRealtime();
      return;
    }
    // No active call yet — create one (backend is idempotent)
    await refreshCall();  // use refresh so asyncData stays in sync
    activeCall.value = await teamApi.createCall(callTitle.value);
    await refreshCall();
    await connectRealtime();
    await refreshAudit();
  } catch (error: any) {
    callError.value = error?.data?.detail ?? 'Не удалось создать созвон.';
  }
}

function stopTrackGroup(stream: MediaStream | null) {
  stream?.getTracks().forEach((track) => track.stop());
}

function syncTrackStates() {
  cameraStream.value?.getAudioTracks().forEach((track) => {
    track.enabled = micEnabled.value;
  });
  cameraStream.value?.getVideoTracks().forEach((track) => {
    track.enabled = cameraEnabled.value;
  });
}

async function startCameraMedia() {
  mediaError.value = '';
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      video: { width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 30 } }
    });
    stopTrackGroup(cameraStream.value);
    cameraStream.value = stream;
    syncTrackStates();
    if (localVideoRef.value) localVideoRef.value.srcObject = stream;
  } catch (error: any) {
    mediaError.value = error?.message ?? 'Не удалось получить доступ к камере/микрофону.';
  }
}

function stopCameraMedia() {
  stopTrackGroup(cameraStream.value);
  cameraStream.value = null;
  if (localVideoRef.value) localVideoRef.value.srcObject = null;
}

async function startScreenMedia() {
  mediaError.value = '';
  try {
    const stream = await navigator.mediaDevices.getDisplayMedia({ 
      audio: true, 
      video: { width: { ideal: 1920 }, height: { ideal: 1080 } }
    });
    stopTrackGroup(screenStream.value);
    screenStream.value = stream;
    if (screenVideoRef.value) screenVideoRef.value.srcObject = stream;

    const [track] = stream.getVideoTracks();
    if (track) {
      track.onended = () => {
        stopScreenMedia();
      };
    }
  } catch (error: any) {
    mediaError.value = error?.message ?? 'Не удалось запустить демонстрацию экрана.';
  }
}

function stopScreenMedia() {
  stopTrackGroup(screenStream.value);
  screenStream.value = null;
  if (screenVideoRef.value) screenVideoRef.value.srcObject = null;
}

async function toggleCameraUnified() {
  if (livekit.isConnected.value) {
    const wasOn = livekit.isCameraEnabled.value;
    await livekit.toggleCamera();
    callWs.sendMediaStatus({ camera: !wasOn });
  } else {
    if (cameraStream.value) {
      stopCameraMedia();
      callWs.sendMediaStatus({ camera: false });
    } else {
      await startCameraMedia();
      callWs.sendMediaStatus({ camera: Boolean(cameraStream.value) });
    }
  }
}

async function toggleMicUnified() {
  if (livekit.isConnected.value) {
    const wasOn = livekit.isMicEnabled.value;
    await livekit.toggleMic();
    callWs.sendMediaStatus({ mic: !wasOn });
  } else {
    micEnabled.value = !micEnabled.value;
    syncTrackStates();
    callWs.sendMediaStatus({ mic: micEnabled.value });
  }
}

async function toggleScreenUnified() {
  if (livekit.isConnected.value) {
    await livekit.toggleScreenShare();
  } else {
    if (screenStream.value) stopScreenMedia();
    else await startScreenMedia();
  }
}

function sendChat() {
  if (!chatBody.value.trim()) return;
  const body = chatBody.value.trim();
  chatBody.value = '';
  callWs.sendChatMessage(body);
}

async function endCall() {
  if (!activeCall.value?.id) return;
  try {
    await teamApi.endCall(activeCall.value.id);
    callWs.disconnect();
    await livekit.disconnect();
    activeCall.value = null;
    await refreshCall();
  } catch (error: any) {
    console.error('Failed to end call:', error);
  }
}

watch(localVideoRef, (el) => {
  if (el && cameraStream.value) el.srcObject = cameraStream.value;
});


let pollTimer: ReturnType<typeof setInterval> | null = null;

function startCallPoller() {
  stopCallPoller();
  pollTimer = setInterval(async () => {
    if (tab.value !== 'call') return;
    await refreshCall();
    // Auto-connect if a call appeared and we're not yet connected
    if (activeCall.value?.id && !callWs.isConnected.value && !realtimeConnecting.value) {
      await connectRealtime();
    }
  }, 8000);
}

function stopCallPoller() {
  if (pollTimer !== null) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

watch(tab, (value) => {
  if (value !== 'call') {
    stopCameraMedia();
    stopScreenMedia();
    callWs.disconnect();
    void livekit.disconnect();
    realtimeSessionId.value = null;
    stopCallPoller();
  } else {
    startCallPoller();
  }
});

onMounted(async () => {
  if (tab.value === 'call') {
    if (activeCall.value?.id) await connectRealtime();
    startCallPoller();
  }
});

onBeforeUnmount(() => {
  stopCameraMedia();
  stopScreenMedia();
  callWs.disconnect();
  void livekit.disconnect();
  stopCallPoller();
});

</script>

<template>
  <div class="grid gap-4">
    <!-- Stats grid - only shown when not in call tab -->
    <div v-if="tab !== 'call'" class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <AppCard v-for="item in stats" :key="item.label">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-semibold text-slate-900">{{ item.value }}</p>
            <p class="text-sm text-slate-500">{{ item.label }}</p>
          </div>
          <AppBadge :label="item.tone === 'warning' ? '!' : ''" :tone="item.tone as any" />
        </div>
      </AppCard>
    </div>

    <FeatureNotice
      v-if="tab !== 'call'"
      tone="info"
      message="Команда управляет ролями и правами."
    />

    <div v-if="tab !== 'call'" class="flex flex-wrap items-end justify-between gap-3">
      <p class="text-sm text-slate-500">Управляйте доступом коллег.</p>
      <AppButton v-if="tab === 'members' && can('team:write')" :label="showInvite ? 'Скрыть' : 'Пригласить'" @click="showInvite = !showInvite" />
    </div>

    <!-- Tabs navigation -->
    <div class="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-slate-50 p-1">
      <button
        v-for="item in [
          { id: 'members', label: 'Участники' },
          { id: 'roles', label: 'Роли' },
          { id: 'audit', label: 'Аудит' },
          { id: 'call', label: 'Созвон' },
        ]"
        :key="item.id"
        type="button"
        class="rounded-lg px-4 py-2 text-sm font-medium transition"
        :class="tab === item.id ? 'bg-white text-sky-700 shadow-sm' : 'text-slate-500'"
        @click="tab = item.id as TeamTab"
      >
        {{ item.label }}
      </button>
    </div>

    <!-- Members tab -->
    <div v-if="tab === 'members'" class="flex flex-wrap gap-2">
      <select v-model="roleFilter" class="app-select">
        <option value="all">Все роли</option>
        <option value="owner">Владелец</option>
        <option value="ops">DevOps</option>
        <option value="finance">Финансы</option>
        <option value="viewer">Наблюдатель</option>
      </select>
      <select v-model="statusFilter" class="app-select">
        <option value="all">Все статусы</option>
        <option value="active">Активные</option>
        <option value="invited">Приг��ашённые</option>
        <option value="disabled">Отключённые</option>
      </select>
    </div>

    <AppCard v-if="showInvite && tab === 'members'">
      <div class="grid gap-3 sm:grid-cols-[1fr_auto_auto] sm:items-end">
        <AppInput v-model="invite.email" label="Email" placeholder="colleague@company.ru" type="email" />
        <label class="grid gap-1.5">
          <span class="text-sm font-medium text-slate-700">Роль</span>
          <select v-model="invite.role" class="app-select">
            <option value="ops">DevOps</option>
            <option value="finance">Финансы</option>
            <option value="viewer">Наблюдатель</option>
          </select>
        </label>
        <AppButton :disabled="inviteState.sending" :label="inviteState.sending ? '...' : 'Отправить'" @click="sendInvite" />
      </div>
    </AppCard>

    <p v-if="inviteState.sent" class="text-sm text-emerald-600">Готово.</p>
    <p v-if="inviteState.error" class="text-sm text-rose-600">{{ inviteState.error }}</p>
    <div v-if="pending" class="text-sm text-slate-500">Загружаем...</div>

    <div v-else-if="tab === 'members'" class="grid gap-3">
      <AppCard v-for="member in activeMembers" :key="member.id">
        <div class="flex items-center gap-3">
          <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold" :class="member.email === session?.email ? 'bg-sky-100 text-sky-800' : 'bg-slate-100 text-slate-700'">{{ member.initials }}</span>
          <div class="min-w-0 flex-1">
            <p class="truncate font-medium text-slate-900">{{ member.name }}<span v-if="member.email === session?.email" class="ml-2 text-xs text-sky-600">Вы</span></p>
            <p class="truncate text-sm text-slate-500">{{ member.email }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <select v-if="member.role !== 'owner' && can('team:write')" :value="member.role" class="app-select min-w-[100px]" :disabled="memberAction === member.id" @change="updateMember(member, { role: ($event.target as HTMLSelectElement).value as TeamMember['role'] })">
              <option value="ops">DevOps</option>
              <option value="finance">Финансы</option>
              <option value="viewer">Наблюдатель</option>
            </select>
            <AppBadge v-else :label="member.role_label" tone="default" />
            <AppBadge :label="statusLabel(member.status)" :tone="statusTone(member.status)" />
            <AppButton v-if="member.status === 'invited' && can('team:write')" label="Актив" tone="secondary" @click="updateMember(member, { status: 'active' })" />
            <AppButton v-if="member.status === 'invited' && can('team:write')" label="Копировать" tone="secondary" @click="copyInvite(member)" />
            <AppButton v-if="member.status === 'invited' && can('team:write')" label="Повтор" tone="secondary" @click="resendInvite(member)" />
            <AppButton v-if="member.status === 'invited' && can('team:write')" label="Отменить" tone="secondary" @click="cancelInvite(member)" />
            <AppButton v-if="member.role !== 'owner' && member.status === 'active' && can('team:write')" label="Откл" tone="secondary" @click="updateMember(member, { status: 'disabled' })" />
            <AppButton v-if="member.role !== 'owner' && can('team:write')" label="Удалить" tone="secondary" @click="deleteMember(member)" />
          </div>
        </div>
      </AppCard>
    </div>

    <!-- Roles tab -->
    <div v-else-if="tab === 'roles'" class="grid gap-4 md:grid-cols-2">
      <AppCard v-for="role in roles" :key="role.id" class="flex flex-col">
        <div class="flex-1">
          <div class="mb-2 flex items-center justify-between">
            <h3 class="font-semibold text-slate-900">{{ role.name }}</h3>
            <AppBadge :label="`${role.members} чел.`" tone="muted" />
          </div>
          <p class="text-sm text-slate-500">{{ role.description }}</p>
        </div>
      </AppCard>
    </div>

    <!-- Audit tab -->
    <div v-else-if="tab === 'audit'" class="grid gap-3">
      <div class="flex items-center justify-between">
        <p class="text-sm text-slate-500">Журнал действий.</p>
        <AppButton label="Обновить" tone="secondary" @click="refreshAudit" />
      </div>
      <AppCard v-for="item in auditItems" :key="item.id">
        <div class="flex items-start justify-between gap-3">
          <div>
            <div class="mb-1 flex items-center gap-2">
              <AppBadge :label="actionLabel(item.action)" :tone="auditTone(item)" />
              <span class="text-xs text-slate-400">{{ formatDate(item.created_at) }}</span>
            </div>
            <p class="text-sm text-slate-900">{{ item.message || item.action }}</p>
            <p class="text-xs text-slate-500">{{ item.actor_email || 'system' }}</p>
          </div>
          <code class="max-w-[200px] truncate rounded bg-slate-50 px-2 py-1 text-xs text-slate-500">{{ item.resource_id }}</code>
        </div>
      </AppCard>
      <div v-if="!auditItems.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">Пока нет событий.</div>
    </div>

    <!-- Call tab -->
    <div v-else class="grid gap-4">

      <!-- ── Idle state ──────────────────────────────────────── -->
      <div v-if="!activeCall" class="overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-50 to-white">
        <div class="px-6 py-10 text-center">
          <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-100 text-sky-600">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-7 w-7">
              <path d="M15 10l4.553-2.07A1 1 0 0 1 21 8.845v6.31a1 1 0 0 1-1.447.915L15 14" />
              <rect x="2" y="7" width="13" height="10" rx="2" />
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-slate-900">Командный созвон</h3>
          <p class="mt-1 text-sm text-slate-500">Видео, голос, экран и совместная доска в одном месте.</p>
          <div class="mt-6 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
            <input
              v-if="can('calls:write')"
              v-model="callTitle"
              class="w-full max-w-xs rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-100 sm:w-64"
              placeholder="Название созвона"
            >
            <AppButton :label="can('calls:write') ? 'Начать созвон' : 'Подключиться к звонку'" @click="createCall" />
          </div>
          <p class="mt-2 text-xs text-slate-400">Проверяем наличие активного звонка каждые 8 с.</p>
          <p v-if="callError" class="mt-3 text-sm text-rose-600">{{ callError }}</p>
        </div>
      </div>

      <!-- ── Active call ─────────────────────────────────────── -->
      <template v-else>

        <!-- Header bar -->
        <div class="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4">
                <path d="M15 10l4.553-2.07A1 1 0 0 1 21 8.845v6.31a1 1 0 0 1-1.447.915L15 14" />
                <rect x="2" y="7" width="13" height="10" rx="2" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-slate-900 leading-tight">{{ activeCall.title }}</p>
              <p class="text-xs text-slate-400">{{ formatDate(activeCall.started_at) }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="flex h-2 w-2 rounded-full" :class="callWs.isConnected ? 'bg-emerald-500' : 'bg-amber-400'" />
            <span class="text-xs text-slate-500">{{ callWs.isConnected ? 'Подключено' : 'Соединение…' }}</span>
          </div>
        </div>

        <!-- Error bar -->
        <div v-if="mediaError || livekit.errorMessage.value || callError" class="flex items-center gap-2 rounded-xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4 shrink-0">
            <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {{ mediaError || livekit.errorMessage.value || callError }}
        </div>

        <!-- Video grid + sidebar -->
        <div class="grid gap-4 lg:grid-cols-[1fr_280px]">

          <!-- Left: video + controls + whiteboard -->
          <div class="flex flex-col gap-4">

            <!-- Video area -->
            <div class="overflow-hidden rounded-2xl border border-slate-200 bg-slate-900">

              <!-- LiveKit tiles: speaker/pinned layout -->
              <template v-if="livekit.tiles.value.length">

                <!-- Speaker view: pinned tile + thumbnail row -->
                <div v-if="pinnedTile" class="flex flex-col gap-0.5 p-1">
                  <LivekitTile
                    :tile="pinnedTile"
                    :is-pinned="true"
                    :is-speaking="livekit.activeSpeakers.value.includes(pinnedTile.identity)"
                    class="w-full"
                    @pin="pinTile"
                  />
                  <!-- Thumbnail strip -->
                  <div
                    v-if="thumbnailTiles.length"
                    class="flex gap-0.5 overflow-x-auto"
                  >
                    <LivekitTile
                      v-for="tile in thumbnailTiles"
                      :key="tile.identity"
                      :tile="tile"
                      :is-pinned="false"
                      :is-speaking="livekit.activeSpeakers.value.includes(tile.identity)"
                      class="w-40 shrink-0"
                      @pin="pinTile"
                    />
                  </div>
                </div>

                <!-- Grid view: no pin selected -->
                <div
                  v-else
                  class="grid gap-0.5 p-1"
                  :class="{
                    'grid-cols-1': livekit.tiles.value.length === 1,
                    'grid-cols-2': livekit.tiles.value.length >= 2 && livekit.tiles.value.length <= 4,
                    'grid-cols-3': livekit.tiles.value.length >= 5,
                  }"
                >
                  <LivekitTile
                    v-for="tile in livekit.tiles.value"
                    :key="tile.identity"
                    :tile="tile"
                    :is-pinned="false"
                    :is-speaking="livekit.activeSpeakers.value.includes(tile.identity)"
                    @pin="pinTile"
                  />
                </div>
              </template>

              <!-- No LiveKit tiles yet — show local raw stream preview -->
              <div v-else class="relative aspect-video">
                <video v-if="cameraStream" ref="localVideoRef" autoplay muted playsinline class="h-full w-full object-cover" />
                <div v-else class="flex h-full flex-col items-center justify-center gap-3 py-12">
                  <div class="flex h-12 w-12 items-center justify-center rounded-full bg-white/10 text-white/40">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="h-6 w-6">
                      <line x1="2" y1="2" x2="22" y2="22" /><path d="M7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16" /><path d="M9.5 4h5L17 7h3a2 2 0 0 1 2 2v7.5" /><path d="M14.121 15.121A3 3 0 1 1 9.88 10.88" />
                    </svg>
                  </div>
                  <p class="text-sm text-white/40">Камера выключена</p>
                </div>
                <video v-if="screenStream" ref="screenVideoRef" autoplay muted playsinline class="absolute inset-0 h-full w-full bg-black/80 object-contain" />
              </div>
            </div>

            <!-- Controls bar -->
            <div class="flex flex-wrap items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3">
              <!-- Camera toggle -->
              <button
                class="flex h-10 w-10 items-center justify-center rounded-full transition"
                :class="hasCamera ? 'bg-sky-100 text-sky-700 hover:bg-sky-200' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'"
                :title="hasCamera ? 'Выключить камеру' : 'Включить камеру'"
                @click="toggleCameraUnified"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
                  <template v-if="hasCamera">
                    <path d="M15 10l4.553-2.07A1 1 0 0 1 21 8.845v6.31a1 1 0 0 1-1.447.915L15 14" /><rect x="2" y="7" width="13" height="10" rx="2" />
                  </template>
                  <template v-else>
                    <line x1="2" y1="2" x2="22" y2="22" /><path d="M7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16" /><path d="M9.5 4h5L17 7h3a2 2 0 0 1 2 2v7.5" /><path d="M14.121 15.121A3 3 0 1 1 9.88 10.88" />
                  </template>
                </svg>
              </button>

              <!-- Mic toggle -->
              <button
                class="flex h-10 w-10 items-center justify-center rounded-full transition"
                :class="isMicActive ? 'bg-sky-100 text-sky-700 hover:bg-sky-200' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'"
                :title="isMicActive ? 'Выключить микрофон' : 'Включить микрофон'"
                @click="toggleMicUnified"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
                  <template v-if="isMicActive">
                    <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" y1="19" x2="12" y2="22" />
                  </template>
                  <template v-else>
                    <line x1="2" y1="2" x2="22" y2="22" /><path d="M18.89 13.23A7.12 7.12 0 0 0 19 12v-2" /><path d="M5 10v2a7 7 0 0 0 9.64 6.57" /><path d="M12 19v3" /><path d="M8 23h8" /><path d="M12 2a3 3 0 0 1 3 3v5" /><path d="M9 9v3a3 3 0 0 0 5.12 2.12" />
                  </template>
                </svg>
              </button>

              <!-- Screen share -->
              <button
                class="flex h-10 w-10 items-center justify-center rounded-full transition"
                :class="hasScreen ? 'bg-amber-100 text-amber-700 hover:bg-amber-200' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'"
                :title="hasScreen ? 'Остановить демонстрацию' : 'Показать экран'"
                @click="toggleScreenUnified"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5">
                  <template v-if="!hasScreen">
                    <rect x="2" y="3" width="20" height="14" rx="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" />
                  </template>
                  <template v-else>
                    <path d="M13 3H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-3" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" /><line x1="22" y1="2" x2="11" y2="13" /><path d="M16 2h6v6" />
                  </template>
                </svg>
              </button>

              <div class="mx-1 h-6 w-px bg-slate-200" />

              <!-- End call -->
              <button
                class="flex h-10 items-center gap-2 rounded-full bg-rose-500 px-5 text-sm font-medium text-white hover:bg-rose-600 transition"
                @click="endCall"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4">
                  <path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7 2 2 0 0 1 1.72 2v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.42 19.42 0 0 1 4.26 13a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.17 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.15 9.8" /><line x1="23" y1="1" x2="1" y2="23" />
                </svg>
                Завершить
              </button>
            </div>

            <!-- Whiteboard -->
            <div v-if="activeCall.tldraw_room" class="overflow-hidden rounded-2xl border border-slate-200">
              <div class="flex items-center gap-2 border-b border-slate-100 bg-white px-4 py-2.5">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4 text-slate-500">
                  <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                </svg>
                <p class="text-sm font-medium text-slate-800">Совместная доска</p>
              </div>
              <TeamCallWhiteboard
                :room-id="activeCall.tldraw_room"
                :user-id="session?.email?.replace('@', '-') || 'guest'"
                :user-name="session?.displayName || session?.email || 'User'"
              />
            </div>

          </div>

          <!-- Right sidebar: participants + chat -->
          <div class="flex flex-col gap-4">

            <!-- Participants -->
            <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white">
              <div class="flex items-center gap-2 border-b border-slate-100 px-4 py-2.5">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4 text-slate-500">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                <p class="text-sm font-semibold text-slate-800">Участники</p>
                <span class="ml-auto rounded-full bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500">{{ Object.keys(callWs.participants).length }}</span>
              </div>
              <div class="max-h-[260px] divide-y divide-slate-50 overflow-y-auto">
                <div v-for="(participant, identity) in callWs.participants" :key="identity" class="flex items-center gap-3 px-4 py-3">
                  <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-600">
                    {{ (participant.name || participant.email || '?').charAt(0).toUpperCase() }}
                  </span>
                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm font-medium text-slate-800">{{ participant.name || participant.email }}</p>
                    <div class="mt-0.5 flex gap-1.5">
                      <svg v-if="participant.isCameraOn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3 text-sky-500" title="Камера">
                        <path d="M15 10l4.553-2.07A1 1 0 0 1 21 8.845v6.31a1 1 0 0 1-1.447.915L15 14" /><rect x="2" y="7" width="13" height="10" rx="2" />
                      </svg>
                      <svg v-if="participant.isMicOn" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3 text-emerald-500" title="Микрофон">
                        <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z" /><path d="M19 10v2a7 7 0 0 1-14 0v-2" /><line x1="12" y1="19" x2="12" y2="22" />
                      </svg>
                      <svg v-if="participant.isScreenSharing" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3 text-amber-500" title="Экран">
                        <rect x="2" y="3" width="20" height="14" rx="2" /><line x1="8" y1="21" x2="16" y2="21" /><line x1="12" y1="17" x2="12" y2="21" />
                      </svg>
                    </div>
                  </div>
                </div>
                <div v-if="!Object.keys(callWs.participants).length" class="px-4 py-6 text-center">
                  <p class="text-xs text-slate-400">Нет других участников</p>
                </div>
              </div>
            </div>

            <!-- Chat -->
            <div class="flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white">
              <div class="flex items-center gap-2 border-b border-slate-100 px-4 py-2.5">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4 text-slate-500">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
                <p class="text-sm font-semibold text-slate-800">Чат созвона</p>
              </div>
              <div class="space-y-3 overflow-y-auto px-3 py-3" style="max-height: 360px;">
                <div v-for="message in chatMessages" :key="message.id">
                  <div class="flex items-baseline gap-2">
                    <span class="text-xs font-medium text-slate-700">{{ message.author_name || 'Участник' }}</span>
                    <span class="text-xs text-slate-400">{{ formatDate(message.created_at) }}</span>
                  </div>
                  <p class="mt-0.5 rounded-xl rounded-tl-sm bg-slate-50 px-3 py-2 text-sm text-slate-700">{{ message.body }}</p>
                </div>
                <div v-if="!chatMessages.length" class="py-6 text-center text-xs text-slate-400">
                  Начните общение в чате
                </div>
              </div>
              <div class="border-t border-slate-100 p-3">
                <div class="flex gap-2">
                  <input
                    v-model="chatBody"
                    class="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm outline-none placeholder:text-slate-400 focus:border-sky-400 focus:bg-white focus:ring-2 focus:ring-sky-100"
                    placeholder="Написать сообщение…"
                    @keydown.enter.prevent="sendChat"
                  >
                  <button
                    class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-sky-500 text-white transition hover:bg-sky-600 disabled:opacity-40"
                    :disabled="!chatBody.trim()"
                    @click="sendChat"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4">
                      <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

          </div>
        </div>

      </template>
    </div>
  </div>
</template>

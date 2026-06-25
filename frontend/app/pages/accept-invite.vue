<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { SessionEntity } from '~/common/auth/entities/session.entity';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import { useSession } from '~/shared/app/hooks/use-session';

definePageMeta({
  layout: 'auth',
});

const { get } = usePlatformApi();
const { save } = useSession();
const route = useRoute();
const router = useRouter();

type State = 'loading' | 'success' | 'error';
const state = ref<State>('loading');
const errorMessage = ref('');
const memberEmail = ref('');

onMounted(async () => {
  const token = String(route.query.token ?? '').trim();
  if (!token) {
    state.value = 'error';
    errorMessage.value = 'Токен приглашения отсутствует. Используйте ссылку из письма.';
    return;
  }
  try {
    const session = await get<SessionEntity>(`/api/v1/platform/invite/accept?token=${encodeURIComponent(token)}`);
    memberEmail.value = session.email;
    save(session);
    state.value = 'success';
    setTimeout(() => router.replace('/team'), 2500);
  } catch (error: any) {
    state.value = 'error';
    errorMessage.value = error?.data?.detail ?? 'Не удалось принять приглашение. Ссылка могла устареть.';
  }
});
</script>

<template>
  <div class="grid gap-6">

    <!-- Loading -->
    <div v-if="state === 'loading'" class="flex flex-col items-center gap-4 py-4 text-center">
      <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-100 text-sky-600">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-7 w-7 animate-spin">
          <path d="M21 12a9 9 0 1 1-6.219-8.56" />
        </svg>
      </div>
      <div>
        <p class="font-semibold text-slate-900">Проверяем приглашение…</p>
        <p class="mt-1 text-sm text-slate-500">Подождите несколько секунд.</p>
      </div>
    </div>

    <!-- Success -->
    <div v-else-if="state === 'success'" class="flex flex-col items-center gap-4 py-4 text-center">
      <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-600">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-7 w-7">
          <path d="M20 6 9 17l-5-5" />
        </svg>
      </div>
      <div>
        <p class="font-semibold text-slate-900">Вы вошли в команду!</p>
        <p class="mt-1 text-sm text-slate-500">{{ memberEmail }}</p>
        <p class="mt-3 text-xs text-slate-400">Перенаправляем в раздел команды…</p>
      </div>
      <NuxtLink to="/team" class="text-sm text-sky-600 hover:underline">Перейти сейчас</NuxtLink>
    </div>

    <!-- Error -->
    <div v-else class="flex flex-col items-center gap-4 py-4 text-center">
      <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-100 text-rose-600">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-7 w-7">
          <circle cx="12" cy="12" r="10" />
          <line x1="15" y1="9" x2="9" y2="15" />
          <line x1="9" y1="9" x2="15" y2="15" />
        </svg>
      </div>
      <div>
        <p class="font-semibold text-slate-900">Не удалось принять приглашение</p>
        <p class="mt-2 text-sm text-slate-500">{{ errorMessage }}</p>
      </div>
      <NuxtLink to="/login" class="text-sm text-sky-600 hover:underline">Войти в аккаунт</NuxtLink>
    </div>

  </div>
</template>

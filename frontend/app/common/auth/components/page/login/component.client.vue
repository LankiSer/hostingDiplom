<script setup lang="ts">
import { ref } from 'vue';
import { navigateTo, useRoute } from '#imports';
import { AUTH_LOGIN_COPY } from '../../../constants/messages';
import { useSession } from '../../../../../shared/app/hooks/use-session';
import SignInForm from './.partials/components/sign-in/component.vue';
import RegisterForm from './.partials/components/register/component.vue';
import type { SessionEntity } from '../../../entities/session.entity';

const route = useRoute();
const { save } = useSession();
const mode = ref<'login' | 'register'>('login');

async function handleSuccess(session: SessionEntity) {
  save(session);
  await navigateTo(String(route.query.redirect ?? '/dashboard'));
}
</script>

<template>
  <div class="grid gap-6">
    <div class="grid gap-2 text-center">
      <p class="text-xs font-semibold uppercase tracking-[0.2em] text-sky-600">{{ AUTH_LOGIN_COPY.badge }}</p>
      <h1 class="text-2xl font-semibold text-slate-900">{{ AUTH_LOGIN_COPY.title }}</h1>
      <p class="text-sm leading-6 text-slate-500">{{ AUTH_LOGIN_COPY.description }}</p>
    </div>

    <div class="relative grid grid-cols-2 rounded-xl border border-slate-200 bg-slate-50 p-1">
      <span
        class="absolute bottom-1 top-1 w-[calc(50%-4px)] rounded-lg bg-white shadow-sm transition-transform duration-300"
        :class="mode === 'register' ? 'translate-x-[calc(100%+4px)]' : 'translate-x-0'"
      />
      <button
        type="button"
        class="relative z-10 rounded-lg py-2.5 text-sm font-medium transition-colors"
        :class="mode === 'login' ? 'text-sky-700' : 'text-slate-500'"
        @click="mode = 'login'"
      >
        {{ AUTH_LOGIN_COPY.modeLogin }}
      </button>
      <button
        type="button"
        class="relative z-10 rounded-lg py-2.5 text-sm font-medium transition-colors"
        :class="mode === 'register' ? 'text-sky-700' : 'text-slate-500'"
        @click="mode = 'register'"
      >
        {{ AUTH_LOGIN_COPY.modeRegister }}
      </button>
    </div>

    <SignInForm v-if="mode === 'login'" @success="handleSuccess" />
    <RegisterForm v-else @success="handleSuccess" />
  </div>
</template>

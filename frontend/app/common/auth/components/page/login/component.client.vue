<script setup lang="ts">
import { ref } from 'vue';
import { navigateTo, useRoute } from '#imports';
import { AUTH_LOGIN_COPY } from '../../../constants/messages';
import AppBadge from '../../../../../shared/app/components/ui/badge/component.vue';
import AppButton from '../../../../../shared/app/components/ui/button/component.vue';
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
    <AppBadge :label="AUTH_LOGIN_COPY.badge" />
    <div class="grid gap-3">
      <h1 class="text-3xl font-semibold text-white">{{ AUTH_LOGIN_COPY.title }}</h1>
      <p class="text-sm leading-6 text-slate-400">{{ AUTH_LOGIN_COPY.description }}</p>
    </div>
    <div class="flex flex-wrap gap-3">
      <AppButton :label="AUTH_LOGIN_COPY.modeLogin" :tone="mode === 'login' ? 'primary' : 'secondary'" @click="mode = 'login'" />
      <AppButton :label="AUTH_LOGIN_COPY.modeRegister" :tone="mode === 'register' ? 'primary' : 'secondary'" @click="mode = 'register'" />
    </div>
    <SignInForm v-if="mode === 'login'" @success="handleSuccess" />
    <RegisterForm v-else @success="handleSuccess" />
    <div class="grid gap-2 text-sm text-slate-400">
      <p>{{ AUTH_LOGIN_COPY.legalHint }}</p>
      <div class="flex flex-wrap gap-3">
        <NuxtLink class="text-sky-300 hover:text-sky-200" to="/legal/privacy">Политика конфиденциальности</NuxtLink>
        <NuxtLink class="text-sky-300 hover:text-sky-200" to="/legal/personal-data">Согласие на обработку данных</NuxtLink>
      </div>
    </div>
  </div>
</template>

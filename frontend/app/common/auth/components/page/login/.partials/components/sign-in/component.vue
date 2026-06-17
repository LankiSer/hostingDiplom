<script setup lang="ts">
import { ref } from 'vue';
import { AUTH_LOGIN_COPY } from '~/common/auth/constants/messages';
import type { SessionEntity } from '~/common/auth/entities/session.entity';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCheckbox from '~/shared/app/components/ui/checkbox/component.vue';
import AppInput from '~/shared/app/components/ui/input/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';

const emit = defineEmits<{ success: [session: SessionEntity] }>();
const { post } = usePlatformApi();
const email = ref('');
const password = ref('');
const acceptTerms = ref(false);
const errorMessage = ref('');
const isSubmitting = ref(false);

async function handleSubmit() {
  if (!acceptTerms.value) return;
  errorMessage.value = '';
  isSubmitting.value = true;
  try {
    const session = await post<SessionEntity>('/api/v1/platform/login', {
      email: email.value,
      password: password.value,
      accept_policy: acceptTerms.value,
      accept_personal_data: acceptTerms.value,
    });
    emit('success', session);
  } catch {
    errorMessage.value = 'Не удалось войти. Проверь email и пароль.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <form class="grid gap-4" @submit.prevent="handleSubmit">
    <AppInput v-model="email" :label="AUTH_LOGIN_COPY.emailLabel" :placeholder="AUTH_LOGIN_COPY.emailPlaceholder" type="email" />
    <AppInput v-model="password" :label="AUTH_LOGIN_COPY.passwordLabel" :placeholder="AUTH_LOGIN_COPY.passwordPlaceholder" type="password" />

    <AppCheckbox v-model="acceptTerms">
      Я принимаю
      <NuxtLink class="text-sky-600 hover:underline" to="/legal/privacy">пользовательское соглашение</NuxtLink>
      и
      <NuxtLink class="text-sky-600 hover:underline" to="/legal/personal-data">политику обработки данных</NuxtLink>
    </AppCheckbox>

    <p v-if="errorMessage" class="text-sm text-rose-600">{{ errorMessage }}</p>
    <AppButton
      :disabled="isSubmitting || !acceptTerms || !email || !password"
      :label="isSubmitting ? AUTH_LOGIN_COPY.submitting : AUTH_LOGIN_COPY.submit"
      type="submit"
    />
  </form>
</template>

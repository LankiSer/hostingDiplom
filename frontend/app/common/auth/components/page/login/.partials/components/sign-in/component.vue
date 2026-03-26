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
const email = ref('owner@gcloude.ru');
const organization = ref('ООО Гклауд');
const acceptPolicy = ref(false);
const acceptPersonalData = ref(false);
const errorMessage = ref('');
const isSubmitting = ref(false);

async function handleSubmit() {
  if (!acceptPolicy.value || !acceptPersonalData.value) return;
  errorMessage.value = '';
  isSubmitting.value = true;
  try {
    const session = await post<SessionEntity>('/api/v1/platform/login', { email: email.value, organization: organization.value });
    emit('success', session);
  } catch {
    errorMessage.value = 'Не удалось войти. Открой `localhost` или проверь локальный `nginx`.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <form class="grid gap-4" @submit.prevent="handleSubmit">
    <AppInput v-model="email" :label="AUTH_LOGIN_COPY.emailLabel" :placeholder="AUTH_LOGIN_COPY.emailPlaceholder" />
    <AppInput v-model="organization" :label="AUTH_LOGIN_COPY.organizationLabel" :placeholder="AUTH_LOGIN_COPY.organizationPlaceholder" />
    <AppCheckbox v-model="acceptPolicy" :label="AUTH_LOGIN_COPY.consentPolicy" />
    <AppCheckbox v-model="acceptPersonalData" :label="AUTH_LOGIN_COPY.consentPersonalData" />
    <p v-if="errorMessage" class="text-sm text-rose-300">{{ errorMessage }}</p>
    <AppButton :disabled="isSubmitting || !acceptPolicy || !acceptPersonalData" :label="isSubmitting ? AUTH_LOGIN_COPY.submitting : AUTH_LOGIN_COPY.submit" type="submit" />
  </form>
</template>

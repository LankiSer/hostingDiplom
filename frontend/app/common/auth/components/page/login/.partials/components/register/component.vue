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
const companyName = ref('ООО Гклауд');
const contactName = ref('Александр Смирнов');
const email = ref('owner@gcloude.ru');
const inn = ref('7701234567');
const acceptPolicy = ref(false);
const acceptPersonalData = ref(false);
const errorMessage = ref('');
const isSubmitting = ref(false);

async function handleSubmit() {
  errorMessage.value = '';
  isSubmitting.value = true;
  try {
    const session = await post<SessionEntity>('/api/v1/platform/register', {
      accept_personal_data: acceptPersonalData.value,
      accept_policy: acceptPolicy.value,
      company_name: companyName.value,
      contact_name: contactName.value,
      email: email.value,
      inn: inn.value
    });
    emit('success', session);
  } catch {
    errorMessage.value = 'Не удалось зарегистрировать организацию. Повтори попытку через локальный кабинет.';
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <form class="grid gap-4" @submit.prevent="handleSubmit">
    <AppInput v-model="companyName" :label="AUTH_LOGIN_COPY.registerCompanyLabel" :placeholder="AUTH_LOGIN_COPY.registerCompanyPlaceholder" />
    <AppInput v-model="contactName" :label="AUTH_LOGIN_COPY.registerContactLabel" :placeholder="AUTH_LOGIN_COPY.registerContactPlaceholder" />
    <AppInput v-model="email" :label="AUTH_LOGIN_COPY.emailLabel" :placeholder="AUTH_LOGIN_COPY.emailPlaceholder" />
    <AppInput v-model="inn" :label="AUTH_LOGIN_COPY.registerInnLabel" :placeholder="AUTH_LOGIN_COPY.registerInnPlaceholder" />
    <AppCheckbox v-model="acceptPolicy" :label="AUTH_LOGIN_COPY.consentPolicy" />
    <AppCheckbox v-model="acceptPersonalData" :label="AUTH_LOGIN_COPY.consentPersonalData" />
    <p v-if="errorMessage" class="text-sm text-rose-300">{{ errorMessage }}</p>
    <AppButton :disabled="isSubmitting || !acceptPolicy || !acceptPersonalData" :label="isSubmitting ? AUTH_LOGIN_COPY.registerSubmitting : AUTH_LOGIN_COPY.registerSubmit" type="submit" />
  </form>
</template>

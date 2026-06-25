<script setup lang="ts">
import { useCookieConsent } from '~/shared/app/hooks/use-cookie-consent';

const { acceptAll, acceptNecessaryOnly, isResolved } = useCookieConsent();
</script>

<template>
  <Teleport to="body">
    <div
      v-if="!isResolved"
      class="fixed inset-x-0 bottom-0 z-[100] border-t border-slate-200 bg-white/95 p-4 shadow-[0_-8px_30px_-12px_rgba(15,23,42,0.25)] backdrop-blur-sm sm:p-5"
      role="dialog"
      aria-live="polite"
      aria-label="Согласие на использование cookie"
    >
      <div class="mx-auto flex max-w-5xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="min-w-0 text-sm leading-6 text-slate-600">
          <p class="font-medium text-slate-900">Мы используем cookie</p>
          <p>
            Обязательные cookie нужны для входа и работы кабинета. Подробнее —
            <NuxtLink class="text-sky-600 hover:underline" to="/legal/cookies">политика cookie</NuxtLink>,
            <NuxtLink class="text-sky-600 hover:underline" to="/legal/privacy">конфиденциальность</NuxtLink>,
            <NuxtLink class="text-sky-600 hover:underline" to="/legal">реквизиты и документы</NuxtLink>.
          </p>
        </div>
        <div class="flex shrink-0 flex-wrap gap-2">
          <button
            type="button"
            class="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            @click="acceptNecessaryOnly"
          >
            Только необходимые
          </button>
          <button
            type="button"
            class="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700"
            @click="acceptAll"
          >
            Принять все
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

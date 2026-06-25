<script setup lang="ts">
import { LEGAL_DOCUMENTS } from '~/shared/app/constants/legal-entity';

definePageMeta({
  layout: 'legal',
  title: 'Юридическая информация',
  subtitle: 'Реквизиты оператора и документы платформы.',
});
</script>

<template>
  <div class="grid gap-6 text-sm leading-6 text-slate-600">
    <div class="grid gap-2">
      <h1 class="text-2xl font-semibold text-slate-900">Юридическая информация</h1>
      <p>
        Здесь собраны реквизиты оператора платформы gcloude и документы, которые регулируют
        использование сервиса, обработку персональных данных и cookie.
      </p>
    </div>

    <LegalEntityInfo />

    <section class="grid gap-3">
      <h2 class="text-base font-semibold text-slate-900">Документы</h2>
      <div class="grid gap-2">
        <NuxtLink
          v-for="doc in LEGAL_DOCUMENTS"
          :key="doc.to"
          :to="doc.to"
          class="rounded-xl border border-slate-200 bg-white px-4 py-3 transition hover:border-sky-200 hover:bg-sky-50/40"
        >
          <p class="font-medium text-slate-900">{{ doc.title }}</p>
          <p class="mt-0.5 text-xs text-slate-500">{{ doc.description }}</p>
        </NuxtLink>
      </div>
    </section>

    <p class="text-xs text-slate-400">
      По вопросам обработки данных и юридическим запросам используйте контактный email оператора,
      указанный в реквизитах выше.
    </p>
  </div>
</template>

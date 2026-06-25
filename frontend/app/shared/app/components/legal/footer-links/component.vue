<script setup lang="ts">
withDefaults(
  defineProps<{ centered?: boolean }>(),
  { centered: false },
);
</script>

<template>
  <nav
    class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500"
    :class="centered ? 'justify-center' : ''"
    aria-label="Юридические документы"
  >
    <NuxtLink class="font-medium text-sky-600 hover:underline" to="/legal">Юридическая информация</NuxtLink>
    <NuxtLink class="hover:text-sky-600 hover:underline" to="/legal/terms">Пользовательское соглашение</NuxtLink>
    <NuxtLink class="hover:text-sky-600 hover:underline" to="/legal/privacy">Конфиденциальность</NuxtLink>
    <NuxtLink class="hover:text-sky-600 hover:underline" to="/legal/personal-data">Персональные данные</NuxtLink>
    <NuxtLink class="hover:text-sky-600 hover:underline" to="/legal/cookies">Cookie</NuxtLink>
  </nav>
</template>

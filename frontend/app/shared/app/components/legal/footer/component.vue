<script setup lang="ts">
import { computed } from 'vue';
import { useLegalEntity } from '~/shared/app/hooks/use-legal-entity';

withDefaults(
  defineProps<{ centered?: boolean; compact?: boolean }>(),
  { centered: false, compact: true },
);

const { entity } = useLegalEntity();
const year = computed(() => new Date().getFullYear());
</script>

<template>
  <footer
    class="grid gap-3 border-t border-slate-200/80 pt-4"
    :class="centered ? 'text-center' : ''"
    aria-label="Юридическая информация"
  >
    <LegalEntityInfo :compact="compact" :show-title="!compact" />

    <LegalFooterLinks :centered="centered" />

    <p class="text-[11px] leading-5 text-slate-400" :class="centered ? 'mx-auto max-w-lg' : ''">
      © {{ year }} {{ entity.companyName }}.
      <NuxtLink class="text-sky-600 hover:underline" to="/legal">Юридическая информация</NuxtLink>
    </p>
  </footer>
</template>

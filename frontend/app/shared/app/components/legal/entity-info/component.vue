<script setup lang="ts">
import { computed } from 'vue';
import { useLegalEntity } from '~/shared/app/hooks/use-legal-entity';

const props = withDefaults(
  defineProps<{ compact?: boolean; showTitle?: boolean }>(),
  { compact: false, showTitle: true },
);

const { entity } = useLegalEntity();

const rows = computed(() => [
  { label: 'Наименование', value: entity.value.companyName },
  { label: 'ИНН', value: entity.value.inn },
  { label: 'ОГРН', value: entity.value.ogrn },
  { label: 'КПП', value: entity.value.kpp },
  { label: 'Юридический адрес', value: entity.value.legalAddress },
  { label: 'Email', value: entity.value.email, href: entity.value.email ? `mailto:${entity.value.email}` : undefined },
  ...(entity.value.phone ? [{ label: 'Телефон', value: entity.value.phone, href: `tel:${entity.value.phone}` }] : []),
]);
</script>

<template>
  <section
    class="text-xs text-slate-500"
    :class="compact ? 'grid gap-1' : 'rounded-xl border border-slate-200 bg-slate-50/80 p-4'"
    aria-label="Реквизиты оператора платформы"
  >
    <p v-if="showTitle" class="text-sm font-semibold text-slate-800" :class="compact ? 'mb-0.5' : 'mb-3'">
      Оператор платформы
    </p>

    <template v-if="compact">
      <p class="leading-5 text-slate-600">{{ entity.companyName }}</p>
      <p class="leading-5">
        <span v-if="entity.inn">ИНН {{ entity.inn }}</span>
        <span v-if="entity.ogrn" class="ml-2">ОГРН {{ entity.ogrn }}</span>
        <span v-if="entity.kpp" class="ml-2">КПП {{ entity.kpp }}</span>
      </p>
    </template>

    <dl v-else class="grid gap-2 sm:grid-cols-2">
      <div v-for="row in rows" :key="row.label" class="grid gap-0.5">
        <dt class="font-medium text-slate-500">{{ row.label }}</dt>
        <dd class="text-sm text-slate-800">
          <a v-if="row.href" :href="row.href" class="text-sky-600 hover:underline">{{ row.value }}</a>
          <span v-else>{{ row.value || '—' }}</span>
        </dd>
      </div>
    </dl>
  </section>
</template>

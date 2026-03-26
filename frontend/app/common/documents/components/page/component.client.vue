<script setup lang="ts">
import { ref } from 'vue';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import AppSection from '~/shared/app/components/content/section/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import type { InvoiceEntity } from '../../../billing/entities/invoice.entity';

const { get, post } = usePlatformApi();
const { data: invoices, pending, refresh } = useAsyncData<InvoiceEntity[]>(
  'documents-invoices',
  () => get('/api/v1/billing/invoices'),
  { lazy: true }
);

const state = ref<{ marking: string | null; error: string }>({ marking: null, error: '' });

function statusTone(s: string) {
  return s === 'paid' ? 'success' : s === 'issued' ? 'default' : s === 'cancelled' ? 'danger' : 'muted';
}

function statusLabel(s: string) {
  return s === 'paid' ? 'Оплачен' : s === 'issued' ? 'Выставлен' : s === 'cancelled' ? 'Отменён' : 'Черновик';
}

function formatAmount(n: number) {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(n);
}

function formatDate(iso: string) {
  return iso ? new Date(iso).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—';
}

function docNumber(inv: InvoiceEntity) {
  return inv.onec_number ? `№${inv.onec_number}` : `INV-${inv.id.slice(0, 8).toUpperCase()}`;
}

async function markPaid(inv: InvoiceEntity) {
  if (inv.status === 'paid') return;
  state.value.marking = inv.id;
  state.value.error = '';
  try {
    await post(`/api/v1/billing/invoices/${inv.id}/mark-paid`, {});
    await refresh();
  } catch {
    state.value.error = 'Ошибка обновления статуса';
  } finally {
    state.value.marking = null;
  }
}

async function cancel(inv: InvoiceEntity) {
  if (inv.status === 'cancelled') return;
  state.value.marking = inv.id;
  state.value.error = '';
  try {
    await post(`/api/v1/billing/invoices/${inv.id}/cancel`, {});
    await refresh();
  } catch {
    state.value.error = 'Ошибка отмены';
  } finally {
    state.value.marking = null;
  }
}
</script>

<template>
  <AppSection title="Документы" description="Счета и акты для юрлиц. Реальные данные из биллинга.">
    <div v-if="pending && !invoices?.length" class="rounded-xl border border-white/5 px-5 py-12 text-center text-sm text-slate-500">
      Загрузка...
    </div>
    <div v-else-if="!invoices?.length" class="rounded-xl border border-white/5 px-5 py-12 text-center text-sm text-slate-600">
      Нет документов. Создайте счёт в разделе
      <NuxtLink to="/billing" class="text-sky-400 hover:text-sky-300">Биллинг</NuxtLink>.
    </div>
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <AppCard v-for="inv in invoices" :key="inv.id" class="flex flex-col">
        <div class="grid flex-1 gap-3">
          <div class="flex items-start justify-between gap-2">
            <h3 class="truncate text-lg font-semibold text-white">{{ docNumber(inv) }}</h3>
            <AppBadge :label="statusLabel(inv.status)" :tone="statusTone(inv.status)" />
          </div>
          <p class="text-sm leading-5 text-slate-400">{{ inv.description || 'Без назначения' }}</p>
          <div class="grid gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5">
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">Юрлицо</span>
              <strong class="truncate max-w-[140px] text-right text-white">{{ inv.company_name }}</strong>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">ИНН</span>
              <strong class="text-white">{{ inv.inn || '—' }}</strong>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">Сумма</span>
              <strong class="text-white">{{ formatAmount(inv.amount) }}</strong>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">Дата</span>
              <strong class="text-white">{{ formatDate(inv.created_at) }}</strong>
            </div>
          </div>
          <div class="mt-auto flex flex-wrap gap-2">
            <AppButton
              v-if="inv.status !== 'paid' && inv.status !== 'cancelled'"
              :disabled="state.marking === inv.id"
              :label="state.marking === inv.id ? '...' : 'Оплачен'"
              tone="primary"
              @click="markPaid(inv)"
            />
            <AppButton
              v-if="inv.status !== 'cancelled'"
              :disabled="state.marking === inv.id"
              :label="state.marking === inv.id ? '...' : 'Отменить'"
              tone="secondary"
              @click="cancel(inv)"
            />
            <NuxtLink to="/billing">
              <AppButton label="В биллинг" tone="secondary" />
            </NuxtLink>
          </div>
        </div>
      </AppCard>
    </div>
    <p v-if="state.error" class="mt-4 text-sm text-rose-300">{{ state.error }}</p>
  </AppSection>
</template>

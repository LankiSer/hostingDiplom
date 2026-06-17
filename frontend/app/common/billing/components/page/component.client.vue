<script setup lang="ts">
import { reactive, ref } from 'vue';
import AppBadge from '~/shared/app/components/ui/badge/component.vue';
import AppButton from '~/shared/app/components/ui/button/component.vue';
import AppCard from '~/shared/app/components/ui/card/component.vue';
import AppInput from '~/shared/app/components/ui/input/component.vue';
import { usePlatformApi } from '~/shared/app/hooks/use-platform-api';
import type { InvoiceEntity } from '../../entities/invoice.entity';

const { get, post } = usePlatformApi();
const { data: invoices, refresh } = useAsyncData<InvoiceEntity[]>('billing-invoices', () => get('/api/v1/billing/invoices'));
const { data: onecStatus } = useAsyncData('billing-status', () => get('/api/v1/billing/status'));

const showForm = ref(false);
const form = reactive({ company_name: '', inn: '', amount: '', description: '' });
const state = reactive({ saving: false, error: '' });

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

async function exportFor1C() {
  try {
    const data = await get<Record<string, unknown>[]>('/api/v1/billing/invoices/export');
    const blob = new Blob([JSON.stringify(data ?? [], null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `invoices_1c_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  } catch {
    state.error = 'Ошибка выгрузки';
  }
}

async function createInvoice() {
  if (!form.company_name.trim() || !form.amount) return;
  state.saving = true;
  state.error = '';
  try {
    await post('/api/v1/billing/invoices', {
      company_name: form.company_name,
      inn: form.inn,
      amount: parseFloat(form.amount),
      description: form.description,
    });
    Object.assign(form, { company_name: '', inn: '', amount: '', description: '' });
    showForm.value = false;
    await refresh();
  } catch (e: any) {
    state.error = e?.data?.detail ?? 'Ошибка создания счёта';
  } finally {
    state.saving = false;
  }
}

const marking = ref<string | null>(null);

async function markPaid(inv: InvoiceEntity) {
  if (inv.status === 'paid') return;
  marking.value = inv.id;
  state.error = '';
  try {
    await post(`/api/v1/billing/invoices/${inv.id}/mark-paid`, {});
    await refresh();
  } catch {
    state.error = 'Ошибка обновления статуса';
  } finally {
    marking.value = null;
  }
}

async function cancel(inv: InvoiceEntity) {
  if (inv.status === 'cancelled') return;
  marking.value = inv.id;
  state.error = '';
  try {
    await post(`/api/v1/billing/invoices/${inv.id}/cancel`, {});
    await refresh();
  } catch {
    state.error = 'Ошибка отмены';
  } finally {
    marking.value = null;
  }
}
</script>

<template>
  <div class="grid gap-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-slate-900">Биллинг</h2>
        <p class="text-sm text-slate-500">
          1С:
          <span v-if="(onecStatus as any)?.onec_configured" class="text-emerald-600">подключена ✓</span>
          <span v-else>обмен через файл — выгрузите JSON и загрузите в 1С</span>
        </p>
      </div>
      <div class="flex gap-2">
        <AppButton label="Новый счёт" @click="showForm = !showForm" />
        <AppButton label="Выгрузить для 1С" tone="secondary" @click="exportFor1C" />
      </div>
    </div>

    <AppCard v-if="showForm">
      <div class="grid gap-3">
        <h3 class="text-sm font-semibold text-slate-900">Выставить счёт</h3>
        <div class="grid gap-3 sm:grid-cols-2">
          <AppInput v-model="form.company_name" label="Компания" placeholder="ООО Ромашка" />
          <AppInput v-model="form.inn" label="ИНН" placeholder="7712345678" />
        </div>
        <div class="grid gap-3 sm:grid-cols-2">
          <AppInput v-model="form.amount" label="Сумма (₽)" placeholder="50000" />
          <AppInput v-model="form.description" label="Назначение платежа" placeholder="Хостинг за апрель" />
        </div>
        <div class="flex items-center gap-2">
          <AppButton :disabled="state.saving" :label="state.saving ? 'Создаём...' : 'Выставить счёт'" @click="createInvoice" />
          <AppButton label="Отмена" tone="secondary" @click="showForm = false" />
        </div>
        <p v-if="state.error" class="text-sm text-rose-600">{{ state.error }}</p>
      </div>
    </AppCard>

    <div v-if="!invoices?.length" class="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-5 py-8 text-center text-sm text-slate-500">
      Нет счётов. Создайте первый.
    </div>

    <div v-else class="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div
        v-for="(inv, i) in invoices"
        :key="inv.id"
        :class="['grid grid-cols-1 gap-3 px-4 py-3 sm:grid-cols-[1fr_auto_auto] sm:items-center', i > 0 && 'border-t border-slate-100']"
      >
        <div class="min-w-0">
          <p class="truncate text-sm font-medium text-slate-900">{{ inv.company_name }}</p>
          <p class="text-xs text-slate-500">
            ИНН {{ inv.inn || '—' }} · {{ inv.description || 'без назначения' }} · {{ formatDate(inv.created_at) }}
            <span v-if="inv.onec_number" class="ml-2 text-sky-500">№{{ inv.onec_number }} в 1С</span>
          </p>
        </div>
        <div class="flex shrink-0 items-center gap-3">
          <span class="text-sm font-semibold text-slate-900">{{ formatAmount(inv.amount) }}</span>
          <AppBadge :label="statusLabel(inv.status)" :tone="statusTone(inv.status)" />
        </div>
        <div class="flex flex-wrap gap-2">
          <AppButton
            v-if="inv.status !== 'paid' && inv.status !== 'cancelled'"
            :disabled="marking === inv.id"
            :label="marking === inv.id ? '...' : 'Оплачен'"
            tone="secondary"
            @click="markPaid(inv)"
          />
          <AppButton
            v-if="inv.status !== 'cancelled'"
            :disabled="marking === inv.id"
            :label="marking === inv.id ? '...' : 'Отменить'"
            tone="secondary"
            @click="cancel(inv)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

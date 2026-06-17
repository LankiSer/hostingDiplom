<script setup lang="ts">
import { computed } from 'vue';
import AppBadge from '../../ui/badge/component.vue';
import AppButton from '../../ui/button/component.vue';
import AppCard from '../../ui/card/component.vue';
import AppSection from '../../content/section/component.vue';
import RemotePageSkeleton from './skeleton.vue';
import { classNames } from '../../../utils/class-names';
import { usePlatformApi } from '../../../hooks/use-platform-api';
import type { WorkspacePageEntity } from '../../../entities/workspace-page.entity';
import type { WorkspaceRemotePageProps } from './interface';

const props = defineProps<WorkspaceRemotePageProps>();
const { get } = usePlatformApi();
const key = computed(() => `${props.cacheKey}:${props.path}`);
const { data, error, pending, refresh } = useAsyncData<WorkspacePageEntity | null>(key, () => get(props.path), {
  default: () => null,
  lazy: true
});

function isExternal(to: string) {
  return to.startsWith('http');
}
</script>

<template>
  <RemotePageSkeleton v-if="pending && !data" />
  <AppSection v-else-if="error || !data" title="Данные недоступны" description="Локальный API не ответил. Повтори запрос или проверь `gateway-service`.">
    <AppButton label="Повторить запрос" @click="refresh" />
  </AppSection>
  <AppSection v-else :title="data.title" :description="data.description">
    <div class="app-page-columns">
      <AppCard v-for="card in data.cards" :key="card.title">
        <div class="grid gap-3">
          <AppBadge v-if="card.badge" :label="card.badge.label" :tone="card.badge.tone" />
          <div class="grid gap-2">
            <h3 class="text-lg font-semibold text-slate-900">{{ card.title }}</h3>
            <p class="text-sm leading-5 text-slate-500">{{ card.description }}</p>
          </div>
          <div v-if="card.facts?.length" class="grid gap-2">
            <div v-for="fact in card.facts" :key="`${card.title}-${fact.label}`" class="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5 text-sm">
              <span class="text-slate-500">{{ fact.label }}</span>
              <strong class="text-slate-900">{{ fact.value }}</strong>
            </div>
          </div>
          <div v-if="card.actions?.length" class="flex flex-wrap gap-3">
            <a v-for="action in card.actions.filter((item) => isExternal(item.to))" :key="action.to" :href="action.to" target="_blank" rel="noreferrer" :class="classNames('inline-flex items-center justify-center rounded-2xl px-4 py-3 text-sm font-semibold transition', action.tone === 'secondary' ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50' : 'bg-sky-600 text-white hover:bg-sky-500')">{{ action.label }}</a>
            <NuxtLink v-for="action in card.actions.filter((item) => !isExternal(item.to))" :key="action.to" :to="action.to" :class="classNames('inline-flex items-center justify-center rounded-2xl px-4 py-3 text-sm font-semibold transition', action.tone === 'secondary' ? 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50' : 'bg-sky-600 text-white hover:bg-sky-500')">{{ action.label }}</NuxtLink>
          </div>
        </div>
      </AppCard>
    </div>
  </AppSection>
</template>

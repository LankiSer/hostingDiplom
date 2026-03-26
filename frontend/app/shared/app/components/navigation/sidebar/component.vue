<script setup lang="ts">
import { useRoute } from '#imports';
import { useNavigation } from '../../../hooks/use-navigation';
import { useSession } from '../../../hooks/use-session';
import { classNames } from '../../../utils/class-names';

const route = useRoute();
const { grouped } = useNavigation();
const { session } = useSession();

function isActive(to: string) {
  return route.path === to || route.path.startsWith(`${to}/`);
}
</script>

<template>
  <aside class="flex h-screen w-[220px] flex-col overflow-y-auto border-r border-white/5 bg-slate-950 px-3 pb-4 pt-5">
    <div class="mb-5 flex items-center gap-2 px-2">
      <div class="flex h-6 w-6 items-center justify-center rounded-md bg-sky-500 text-xs font-bold text-white">G</div>
      <span class="text-sm font-semibold text-white">gcloude</span>
    </div>

    <div v-if="session" class="mb-5 rounded-lg bg-white/5 px-3 py-2">
      <p class="truncate text-xs font-medium text-slate-200">{{ session.displayName }}</p>
      <p class="truncate text-xs text-slate-500">{{ session.companyName }}</p>
    </div>

    <nav class="flex flex-1 flex-col gap-5">
      <div v-for="group in grouped" :key="group.group">
        <p class="mb-1.5 px-2 text-[10px] font-semibold uppercase tracking-widest text-slate-600">
          {{ group.label }}
        </p>
        <div class="flex flex-col gap-0.5">
          <NuxtLink
            v-for="item in group.items"
            :key="item.to"
            :to="item.to"
            :class="classNames(
              'block rounded-lg px-3 py-2 text-sm transition-colors',
              isActive(item.to)
                ? 'bg-sky-500/15 font-medium text-sky-300'
                : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
            )"
          >
            {{ item.label }}
          </NuxtLink>
        </div>
      </div>
    </nav>
  </aside>
</template>

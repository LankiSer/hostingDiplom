<script setup lang="ts">
import type { AppNavigationIcon } from '../../../entities/navigation.entity';

defineProps<{ icon: AppNavigationIcon; active?: boolean }>();
</script>

<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.75"
    stroke-linecap="round"
    stroke-linejoin="round"
    class="h-[18px] w-[18px]"
    aria-hidden="true"
  >
    <template v-if="icon === 'dashboard'">
      <rect x="3" y="3" width="7" height="9" rx="1.5" />
      <rect x="14" y="3" width="7" height="5" rx="1.5" />
      <rect x="14" y="12" width="7" height="9" rx="1.5" />
      <rect x="3" y="16" width="7" height="5" rx="1.5" />
    </template>
    <template v-else-if="icon === 'projects'">
      <path d="M4 7h16M4 12h16M4 17h10" />
      <circle cx="19" cy="17" r="2" />
    </template>
    <template v-else-if="icon === 'apps'">
      <rect x="4" y="4" width="6" height="6" rx="1.5" />
      <rect x="14" y="4" width="6" height="6" rx="1.5" />
      <rect x="4" y="14" width="6" height="6" rx="1.5" />
      <rect x="14" y="14" width="6" height="6" rx="1.5" />
    </template>
    <template v-else-if="icon === 'deployments'">
      <path d="M12 3v10" />
      <path d="M8 9l4 4 4-4" />
      <rect x="5" y="15" width="14" height="6" rx="1.5" />
    </template>
    <template v-else-if="icon === 'domains'">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" />
    </template>
    <template v-else-if="icon === 'logs'">
      <path d="M8 6h12M8 12h12M8 18h12" />
      <circle cx="4" cy="6" r="1" fill="currentColor" stroke="none" />
      <circle cx="4" cy="12" r="1" fill="currentColor" stroke="none" />
      <circle cx="4" cy="18" r="1" fill="currentColor" stroke="none" />
    </template>
    <template v-else-if="icon === 'billing'">
      <rect x="3" y="6" width="18" height="12" rx="2" />
      <path d="M3 10h18" />
    </template>
    <template v-else-if="icon === 'documents'">
      <path d="M8 4h8l4 4v12a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z" />
      <path d="M16 4v4h4" />
    </template>
    <template v-else-if="icon === 'team'">
      <circle cx="9" cy="8" r="3" />
      <circle cx="17" cy="9" r="2.5" />
      <path d="M3 19c0-3 3-5 6-5s6 2 6 5" />
      <path d="M16 19c0-2 2-3.5 4-3.5" />
    </template>
    <template v-else>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v2M12 20v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M2 12h2M20 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4" />
    </template>
  </svg>
</template>

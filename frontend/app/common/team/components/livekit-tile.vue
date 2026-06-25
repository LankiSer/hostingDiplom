<script setup lang="ts">
import { onMounted, watch } from 'vue';
import { ref } from 'vue';
import type { LivekitParticipantTile } from '../hooks/use-livekit-room';

const props = defineProps<{
  tile: LivekitParticipantTile;
  isPinned?: boolean;
  isSpeaking?: boolean;
}>();

const emit = defineEmits<{ pin: [identity: string] }>();

const hostRef = ref<HTMLDivElement | null>(null);

function mountVideo() {
  if (!hostRef.value || !props.tile.videoEl) return;
  hostRef.value.replaceChildren(props.tile.videoEl);
  props.tile.videoEl.className = 'h-full w-full object-cover';
}

watch(() => props.tile.videoEl, mountVideo);
onMounted(mountVideo);
</script>

<template>
  <div
    class="group relative aspect-video overflow-hidden rounded-xl bg-slate-900 transition-all duration-200 cursor-pointer"
    :class="{
      'ring-2 ring-emerald-400 ring-offset-1 ring-offset-slate-900': isSpeaking && !isPinned,
      'ring-2 ring-sky-500 ring-offset-1 ring-offset-slate-900': isPinned,
    }"
    @click="emit('pin', tile.identity)"
  >
    <!-- Video host -->
    <div ref="hostRef" class="h-full w-full" />

    <!-- Avatar placeholder when no video -->
    <div
      v-if="!tile.videoEl"
      class="absolute inset-0 flex flex-col items-center justify-center gap-2"
    >
      <div
        class="flex h-14 w-14 items-center justify-center rounded-full text-xl font-semibold"
        :class="tile.isLocal ? 'bg-sky-700 text-sky-100' : 'bg-slate-700 text-slate-200'"
      >
        {{ (tile.name || '?').charAt(0).toUpperCase() }}
      </div>
      <p class="text-xs text-slate-400">{{ tile.isCameraOn ? 'Видео…' : 'Камера выкл.' }}</p>
    </div>

    <!-- Speaking pulse ring overlay -->
    <div
      v-if="isSpeaking"
      class="pointer-events-none absolute inset-0 rounded-xl ring-2 ring-emerald-400 animate-pulse"
    />

    <!-- Bottom name bar -->
    <div class="absolute bottom-0 left-0 right-0 flex items-center gap-1.5 bg-gradient-to-t from-black/70 to-transparent px-2.5 pb-2 pt-4">
      <!-- Speaking mic pulse dot -->
      <span
        v-if="isSpeaking"
        class="flex h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-400 animate-pulse"
      />
      <span class="flex-1 truncate text-xs font-medium text-white">
        {{ tile.name }}{{ tile.isLocal ? ' (вы)' : '' }}
      </span>
      <!-- Mic status -->
      <span v-if="!tile.isMicOn" class="shrink-0 text-rose-400" title="Микрофон выкл.">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3">
          <line x1="2" y1="2" x2="22" y2="22" />
          <path d="M18.89 13.23A7.12 7.12 0 0 0 19 12v-2" />
          <path d="M5 10v2a7 7 0 0 0 9.64 6.57" />
          <path d="M12 19v3" />
          <path d="M12 2a3 3 0 0 1 3 3v5" />
          <path d="M9 9v3a3 3 0 0 0 5.12 2.12" />
        </svg>
      </span>
      <!-- Screen share badge -->
      <span v-if="tile.isScreenShare" class="rounded bg-amber-500/80 px-1 py-0.5 text-[10px] font-medium text-white">Экран</span>
      <!-- Pin hint on hover -->
      <span
        v-if="!isPinned"
        class="pointer-events-none hidden shrink-0 text-white/60 group-hover:block"
        title="Закрепить"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="h-3 w-3">
          <line x1="12" y1="17" x2="12" y2="22" />
          <path d="M5 17h14v-1.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V6h1a2 2 0 0 0 0-4H8a2 2 0 0 0 0 4h1v4.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24Z" />
        </svg>
      </span>
    </div>
  </div>
</template>

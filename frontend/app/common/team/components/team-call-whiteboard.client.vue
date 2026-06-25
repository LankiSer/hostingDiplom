<script setup lang="ts">
import { onMounted, onUnmounted, ref, shallowRef } from 'vue';
import { useTldrawSync } from '../hooks/use-tldraw-sync';

const props = defineProps<{
  roomId: string;
  userId: string;
  userName: string;
}>();

const containerRef = ref<HTMLDivElement | null>(null);
const editorRef = shallowRef<any>(null);
const syncError = ref('');
const tldrawSync = useTldrawSync();

let reactRoot: { unmount: () => void } | null = null;
let syncTimer: ReturnType<typeof setTimeout> | null = null;
let lastSentHash = '';
let applyingRemote = false;

function objectHash(obj: unknown): string {
  try { return JSON.stringify(obj).slice(0, 64); } catch { return ''; }
}

function scheduleSync() {
  if (!editorRef.value || applyingRemote) return;
  if (syncTimer) clearTimeout(syncTimer);
  syncTimer = setTimeout(async () => {
    if (!editorRef.value || applyingRemote) return;
    try {
      const { getSnapshot } = await import('@tldraw/tldraw');
      const { document } = getSnapshot(editorRef.value);
      // Hash only the store records so send/receive hashes are computed the same way
      const hash = objectHash(document.store);
      if (hash === lastSentHash) return;
      lastSentHash = hash;
      tldrawSync.sync({ document, roomId: props.roomId, userId: props.userId });
    } catch (err) {
      console.warn('[tldraw] getSnapshot failed:', err);
    }
  }, 400);
}

async function applyRemoteSnapshot(payload: Record<string, unknown>) {
  if (!editorRef.value) return;

  // Validate incoming snapshot structure
  const doc = payload.document as { store?: Record<string, unknown>; schema?: unknown } | undefined;
  if (!doc?.store || typeof doc.store !== 'object') return;

  const hash = objectHash(doc.store);
  if (hash === lastSentHash) return;  // we sent this — skip echo

  const editor = editorRef.value;
  applyingRemote = true;
  try {
    const incomingStore = doc.store as Record<string, any>;
    const records = Object.values(incomingStore).filter(Boolean);
    if (!records.length) return;

    // mergeRemoteChanges is the tldraw v3-recommended way to apply external data:
    // it does NOT trigger user history or 'user' source listeners.
    editor.store.mergeRemoteChanges(() => {
      editor.store.put(records);

      // Remove records missing in remote snapshot (preserve viewport/selection state)
      const remoteIds = new Set(Object.keys(incomingStore));
      const toRemove = editor.store
        .allRecords()
        .map((r: any) => r.id as string)
        .filter((id: string) =>
          !remoteIds.has(id) &&
          !id.startsWith('instance') &&
          !id.startsWith('camera') &&
          !id.startsWith('pointer'),
        );
      if (toRemove.length) editor.store.remove(toRemove as any);
    });

    lastSentHash = hash;
  } catch (err) {
    console.warn('[tldraw] mergeRemoteChanges failed:', err);
  } finally {
    applyingRemote = false;
  }
}

async function mountTldraw() {
  if (!containerRef.value || !import.meta.client) return;

  const [{ createRoot }, React, { Tldraw }] = await Promise.all([
    import('react-dom/client'),
    import('react'),
    import('@tldraw/tldraw'),
  ]);
  await import('@tldraw/tldraw/tldraw.css');

  const handleMount = (editor: any) => {
    editorRef.value = editor;
    tldrawSync.setSyncHandler(applyRemoteSnapshot);
    tldrawSync.connect(props.roomId, props.userId, props.userName);
    // source: 'user' only fires for user-initiated changes, not remote loadSnapshot
    editor.store.listen(() => scheduleSync(), { source: 'user', scope: 'document' });
  };

  reactRoot = createRoot(containerRef.value);
  reactRoot.render(
    React.createElement(Tldraw, {
      onMount: handleMount,
    }),
  );
}

onMounted(async () => {
  try {
    await mountTldraw();
  } catch (error: any) {
    syncError.value = error?.message || 'Не удалось загрузить tldraw.';
  }
});

onUnmounted(() => {
  if (syncTimer) clearTimeout(syncTimer);
  tldrawSync.disconnect();
  reactRoot?.unmount();
  reactRoot = null;
});
</script>

<template>
  <div class="grid gap-2">
    <div class="flex items-center justify-between">
      <p class="text-sm font-medium text-slate-800">Совместная доска</p>
      <span class="text-xs" :class="tldrawSync.state.value.isConnected ? 'text-emerald-600' : 'text-amber-600'">
        {{ tldrawSync.state.value.isConnected ? 'Синхронизация активна' : 'Подключение к доске…' }}
      </span>
    </div>
    <p v-if="syncError || tldrawSync.state.value.errorMessage" class="text-sm text-rose-600">
      {{ syncError || tldrawSync.state.value.errorMessage }}
    </p>
    <div ref="containerRef" class="h-[480px] w-full overflow-hidden rounded-lg border border-slate-200 bg-white" />
  </div>
</template>

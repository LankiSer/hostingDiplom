import { ref, onUnmounted } from 'vue';
import { buildPlatformWsUrl } from '~/shared/app/utils/ws-url';

export interface TldrawSyncState {
  isConnected: boolean;
  remoteUsers: Record<string, { x: number; y: number; color: string }>;
  errorMessage: string;
}

export function useTldrawSync() {
  const ws = ref<WebSocket | null>(null);
  const state = ref<TldrawSyncState>({
    isConnected: false,
    remoteUsers: {},
    errorMessage: '',
  });

  let onSyncHandler: ((payload: Record<string, unknown>) => void) | null = null;

  const connect = (roomId: string, userId: string, userName: string) => {
    disconnect();

    const url = buildPlatformWsUrl(`/api/v1/platform/ws/tldraw/${roomId}`, {
      identity: userId,
      email: userName.includes('@') ? userName : `${userId}@local`,
    });

    ws.value = new WebSocket(url);

    ws.value.onopen = () => {
      state.value.isConnected = true;
      state.value.errorMessage = '';
    };

    ws.value.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as Record<string, unknown>;
        handleIncomingMessage(message);
      } catch (error) {
        console.error('Failed to parse tldraw sync message:', error);
      }
    };

    ws.value.onclose = () => {
      state.value.isConnected = false;
    };

    ws.value.onerror = () => {
      state.value.errorMessage = 'Не удалось подключиться к доске (WebSocket).';
    };
  };

  const disconnect = () => {
    if (ws.value) {
      ws.value.close();
      ws.value = null;
    }
    state.value.isConnected = false;
  };

  const setSyncHandler = (handler: (payload: Record<string, unknown>) => void) => {
    onSyncHandler = handler;
  };

  const sync = (payload: Record<string, unknown>) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return;
    ws.value.send(JSON.stringify({
      type: 'sync',
      payload,
    }));
  };

  const handleIncomingMessage = (message: Record<string, unknown>) => {
    const type = message.type as string;
    if (type === 'sync' && message.payload && onSyncHandler) {
      void onSyncHandler(message.payload as Record<string, unknown>);
      return;
    }

    if (type === 'selection' && message.payload) {
      const payload = message.payload as Record<string, unknown>;
      const userId = String(payload.userId || '');
      if (userId) {
        state.value.remoteUsers[userId] = {
          x: Number(payload.x || 0),
          y: Number(payload.y || 0),
          color: String(payload.color || '#0284c7'),
        };
      }
    }
  };

  onUnmounted(disconnect);

  return {
    connect,
    disconnect,
    state,
    sync,
    setSyncHandler,
  };
}

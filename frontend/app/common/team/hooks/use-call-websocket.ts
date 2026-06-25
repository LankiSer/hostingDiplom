import { reactive, ref, onUnmounted } from 'vue';
import { buildPlatformWsUrl } from '~/shared/app/utils/ws-url';

export interface CallParticipant {
  identity: string;
  name: string;
  email: string;
  isCameraOn: boolean;
  isMicOn: boolean;
  isScreenSharing: boolean;
}

export interface CallChatMessage {
  id: string;
  body: string;
  author_name: string;
  created_at: string;
}

interface CallWsMessage {
  type: string;
  sender_identity?: string;
  sender_name?: string;
  sender_email?: string;
  timestamp?: string;
  payload?: Record<string, unknown>;
}

export function useCallWebSocket() {
  const ws = ref<WebSocket | null>(null);
  const participants = reactive<Record<string, CallParticipant>>({});
  const chatMessages = ref<CallChatMessage[]>([]);
  const isConnected = ref(false);
  const errorMessage = ref('');

  const seenMessageIds = new Set<string>();

  const initMessages = (messages: CallChatMessage[]) => {
    seenMessageIds.clear();
    chatMessages.value = messages.map((m) => {
      seenMessageIds.add(m.id);
      return m;
    });
  };

  const connect = (sessionId: string, email: string, displayName = '') => {
    disconnect();

    const url = buildPlatformWsUrl(`/api/v1/platform/ws/calls/${sessionId}`, {
      email,
      name: displayName,
    });

    ws.value = new WebSocket(url);

    ws.value.onopen = () => {
      isConnected.value = true;
      errorMessage.value = '';
    };

    ws.value.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as CallWsMessage;
        handleIncomingMessage(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.value.onclose = () => {
      isConnected.value = false;
    };

    ws.value.onerror = () => {
      errorMessage.value = 'Не удалось подключиться к созвону (WebSocket).';
    };
  };

  const disconnect = () => {
    if (ws.value) {
      ws.value.close();
      ws.value = null;
    }
    isConnected.value = false;
    Object.keys(participants).forEach((key) => delete participants[key]);
    chatMessages.value = [];
    seenMessageIds.clear();
  };

  const sendChatMessage = (body: string) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN || !body.trim()) return;
    ws.value.send(JSON.stringify({
      type: 'chat',
      body,
    }));
  };

  const sendMediaStatus = (status: Partial<{ camera: boolean; mic: boolean; screen: boolean }>) => {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return;
    ws.value.send(JSON.stringify({
      type: 'media_status',
      ...status,
    }));
  };

  const handleIncomingMessage = (message: CallWsMessage) => {
    const identity = message.sender_identity || '';
    if (!identity) return;

    switch (message.type) {
      case 'participant_join':
        participants[identity] = {
          identity,
          name: message.sender_name || identity,
          email: message.sender_email || '',
          isCameraOn: false,
          isMicOn: true,
          isScreenSharing: false,
        };
        break;
      case 'participant_leave':
        delete participants[identity];
        break;
      case 'media_status':
        if (participants[identity]) {
          const participant = participants[identity];
          if (message.payload?.is_camera_on !== undefined) participant.isCameraOn = Boolean(message.payload.is_camera_on);
          if (message.payload?.is_mic_on !== undefined) participant.isMicOn = Boolean(message.payload.is_mic_on);
          if (message.payload?.is_screen_sharing !== undefined) participant.isScreenSharing = Boolean(message.payload.is_screen_sharing);
        }
        break;
      case 'chat': {
        const msgId = String(message.payload?.message_id || '');
        if (msgId && seenMessageIds.has(msgId)) break;
        if (msgId) seenMessageIds.add(msgId);
        chatMessages.value.push({
          id: msgId || String(Date.now()),
          body: String(message.payload?.body || ''),
          author_name: message.sender_name || 'Участник',
          created_at: message.timestamp || new Date().toISOString(),
        });
        break;
      }
      default:
        break;
    }
  };

  onUnmounted(disconnect);

  return {
    connect,
    disconnect,
    participants,
    chatMessages,
    initMessages,
    isConnected,
    errorMessage,
    sendChatMessage,
    sendMediaStatus,
  };
}

import { onUnmounted, ref, shallowRef } from 'vue';
import type { TeamCallLivekitConnection } from '../entities/team.entity';

type LiveKitRoom = import('livekit-client').Room;
type RemoteParticipant = import('livekit-client').RemoteParticipant;
type RemoteTrackPublication = import('livekit-client').RemoteTrackPublication;
type RemoteTrack = import('livekit-client').RemoteTrack;

export interface LivekitParticipantTile {
  identity: string;
  name: string;
  videoEl: HTMLVideoElement | null;
  isLocal: boolean;
  isCameraOn: boolean;
  isMicOn: boolean;
  isScreenShare: boolean;
}

export function useLivekitRoom() {
  const room = shallowRef<LiveKitRoom | null>(null);
  const isConnected = ref(false);
  const errorMessage = ref('');
  const tiles = ref<LivekitParticipantTile[]>([]);
  const isCameraEnabled = ref(false);
  const isMicEnabled = ref(false);
  const isScreenEnabled = ref(false);
  const activeSpeakers = ref<string[]>([]);

  const tileMap = new Map<string, LivekitParticipantTile>();

  function upsertTile(identity: string, patch: Partial<LivekitParticipantTile>) {
    const existing = tileMap.get(identity) ?? {
      identity,
      name: identity,
      videoEl: null,
      isLocal: false,
      isCameraOn: false,
      isMicOn: false,
      isScreenShare: false,
    };
    tileMap.set(identity, { ...existing, ...patch });
    tiles.value = Array.from(tileMap.values());
  }

  function attachVideoTrack(identity: string, track: any, isLocal = false, isScreenShare = false) {
    const el = track.attach() as HTMLVideoElement;
    el.autoplay = true;
    el.playsInline = true;
    if (isLocal) el.muted = true;
    const tileIdentity = isScreenShare ? `${identity}:screen` : identity;
    upsertTile(tileIdentity, {
      identity: tileIdentity,
      name: tileMap.get(identity)?.name || identity,
      videoEl: el,
      isCameraOn: !isScreenShare,
      isScreenShare,
      isLocal,
    });
  }

  async function connect(connection: TeamCallLivekitConnection) {
    await disconnect();
    errorMessage.value = '';

    try {
      const { Room, RoomEvent, Track } = await import('livekit-client');

      const livekitRoom = new Room({ adaptiveStream: true, dynacast: true });
      room.value = livekitRoom;

      livekitRoom
        .on(RoomEvent.ActiveSpeakersChanged, (speakers: any[]) => {
          activeSpeakers.value = speakers.map((s: any) => s.identity);
        })
        .on(RoomEvent.TrackSubscribed, (track: RemoteTrack, pub: RemoteTrackPublication, participant: RemoteParticipant) => {
          const isScreenShare = pub.source === Track.Source.ScreenShare;
          upsertTile(participant.identity, {
            name: participant.name || participant.identity,
            isMicOn: participant.isMicrophoneEnabled,
          });
          if (track.kind === 'video') {
            attachVideoTrack(participant.identity, track, false, isScreenShare);
            if (!isScreenShare) {
              upsertTile(participant.identity, { isCameraOn: true });
            }
          } else if (track.kind === 'audio') {
            const audioEl = track.attach() as HTMLAudioElement;
            audioEl.dataset.livekitAudio = participant.identity;
            document.body.appendChild(audioEl);
          }
        })
        .on(RoomEvent.TrackUnsubscribed, (track: RemoteTrack, pub: any, participant: RemoteParticipant) => {
          const isScreenShare = pub.source === Track.Source.ScreenShare;
          if (track.kind === 'video') {
            track.detach().forEach((el) => el.remove());
            if (isScreenShare) {
              const screenId = `${participant.identity}:screen`;
              tileMap.delete(screenId);
              tiles.value = Array.from(tileMap.values());
            } else {
              upsertTile(participant.identity, { isCameraOn: false, videoEl: null });
            }
          } else if (track.kind === 'audio') {
            track.detach().forEach((el) => el.remove());
            document.querySelectorAll(`[data-livekit-audio="${participant.identity}"]`).forEach((el) => el.remove());
          }
        })
        .on(RoomEvent.ParticipantDisconnected, (participant: RemoteParticipant) => {
          // Remove camera tile and screen tile
          tileMap.delete(participant.identity);
          tileMap.delete(`${participant.identity}:screen`);
          tiles.value = Array.from(tileMap.values());
          // Remove audio elements
          document.querySelectorAll(`[data-livekit-audio="${participant.identity}"]`).forEach((el) => el.remove());
        })
        .on(RoomEvent.LocalTrackPublished, (pub: any, participant: any) => {
          const track = pub.track;
          if (!track) return;
          if (track.kind === 'video') {
            const isScreenShare = pub.source === Track.Source.ScreenShare;
            attachVideoTrack(participant.identity, track, true, isScreenShare);
            if (isScreenShare) isScreenEnabled.value = true;
            else isCameraEnabled.value = true;
          }
          if (track.kind === 'audio') {
            isMicEnabled.value = true;
            upsertTile(participant.identity, { isMicOn: true });
          }
        })
        .on(RoomEvent.LocalTrackUnpublished, (pub: any, participant: any) => {
          const track = pub.track;
          if (!track) return;
          const isScreenShare = pub.source === Track.Source.ScreenShare;
          if (track.kind === 'video') {
            track.detach().forEach((el: HTMLVideoElement) => el.remove());
            if (isScreenShare) {
              isScreenEnabled.value = false;
              tileMap.delete(`${participant.identity}:screen`);
              tiles.value = Array.from(tileMap.values());
            } else {
              isCameraEnabled.value = false;
              upsertTile(participant.identity, { isCameraOn: false, videoEl: null });
            }
          }
          if (track.kind === 'audio') {
            isMicEnabled.value = false;
            upsertTile(participant.identity, { isMicOn: false });
          }
        })
        .on(RoomEvent.TrackMuted, (pub: any, participant: any) => {
          if (pub.kind === 'audio') upsertTile(participant.identity, { isMicOn: false });
          if (pub.kind === 'video' && pub.source !== Track.Source.ScreenShare) upsertTile(participant.identity, { isCameraOn: false });
        })
        .on(RoomEvent.TrackUnmuted, (pub: any, participant: any) => {
          if (pub.kind === 'audio') upsertTile(participant.identity, { isMicOn: true });
          if (pub.kind === 'video' && pub.source !== Track.Source.ScreenShare) upsertTile(participant.identity, { isCameraOn: true });
        });

      await livekitRoom.connect(connection.url, connection.token);
      isConnected.value = true;

      upsertTile(connection.identity, {
        name: connection.name,
        isLocal: true,
        isCameraOn: false,
        isMicOn: false,
      });

    } catch (error: any) {
      errorMessage.value = error?.message || 'Не удалось подключиться к LiveKit.';
      isConnected.value = false;
    }
  }

  async function toggleCamera() {
    if (!room.value) return;
    await room.value.localParticipant.setCameraEnabled(!room.value.localParticipant.isCameraEnabled);
  }

  async function toggleMic() {
    if (!room.value) return;
    await room.value.localParticipant.setMicrophoneEnabled(!room.value.localParticipant.isMicrophoneEnabled);
  }

  async function toggleScreenShare() {
    if (!room.value) return;
    await room.value.localParticipant.setScreenShareEnabled(!room.value.localParticipant.isScreenShareEnabled);
  }

  async function disconnect() {
    if (room.value) {
      room.value.disconnect();
      room.value = null;
    }
    // Remove all audio elements appended to document.body for this session
    document.querySelectorAll('[data-livekit-audio]').forEach((el) => el.remove());
    tileMap.clear();
    tiles.value = [];
    isConnected.value = false;
    isCameraEnabled.value = false;
    isMicEnabled.value = false;
    isScreenEnabled.value = false;
    activeSpeakers.value = [];
  }

  onUnmounted(() => { void disconnect(); });

  return {
    connect,
    disconnect,
    toggleCamera,
    toggleMic,
    toggleScreenShare,
    room,
    isConnected,
    errorMessage,
    tiles,
    isCameraEnabled,
    isMicEnabled,
    isScreenEnabled,
    activeSpeakers,
  };
}

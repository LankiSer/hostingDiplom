# Self-hosted Realtime Stack

This document describes the self-hosted solutions for real-time collaboration in the platform.

## Components

### 1. LiveKit (WebRTC Video/Audio)

LiveKit is a self-hosted SFU (Selective Forwarding Unit) for WebRTC video and audio communication.

**Configuration:**
- URL: `http://livekit:7880`
- WebSocket: `ws://localhost:7883` (host port mapped in docker-compose)

**Ports (docker-compose host mapping):**
- 7883/tcp → 7880 container — HTTP API and WebSocket signaling
- 7881/tcp - WSS (TLS WebSocket)
- 7882/udp - WebRTC media
- 443/tcp, udp - STUN/TURN
- 10000-10100/udp - WebRTC media range

**STUN/TURN Configuration:**
Edit `infrastructure/livekit/livekit.yaml`:
```yaml
rtc:
  stun_servers:
    - stun:stun.l.google.com:19302
  turn_servers:
    - protocol: udp
      port: 3478
      username: your_turn_username
      password: your_turn_password
```

### 2. Tldraw Sync (Collaborative Whiteboard)

Tldraw sync backend for real-time whiteboard collaboration using WebSockets.

**Endpoint (same-origin via gateway):**
- WebSocket: `wss://app.<domain>/api/v1/platform/ws/tldraw/{tldraw_room}`

Legacy standalone service (optional): `tldraw-sync-service` on port 8010 — not required when using gateway route.

**Features:**
- Real-time drawing synchronization
- Selection sync
- Undo/redo events
- Presence updates

### 3. Gateway Service WebSocket Signaling

Gateway service provides WebSocket signaling for team call participants.

**Endpoint:**
- WebSocket: `wss://app.<domain>/api/v1/platform/ws/calls/{session_id}?email=<user@email>`

**Features:**
- Participant join/leave events
- Media status updates (camera, mic, screen)
- Chat messages
- Whiteboard sync events

## API Endpoints

### LiveKit Connection
```
GET /api/v1/platform/team/calls/{session_id}/livekit
```

Returns LiveKit connection credentials including STUN/TURN servers.

### Call Participants
```
GET /api/v1/platform/team/calls/{session_id}/participants
```

Returns list of participants in a call room.

### Update Participant Status
```
POST /api/v1/platform/team/calls/{session_id}/participants/{identity}/update
```

Update participant media status (camera, mic, screen sharing).

### Kick Participant
```
POST /api/v1/platform/team/calls/{session_id}/participants/{identity}/kick
```

Kick participant from call room (admin only).

## Frontend Usage

### Call WebSocket Hook
```typescript
import { useCallWebSocket } from '~/common/team/hooks/use-call-websocket';

const callWs = useCallWebSocket();

// Connect to call room
callWs.connect(sessionId, email);

// Send chat message
callWs.sendChatMessage('Hello everyone!');

// Broadcast media status
callWs.sendMediaStatus({ camera: true, mic: false });

// Access participants
console.log(callWs.participants);
console.log(callWs.isConnected);
```

### Tldraw Sync Hook
```typescript
import { useTldrawSync } from '~/common/team/hooks/use-tldraw-sync';

const whiteboardSync = useTldrawSync();

// Connect to room
whiteboardSync.connect(roomId, userId, userName);

// Sync whiteboard state
whiteboardSync.sync({ shapes: [...] });

// Broadcast selection
whiteboardSync.selection({ userId, x, y });

// Undo/redo
whiteboardSync.undo();
whiteboardSync.redo();

// Check connection status
console.log(whiteboardSync.state.isConnected);
```

## Docker Compose

To start the realtime stack:

```bash
docker compose up -d --build livekit tldraw-sync-service
```

## Production Deployment

### 1. TURN Server
For WebRTC to work behind NAT/firewall, configure a TURN server:

```yaml
# infrastructure/livekit/livekit.yaml
turn_servers:
  - protocol: udp
    port: 3478
    username: your_turn_username
    password: your_turn_password
```

Update gateway-service `.env`:
```bash
LIVEKIT_TURN_URL=turn:your-turn-server.com:3478
LIVEKIT_TURN_USERNAME=your_turn_username
LIVEKIT_TURN_PASSWORD=your_turn_password
```

### 2. DNS Configuration
Add DNS entries:
```
tldraw-sync.apps.yourdomain.com -> your nginx ingress
```

### 3. TLS/SSL
Configure nginx with SSL certificates for production:
```nginx
server {
    listen 443 ssl;
    server_name tldraw-sync.apps.yourdomain.com;
    
    ssl_certificate /etc/ssl/certs/tldraw.crt;
    ssl_certificate_key /etc/ssl/private/tldraw.key;
    
    location /ws/tldraw/ {
        proxy_pass http://tldraw-sync-service:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

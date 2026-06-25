"""WebSocket signaling for real-time team call communication."""
import asyncio
from typing import Dict

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from src.core.rbac import CurrentUser

router = APIRouter()


class CallParticipant(BaseModel):
    """Participant in a call session."""
    identity: str
    name: str
    email: str
    is_camera_on: bool = False
    is_mic_on: bool = True
    is_screen_sharing: bool = False


class CallMessage(BaseModel):
    """Message between call participants."""
    type: str
    sender_identity: str
    sender_name: str
    sender_email: str
    timestamp: str
    payload: dict = {}


class CallRoomManager:
    """Manages call rooms and participant connections."""
    
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}
        self.participants: Dict[str, Dict[str, CallParticipant]] = {}
    
    def create_room(self, room_id: str) -> None:
        """Create a new call room if it doesn't exist."""
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
            self.participants[room_id] = {}
    
    def add_participant(self, room_id: str, identity: str, websocket: WebSocket) -> None:
        """Add a participant to a room."""
        if room_id not in self.rooms:
            self.create_room(room_id)
        self.rooms[room_id][identity] = websocket
        self.participants[room_id][identity] = CallParticipant(
            identity=identity, name="", email=""
        )
    
    def remove_participant(self, room_id: str, identity: str) -> None:
        """Remove a participant from a room."""
        if room_id in self.rooms and identity in self.rooms[room_id]:
            del self.rooms[room_id][identity]
        if room_id in self.participants and identity in self.participants[room_id]:
            del self.participants[room_id][identity]
    
    def get_participants(self, room_id: str) -> Dict[str, CallParticipant]:
        """Get all participants in a room."""
        return self.participants.get(room_id, {})
    
    async def broadcast(self, room_id: str, message: CallMessage, exclude: str | None = None) -> None:
        """Broadcast message to all participants in a room concurrently."""
        if room_id not in self.rooms:
            return
        message_dict = message.model_dump()
        targets = [
            ws for identity, ws in self.rooms[room_id].items()
            if not (exclude and identity == exclude)
        ]

        async def _send(ws: WebSocket) -> None:
            try:
                await ws.send_json(message_dict)
            except Exception:
                pass

        await asyncio.gather(*(_send(ws) for ws in targets))


room_manager = CallRoomManager()

# Status message types
MSG_TYPE_PARTICIPANT_JOIN = "participant_join"
MSG_TYPE_PARTICIPANT_LEAVE = "participant_leave"
MSG_TYPE_PARTICIPANT_UPDATE = "participant_update"
MSG_TYPE_CHAT = "chat"
MSG_TYPE_MEDIA_STATUS = "media_status"
MSG_TYPE_WHITEBOARD_SYNC = "whiteboard_sync"


@router.websocket("/api/v1/platform/ws/calls/{session_id}")
async def call_websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    email: str = Query(default=""),
    x_platform_email: str = Query(default=""),
) -> None:
    """
    WebSocket endpoint for real-time team call communication.
    
    Handles:
    - Participant join/leave
    - Chat messages
    - Media status updates (camera/mic/screen)
    - Whiteboard sync events
    """
    await websocket.accept()

    auth_email = (email or x_platform_email or websocket.headers.get("x-platform-email", "")).strip().lower()
    if not auth_email or auth_email == "anonymous@gcloude.local":
        await websocket.close(code=4001, reason="Unauthorized")
        return

    # Get current user from platform session
    try:
        from src.repositories.platform_repository import PlatformRepository
        access = PlatformRepository().resolve_access_for_email(
            auth_email,
            auto_activate_invite=True,
        )
        if "calls:read" not in access["permissions"]:
            raise ValueError("No call access")
        actor = CurrentUser(
            email=access["email"],
            role=access["role"],
            display_name=access["displayName"],
            permissions=access["permissions"],
        )
    except Exception:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    # Check if call session exists and is active
    from src.repositories.platform_repository import PlatformRepository
    from src.services.service import GatewayService
    
    service = GatewayService()
    try:
        call_session = service.get_call_session(session_id)
    except Exception:
        await websocket.close(code=4002, reason="Call session not found")
        return
    
    if call_session.get("status") != "active":
        await websocket.close(code=4003, reason="Call session is not active")
        return
    
    # Register participant
    identity = f"{actor.email.replace('@', '-')}-{session_id[:8]}"
    room_manager.add_participant(session_id, identity, websocket)
    
    # Notify others about new participant
    participant = CallParticipant(
        identity=identity,
        name=actor.display_name,
        email=actor.email,
    )
    room_manager.participants[session_id][identity] = participant
    
    join_message = CallMessage(
        type=MSG_TYPE_PARTICIPANT_JOIN,
        sender_identity=identity,
        sender_name=participant.name,
        sender_email=participant.email,
        timestamp=call_session.get("created_at", ""),
        payload={"participant": participant.model_dump()},
    )
    await room_manager.broadcast(session_id, join_message, exclude=identity)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == MSG_TYPE_CHAT:
                await handle_chat_message(websocket, session_id, data, actor, identity)
            elif message_type == MSG_TYPE_MEDIA_STATUS:
                await handle_media_status(session_id, data, identity)
            elif message_type == MSG_TYPE_WHITEBOARD_SYNC:
                await handle_whiteboard_sync(session_id, data, identity)
            else:
                # Unknown message type - ignore
                pass
                
    except WebSocketDisconnect:
        # Participant left
        room_manager.remove_participant(session_id, identity)
        
        leave_message = CallMessage(
            type=MSG_TYPE_PARTICIPANT_LEAVE,
            sender_identity=identity,
            sender_name=participant.name,
            sender_email=participant.email,
            timestamp=call_session.get("created_at", ""),
            payload={"participant_identity": identity},
        )
        await room_manager.broadcast(session_id, leave_message)


async def handle_chat_message(
    websocket: WebSocket,
    session_id: str,
    data: dict,
    actor: CurrentUser,
    identity: str,
) -> None:
    """Handle chat message from participant."""
    body = data.get("body", "").strip()
    if not body:
        return
    
    from src.services.service import GatewayService
    
    service = GatewayService()
    
    try:
        # Persist message to database
        message = service.add_call_message(
            session_id, body, kind="chat", actor=actor
        )
        
        chat_message = CallMessage(
            type=MSG_TYPE_CHAT,
            sender_identity=identity,
            sender_name=actor.display_name,
            sender_email=actor.email,
            timestamp=message.get("created_at", ""),
            payload={
                "message_id": message.get("id", ""),
                "body": body,
            },
        )
        await room_manager.broadcast(session_id, chat_message)
    except Exception:
        # Silently ignore database errors to not break WebSocket
        pass


async def handle_media_status(
    session_id: str,
    data: dict,
    identity: str,
) -> None:
    """Handle media status update from participant."""
    is_camera_on = data.get("camera", False)
    is_mic_on = data.get("mic", True)
    is_screen_sharing = data.get("screen", False)
    
    if session_id not in room_manager.participants:
        return
    
    participant = room_manager.participants[session_id].get(identity)
    if not participant:
        return
    
    participant.is_camera_on = is_camera_on
    participant.is_mic_on = is_mic_on
    participant.is_screen_sharing = is_screen_sharing
    
    media_message = CallMessage(
        type=MSG_TYPE_MEDIA_STATUS,
        sender_identity=identity,
        sender_name=participant.name,
        sender_email=participant.email,
        timestamp="",
        payload={
            "participant_identity": identity,
            "is_camera_on": is_camera_on,
            "is_mic_on": is_mic_on,
            "is_screen_sharing": is_screen_sharing,
        },
    )
    await room_manager.broadcast(session_id, media_message)


async def handle_whiteboard_sync(
    session_id: str,
    data: dict,
    identity: str,
) -> None:
    """Handle whiteboard sync event from participant."""
    whiteboard_message = CallMessage(
        type=MSG_TYPE_WHITEBOARD_SYNC,
        sender_identity=identity,
        sender_name="",
        sender_email="",
        timestamp="",
        payload=data.get("payload", {}),
    )
    await room_manager.broadcast(session_id, whiteboard_message)

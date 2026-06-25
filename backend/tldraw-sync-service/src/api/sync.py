"""WebSocket sync endpoint for tldraw collaborative whiteboard."""
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class TldrawRoomManager:
    """Manages tldraw room connections and state."""
    
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}
    
    def create_room(self, room_id: str) -> None:
        """Create a new room if it doesn't exist."""
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
    
    def add_connection(self, room_id: str, identity: str, websocket: WebSocket) -> None:
        """Add a WebSocket connection to a room."""
        if room_id not in self.rooms:
            self.create_room(room_id)
        self.rooms[room_id][identity] = websocket
    
    def remove_connection(self, room_id: str, identity: str) -> None:
        """Remove a WebSocket connection from a room."""
        if room_id in self.rooms and identity in self.rooms[room_id]:
            del self.rooms[room_id][identity]
    
    def broadcast(self, room_id: str, message: dict, exclude: str | None = None) -> None:
        """Broadcast message to all connections in a room."""
        if room_id not in self.rooms:
            return
        for identity, websocket in self.rooms[room_id].items():
            if exclude and identity == exclude:
                continue
            try:
                websocket.send_json(message)
            except Exception:
                pass


room_manager = TldrawRoomManager()


@router.websocket("/ws/tldraw/{room_id}")
async def tldraw_sync_endpoint(websocket: WebSocket, room_id: str) -> None:
    """
    WebSocket endpoint for tldraw collaborative whiteboard sync.
    
    Handles:
    - Join/leave room
    - Whiteboard state sync
    - Undo/redo events
    - Selection changes
    """
    await websocket.accept()
    
    # Extract user info from headers
    identity = websocket.headers.get("x-identity", "guest")
    email = websocket.headers.get("x-email", "")
    
    room_manager.add_connection(room_id, identity, websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            
            if event_type == "sync":
                # Whiteboard state sync
                room_manager.broadcast(room_id, data, exclude=identity)
            elif event_type == "selection":
                # Selection change event
                room_manager.broadcast(room_id, data, exclude=identity)
            elif event_type == "undo":
                # Undo event
                room_manager.broadcast(room_id, data, exclude=identity)
            elif event_type == "redo":
                # Redo event
                room_manager.broadcast(room_id, data, exclude=identity)
            elif event_type == "presence":
                # Presence update
                room_manager.broadcast(room_id, data, exclude=identity)
            else:
                # Unknown event type - ignore
                pass
                
    except WebSocketDisconnect:
        room_manager.remove_connection(room_id, identity)

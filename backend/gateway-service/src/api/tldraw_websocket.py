"""WebSocket sync for collaborative tldraw whiteboard (same-origin via gateway)."""
import asyncio
from typing import Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class TldrawRoomManager:
    def __init__(self) -> None:
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}

    def add_connection(self, room_id: str, identity: str, websocket: WebSocket) -> None:
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        self.rooms[room_id][identity] = websocket

    def remove_connection(self, room_id: str, identity: str) -> None:
        if room_id in self.rooms and identity in self.rooms[room_id]:
            del self.rooms[room_id][identity]
        if room_id in self.rooms and not self.rooms[room_id]:
            del self.rooms[room_id]

    async def broadcast(self, room_id: str, message: dict, exclude: str | None = None) -> None:
        if room_id not in self.rooms:
            return
        targets = [
            ws for identity, ws in self.rooms[room_id].items()
            if not (exclude and identity == exclude)
        ]

        async def _send(ws: WebSocket) -> None:
            try:
                await ws.send_json(message)
            except Exception:
                pass

        await asyncio.gather(*(_send(ws) for ws in targets))


room_manager = TldrawRoomManager()


@router.websocket("/api/v1/platform/ws/tldraw/{room_id}")
async def tldraw_sync_endpoint(
    websocket: WebSocket,
    room_id: str,
    identity: str = "guest",
    email: str = "",
) -> None:
    await websocket.accept()

    user_identity = identity.strip() or email.replace("@", "-") or "guest"

    room_manager.add_connection(room_id, user_identity, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            if event_type in {"sync", "selection", "undo", "redo", "presence"}:
                await room_manager.broadcast(room_id, data, exclude=user_identity)
    except WebSocketDisconnect:
        room_manager.remove_connection(room_id, user_identity)

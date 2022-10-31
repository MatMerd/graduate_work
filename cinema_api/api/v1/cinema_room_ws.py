from aioredis import Redis
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from api.ws_manager import WebsocketManager, get_websocket_manager
from crud.auth_crud import get_current_user
from schemas.cinema_room import User
from core import log


router = APIRouter()


@router.websocket("/{cinema_room_id}")
async def cinema_room_ws_messages(
    websocket: WebSocket,
    cinema_room_id: str,
    user: User = Depends(get_current_user),
    ws_manager: WebsocketManager = Depends(get_websocket_manager),
):
    await ws_manager.connect(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                await ws_manager.broadcast(data)
            except WebSocketDisconnect:
                await ws_manager.disconnect()
    except RuntimeError:
        log.main_logger.info("WebSocket client closed")

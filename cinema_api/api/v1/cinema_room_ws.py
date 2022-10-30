from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from api.ws_manager import WebsocketManager, get_websocket_manager
from core.utils import (
    construct_cinema_room_chanel_name,
)


router = APIRouter()


@router.websocket("/{cinema_room_id}")
async def cinema_room_ws_messages(
    websocket: WebSocket, cinema_room_id: str, ws_manager: WebsocketManager = Depends(get_websocket_manager)
):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.send_personal_message(f"You wrote: {data}", websocket)
            await ws_manager.broadcast(f"Says: {data}")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        await ws_manager.broadcast("left the chat")

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from api.ws_handlers import handlers_mapping
from api.ws_manager import WebsocketManager, get_websocket_manager
from core import log
from crud.auth_crud import get_current_user_ws
from schemas.cinema_room import User
from schemas.websocket_command import CommandType


router = APIRouter()


@router.websocket("/{cinema_room_id}")
async def cinema_room_ws_messages(
    websocket: WebSocket,
    cinema_room_id: str,
    user: User = Depends(get_current_user_ws),
    ws_manager: WebsocketManager = Depends(get_websocket_manager),
):
    await ws_manager.connect(websocket, user)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                command_type = data.get("command_type")
                if not command_type:
                    log.main_logger.info("Data from user are invalid. command_type not contain in data")
                command_type = CommandType(command_type)
                handler = handlers_mapping[command_type]
                await handler(ws_manager, data)
            except WebSocketDisconnect:
                user = ws_manager.users[websocket]
                log.main_logger.info(f"User {user.username} disconnected")
                await ws_manager.disconnect(websocket, user)
    except RuntimeError:
        log.main_logger.info(f"Users count: {len(ws_manager.users)}")
        log.main_logger.info(f"WebSocket client for {user.username} closed")

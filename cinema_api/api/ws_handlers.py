from typing import Any

from .ws_manager import WebsocketManager
from core.exceptions import UserPermissionError
from schemas.cinema_room import User, CinemaRoomUserTypeEnum
from schemas.websocket_command import Command, CommandType


async def pause_video(manager: WebsocketManager, command: dict[str, Any]):
    await manager.broadcast(command)


async def play_video(manager: WebsocketManager, command: dict[str, Any]):
    await manager.broadcast(command)


async def forward_video(manager: WebsocketManager, command: dict[str, Any]):
    parsed_command = Command(**command)
    ws = [
        ws for ws, u in manager.users.items() if u.username == parsed_command.username
    ][0]
    user = manager.users[ws]
    if user.cinema_room_user_type is CinemaRoomUserTypeEnum.admin:
        await manager.broadcast(command)
    else:
        await manager.send_personal_message(
            Command(
                command_type=CommandType.send_message,
                username=parsed_command.username,
                message="Only admin can forward video",
            ),
            ws,
        )
        raise UserPermissionError("User have not permission forwarding video")


async def rewind_video(manager: WebsocketManager, command: dict[str, Any]):
    parsed_command = Command(**command)
    ws = [
        ws for ws, u in manager.users.items() if u.username == parsed_command.username
    ][0]
    user = manager.users[ws]
    if user.cinema_room_user_type is CinemaRoomUserTypeEnum.admin:
        await manager.broadcast(command)
    else:
        await manager.send_personal_message(
            Command(
                command_type=CommandType.send_message,
                username=parsed_command.username,
                message="Only admin can rewind video",
            ),
            ws,
        )
        raise UserPermissionError("User have not permission rewinding video")


async def send_message(manager: WebsocketManager, command: dict[str, Any]):
    await manager.message_service.add_message_to_room(
        manager.cinema_room_chanel, command
    )
    await manager.broadcast(command)


async def exclude_user(manager: WebsocketManager, command: dict[str, Any]):
    parsed_command = Command(**command)
    ws = [
        ws for ws, u in manager.users.items() if u.username == parsed_command.username
    ][0]
    user = manager.users[ws]
    if user.cinema_room_user_type is CinemaRoomUserTypeEnum.admin:
        await manager.disconnect(ws, user)
    else:
        await manager.send_personal_message(
            Command(
                command_type=CommandType.send_message,
                username=parsed_command.username,
                message="Only admin can disconnect another user",
            ),
            ws,
        )
        raise UserPermissionError("User have not permission disconnect another user")    


handlers_mapping = {
    CommandType.pause_video: pause_video,
    CommandType.play_video: play_video,
    CommandType.forward_video: forward_video,
    CommandType.rewind_video: rewind_video,
    CommandType.send_message: send_message,
    CommandType.exclude_user: exclude_user,
}

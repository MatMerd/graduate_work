import asyncio
from typing import Any

from .ws_manager import WebsocketManager
from core import log
from core.tasks.cinema_room_film import increment_film_timestamp_coro
from schemas.cinema_room import CinemaRoomUserTypeEnum
from schemas.websocket_command import Command, CommandType


async def pause_video(manager: WebsocketManager, command: dict[str, Any]):
    manager.cinema_room = await manager.cinema_crud.pause_film(cinema_room=manager.cinema_room)
    await manager.broadcast(command)


async def stop_video(manager: WebsocketManager, command: dict[str, Any]):
    parsed_command = Command(**command)
    ws = [
        ws for ws, u in manager.users.items() if u.username == parsed_command.username
    ][0]
    user = manager.users[ws]
    if user.cinema_room_user_type is CinemaRoomUserTypeEnum.admin:
        manager.cinema_room = await manager.cinema_crud.stop_film(cinema_room=manager.cinema_room)
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


async def play_video(manager: WebsocketManager, command: dict[str, Any]):
    manager.cinema_room = await manager.cinema_crud.play_film(cinema_room=manager.cinema_room)
    asyncio.ensure_future(increment_film_timestamp_coro(manager))
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


handlers_mapping = {
    CommandType.stop_video: stop_video,
    CommandType.pause_video: pause_video,
    CommandType.play_video: play_video,
    CommandType.forward_video: forward_video,
    CommandType.rewind_video: rewind_video,
    CommandType.send_message: send_message,
    CommandType.exclude_user: exclude_user,
}

from functools import lru_cache
from typing import Any

import orjson
from fastapi import Depends, WebSocket

from crud.cinema_crud import CinemaCRUD, get_cinema_crud
from core import log
from core.utils import construct_cinema_room_chanel_messages_by_room_id
from schemas.cinema_room import User
from service.message_service import get_message_service, MessageService
from schemas.websocket_command import Command


# TODO: придумать, как это можно использовать
# async def pubsub(websocket: WebSocket, cinema_room_chanel_name: str, redis: Redis):
#     log.main_logger.info("Creating pubsub")
#     psub = redis.pubsub()

#     async def producer_handler(channel):
#         while True:
#             try:
#                 async with async_timeout.timeout(1):
#                     message = await channel.get_message(ignore_subscribe_messages=True)
#                     if message is not None:
#                             await websocket.send_text(message["data"])
#                     await asyncio.sleep(0.01)
#             except asyncio.TimeoutError:
#                 pass
#             except WebSocketDisconnect:
#                 log.main_logger.info("Web socket was closed")
#                 break


#     async with psub as p:
#         await p.subscribe(cinema_room_chanel_name)
#         chanel_messages_name = construct_cinema_room_chanel_messages_by_chanel_name(cinema_room_chanel_name)
#         messages = await redis.lrange(chanel_messages_name, 0, -1)
#         for message in reversed(messages):
#             await websocket.send_text(message)
#         await producer_handler(p)  # wait for reader to complete
#         await p.unsubscribe(cinema_room_chanel_name)

#     # closing all open connections
#     await psub.close()


# async def redis_connector(websocket: WebSocket, cinema_room_chanel_name: str, redis: Redis):
#     log.main_logger.info("Connecting web socket to redis chanel")
#     tsk = asyncio.create_task(pubsub(websocket, cinema_room_chanel_name, redis))
#     cinema_room_chanel_messages = construct_cinema_room_chanel_messages_by_chanel_name(cinema_room_chanel_name)

#     async def consumer_handler(websocket: WebSocket):
#         while not tsk.done():
#             while True:
#                 try:
#                     message = await websocket.receive_text()
#                     if message:
#                         await redis.publish(cinema_room_chanel_name, message)
#                         await redis.lpush(cinema_room_chanel_messages, message)

#                 except WebSocketDisconnect:
#                     log.main_logger.info("Close chanel")
#                     break
#             # send stop word
#             # await pub.publish(cinema_room_chanel_name, STOPWORD)
#         await redis.close()

#     await consumer_handler(websocket=websocket)


class WebsocketManager:
    def __init__(
        self,
        cinema_room_id: str,
        cinema_crud: CinemaCRUD,
        message_service: MessageService,
    ):
        self.cinema_crud = cinema_crud
        self.cinema_room_id = cinema_room_id
        self.users: dict[WebSocket, User] = dict()
        self.cinema_room_chanel = construct_cinema_room_chanel_messages_by_room_id(
            cinema_room_id
        )
        self.message_service = message_service

    async def connect(self, websocket: WebSocket, user: User):
        await websocket.accept()
        self.cinema_room = await self.cinema_crud.get_cinema_room(
            cinema_room_key=self.cinema_room_id
        )
        self.users[websocket] = user
        self.cinema_room = await self.cinema_crud.add_user_to_users_list(
            cinema_room=self.cinema_room, user=user
        )
        messages = await self.message_service.get_messages_from_room(
            self.cinema_room_chanel
        )
        for message in messages:
            await self.send_personal_message(message, websocket)
        log.main_logger.info(f"User connected to room: {user.username}")

    async def disconnect(self, websocket, user):
        del self.users[websocket]
        self.cinema_room = await self.cinema_crud.remove_user_from_user_list(
            cinema_room=self.cinema_room, user=user
        )

    async def send_personal_message(self, command: Command, websocket: WebSocket):
        jsonable_command = orjson.loads(command.json())
        await websocket.send_json(jsonable_command)

    async def broadcast(self, command: dict[str, Any]):
        Command(**command)
        for connection in self.users:
            await connection.send_json(command)


@lru_cache
def get_websocket_manager(
    cinema_room_id: str,
    cinema_crud=Depends(get_cinema_crud),
    message_service=Depends(get_message_service),
):
    return WebsocketManager(cinema_room_id, cinema_crud, message_service)

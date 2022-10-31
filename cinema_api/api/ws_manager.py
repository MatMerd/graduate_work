from fastapi import Depends, WebSocket, WebSocketDisconnect


from crud.cinema_crud import CinemaCRUD, get_cinema_crud
from db.redis import get_redis_client
from core import log
from core.utils import (
    construct_cinema_room_chanel_messages_by_chanel_name,
    construct_cinema_room_chanel_name,
)
from schemas.cinema_room import CinemaRoom, User


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
    def __init__(self, cinema_room_id: str, user: User, cinema_crud: CinemaCRUD):
        self.cinema_crud = cinema_crud
        self.cinema_room_id = cinema_room_id
        self.user = user

        self.cinema_room: CinemaRoom

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.cinema_room = await self.cinema_crud.get_cinema_room(cinema_room_key=self.cinema_room_id)
        self.user.websocket = websocket
        await self.cinema_crud.add_user_to_users_list(cinema_room=self.cinema_room, user=self.user)

    async def disconnect(self):
        await self.cinema_crud.remove_user_from_user_list(cinema_room=self.cinema_room, user=self.user)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in [user.websocket for user in self.cinema_room.users if user.websocket]:
            await connection.send_text(message)


def get_websocket_manager(cinema_room_id: str, user: User, cinema_crud=Depends(get_cinema_crud)):
    return WebsocketManager(cinema_room_id, user, cinema_crud)

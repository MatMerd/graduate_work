import asyncio
from functools import lru_cache

import async_timeout
from aioredis import Redis
from fastapi import Depends, WebSocket
from cinema_api.db.redis import get_redis_client

from core import log
from core.utils import construct_cinema_room_chanel_messages_by_chanel_name


STOPWORD = "QUIT"


async def pubsub(websocket: WebSocket, cinema_room_chanel_name: str, redis: Redis):
    psub = redis.pubsub()

    async def producer_handler(channel):
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await channel.get_message(ignore_subscribe_messages=True)
                    if message is not None:
                        if message["data"] == STOPWORD:
                            log.main_logger.info("(Reader) STOP")
                            break
                        else:
                            await websocket.send_text(message["data"])
                    await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass

    async with psub as p:
        await p.subscribe(cinema_room_chanel_name)
        chanel_messages_name = construct_cinema_room_chanel_messages_by_chanel_name(cinema_room_chanel_name)
        messages = await redis.lrange(chanel_messages_name, 0, -1)
        for message in reversed(messages):
            await websocket.send_text(message)
        await producer_handler(p)  # wait for reader to complete
        await p.unsubscribe(cinema_room_chanel_name)

    # closing all open connections
    await psub.close()


async def redis_connector(websocket: WebSocket, cinema_room_chanel_name: str, pub: Redis):
    tsk = asyncio.create_task(pubsub(websocket, cinema_room_chanel_name, pub))
    cinema_room_chanel_messages = construct_cinema_room_chanel_messages_by_chanel_name(cinema_room_chanel_name)

    async def consumer_handler(websocket: WebSocket):
        while not tsk.done():
            # wait for clients to subscribe
            while True:
                subs = dict(await pub.pubsub_numsub(cinema_room_chanel_name))
                if subs[cinema_room_chanel_name] == 1:
                    break
                await asyncio.sleep(0)
            # publish some messages
            while True:
                message = await websocket.receive_text()
                if message:
                    if message != STOPWORD:
                        await pub.publish(cinema_room_chanel_name, message)
                        await pub.lpush(cinema_room_chanel_messages, message)
                    else:
                        log.main_logger.info("Close chanel")
                        break
            # send stop word
            await pub.publish(cinema_room_chanel_name, STOPWORD)
        await pub.close()

    await consumer_handler(websocket=websocket)


class WebsocketManager:
    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


@lru_cache
def get_websocket_manager():
    return WebsocketManager()

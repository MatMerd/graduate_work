from functools import lru_cache
from typing import Any

import orjson
from aioredis import Redis
from fastapi import Depends

from db.redis import get_redis_client
from schemas.websocket_command import Command


class MessageService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add_message_to_room(
        self, cinema_room_chanel: str, command: dict[str, Any]
    ):
        Command(**command)
        raw_message = orjson.dumps(command)
        await self.redis.lpush(cinema_room_chanel, raw_message)

    async def get_messages_from_room(self, cinema_room_chanel: str) -> list[Command]:
        raw_messages = await self.redis.lrange(cinema_room_chanel, 0, -1)
        messages = [
            Command.parse_raw(raw_message) for raw_message in reversed(raw_messages)
        ]
        return messages


@lru_cache
def get_message_service(redis=Depends(get_redis_client)):
    return MessageService(redis=redis)

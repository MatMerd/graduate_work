from functools import lru_cache

import orjson
from aioredis import Redis
from fastapi import Depends

from core import log
from core.exceptions import CinemaRoomNotFoundError, UserPermissionError
from .base_service import AbstractService
from db.redis import get_redis_client
from schemas.cinema_room import CinemaRoom, CinemaRoomCreate, CinemaRoomUpdate


class CinemaService(AbstractService):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_cinema_room(self, cinema_key: str) -> CinemaRoom:
        return await super().get_cinema_room(cinema_key)

    async def create_cinema_room(
        self, cinema_key: str, admin_id: str, cinema_room_data: CinemaRoomCreate
    ) -> CinemaRoom:
        return await super().create_cinema_room(
            cinema_key, admin_id, cinema_room_data=cinema_room_data
        )

    async def update_cinema_room(
        self, cinema_room: CinemaRoom, update_room_data: CinemaRoomUpdate
    ) -> CinemaRoom:
        return await super().update_cinema_room(cinema_room, update_room_data)

    async def delete_cinema_room(self, cinema_key: str, admin_id: str) -> bool:
        return await super().delete_cinema_room(
            cinema_key=cinema_key, admin_id=admin_id
        )

    async def _get(self, cinema_key: str) -> CinemaRoom:
        cinema_room_data = await self.redis.get(cinema_key)
        if not cinema_room_data:
            raise CinemaRoomNotFoundError(f"Room {cinema_key} not found")
        cinema_room = CinemaRoom.parse_raw(cinema_room_data)
        return cinema_room

    async def _create(
        self, cinema_key: str, admin_id: str, cinema_room_data: CinemaRoomCreate
    ) -> CinemaRoom:
        cinema_room = CinemaRoom(
            **cinema_room_data.dict(), admin_id=admin_id, cinema_room_key=cinema_key
        )
        raw_cinema_room = orjson.dumps(cinema_room.dict())
        await self.redis.set(cinema_key, raw_cinema_room)  # type: ignore
        return cinema_room

    async def _update(
        self, cinema_room: CinemaRoom, update_room_data: CinemaRoomUpdate
    ) -> CinemaRoom:
        updated_room_data = update_room_data.dict(exclude_unset=True)
        updated_cinema_room = cinema_room.copy(update=updated_room_data)
        raw_updated_cinema_room = orjson.dumps(updated_cinema_room.dict())
        await self.redis.set(cinema_room.cinema_room_key, raw_updated_cinema_room)  # type: ignore
        return updated_cinema_room

    async def _delete(self, cinema_key: str, admin_id: str) -> bool:
        cinema_room = await self.get_cinema_room(cinema_key=cinema_key)
        if cinema_room.admin_id != admin_id:
            user = ...
            raise UserPermissionError(
                "User {user.username} have not permission for delete room"
            )
        is_deleted = await self.redis.delete(cinema_key)
        # await self.redis.delete(
        #     construct_cinema_room_chanel_messages_by_room_id(cinema_room_id=cinema_key)
        # )
        if not is_deleted:
            raise CinemaRoomNotFoundError(f"Room {cinema_key} not found")
        return True


@lru_cache
def get_cinema_service(redis: Redis = Depends(get_redis_client)) -> CinemaService:
    return CinemaService(redis)

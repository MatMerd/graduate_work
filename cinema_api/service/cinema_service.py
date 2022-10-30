from copy import deepcopy
from functools import lru_cache

import orjson
from aioredis import Redis
from fastapi import Depends


from core.exceptions import CinemaRoomNotFoundError, UserAlreadyExistError
from core.utils import construct_cinema_room_chanel_messages_by_room_id
from .base_service import AbstractService
from db.redis import get_redis_client
from schemas.cinema_room import CinemaRoom, CinemaRoomCreate, CinemaRoomUpdate, User


class CinemaService(AbstractService):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_cinema_room(self, cinema_key: str) -> CinemaRoom:
        return await super().get_cinema_room(cinema_key)

    async def create_cinema_room(
        self, cinema_key: str, admin_id: str, cinema_room_data: CinemaRoomCreate
    ) -> CinemaRoom:
        return await super().create_cinema_room(cinema_key, admin_id, cinema_room_data)

    async def update_cinema_room(
        self, cinema_room: CinemaRoom, update_room_data: CinemaRoomUpdate
    ) -> CinemaRoom:
        return await super().update_cinema_room(cinema_room, update_room_data)

    async def delete_cinema_room(self, cinema_key: str) -> bool:
        return await super().delete_cinema_room(cinema_key=cinema_key)

    def check_cinema_room_users(
        self, cinema_room: CinemaRoom, user: User
    ) -> list[User]:
        users = deepcopy(cinema_room.users)
        if not users:
            users = [user]
        else:
            if user.user_id not in [u.user_id for u in users]:
                users.append(user)
            else:
                raise UserAlreadyExistError(
                    message=f"User already exist in cinema room {cinema_room.cinema_room_key}"
                )
        return users

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
        cinema_room_raw = orjson.dumps(cinema_room.dict())
        await self.redis.set(cinema_key, cinema_room_raw)  # type: ignore
        return cinema_room

    async def _update(
        self, cinema_room: CinemaRoom, update_room: CinemaRoomUpdate
    ) -> CinemaRoom:
        updated_room_data = update_room.dict(exclude_unset=True)
        updated_cinema_room = cinema_room.copy(update=updated_room_data)
        await self.redis.set(cinema_key, updated_cinema_room.dict())  # type: ignore
        return updated_cinema_room

    async def _delete(self, cinema_key: str) -> bool:
        is_deleted = await self.redis.delete(cinema_key)
        await self.redis.delete(
            construct_cinema_room_chanel_messages_by_room_id(cinema_room_id=cinema_key)
        )
        if not is_deleted:
            raise CinemaRoomNotFoundError(f"Room {cinema_key} not found")
        return True


@lru_cache
def get_cinema_service(redis: Redis = Depends(get_redis_client)) -> CinemaService:
    return CinemaService(redis)

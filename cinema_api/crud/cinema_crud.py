from copy import deepcopy
from functools import lru_cache
from uuid import uuid4

from fastapi import Depends

from core import log
from core.exceptions import UserAlreadyExistError
from schemas.cinema_room import (
    CinemaRoom,
    CinemaRoomCreate,
    CinemaRoomUpdate,
    CinemaRoomUserTypeEnum,
    User,
)
from service.cinema_service import CinemaService, get_cinema_service


class CinemaCRUD:
    def __init__(self, cinema_service: CinemaService) -> None:
        self.cinema_service = cinema_service

    def is_user_in_cinema_room(self, cinema_room: CinemaRoom, user: User) -> bool:
        if cinema_room.users and user.user_id in cinema_room.users:
            return True

        return False

    async def create_cinema_room(
        self, *, admin_id: str, cinema_room_create: CinemaRoomCreate
    ) -> CinemaRoom:
        cinema_room_key = str(uuid4())
        cinema_room = await self.cinema_service.create_cinema_room(
            cinema_key=cinema_room_key,
            admin_id=admin_id,
            cinema_room_data=cinema_room_create,
        )
        return cinema_room

    async def add_user_to_users_list(
        self, *, cinema_room: CinemaRoom, user: User
    ) -> CinemaRoom:
        users = deepcopy(cinema_room.users) if cinema_room.users else {}
        if not self.is_user_in_cinema_room(cinema_room=cinema_room, user=user):
            if user.user_id == cinema_room.admin_id:
                user.cinema_room_user_type = CinemaRoomUserTypeEnum.admin

            users[user.user_id] = user
        else:
            raise UserAlreadyExistError(
                f"User {user.username} already in room {cinema_room.cinema_room_key}"
            )
        update_cinema_room = CinemaRoomUpdate(users=users)
        return await self.cinema_service.update_cinema_room(
            cinema_room=cinema_room, update_room_data=update_cinema_room
        )

    async def remove_user_from_user_list(
        self, *, cinema_room: CinemaRoom, user: User
    ) -> CinemaRoom:
        users = deepcopy(cinema_room.users) if cinema_room.users else {}
        if self.is_user_in_cinema_room(cinema_room=cinema_room, user=user):
            del users[user.user_id]
        update_cinema_room = CinemaRoomUpdate(users=users)
        return await self.cinema_service.update_cinema_room(
            cinema_room=cinema_room, update_room_data=update_cinema_room
        )

    async def update_film_timestamp(
        self, *, cinema_room: CinemaRoom, film_timestamp: float
    ) -> CinemaRoom:
        update_cinema_room = CinemaRoomUpdate(film_view_timestamp=film_timestamp)
        return await self.cinema_service.update_cinema_room(
            cinema_room=cinema_room, update_room_data=update_cinema_room
        )

    async def get_cinema_room(self, *, cinema_room_key: str) -> CinemaRoom:
        cinema_room = await self.cinema_service.get_cinema_room(cinema_room_key)
        return cinema_room

    async def delete_cinema_room(self, *, cinema_room_key: str, admin_id: str) -> int:
        return await self.cinema_service.delete_cinema_room(
            cinema_key=cinema_room_key, admin_id=admin_id
        )


@lru_cache
def get_cinema_crud(
    cinema_service: CinemaService = Depends(get_cinema_service),
) -> CinemaCRUD:
    return CinemaCRUD(cinema_service)

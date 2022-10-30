from copy import deepcopy
from functools import lru_cache
from uuid import uuid4

from fastapi import Depends
from schemas.cinema_room import CinemaRoom, CinemaRoomCreate, CinemaRoomUpdate, User

from service.cinema_service import CinemaService, get_cinema_service


class CinemaCRUD:
    def __init__(self, cinema_service: CinemaService) -> None:
        self.cinema_service = cinema_service

    async def create_cinema_room(
        self, *, cinema_room_create: CinemaRoomCreate, admin_id: str
    ) -> CinemaRoom:
        cinema_room_key = str(uuid4())
        cinema_room = await self.cinema_service.create_cinema_room(
            cinema_key=cinema_room_key,
            cinema_room_data=cinema_room_create,
            admin_id=admin_id,
        )
        return cinema_room

    async def add_user_to_users_list(
        self, *, cinema_key: str, user: User
    ) -> CinemaRoom:
        cinema_room = await self.cinema_service.get_cinema_room(cinema_key=cinema_key)
        users = self.cinema_service.check_cinema_room_users(
            cinema_room=cinema_room, user=user
        )
        update_cinema_room = CinemaRoomUpdate(users=users)
        return await self.cinema_service.update_cinema_room(
            cinema_room=cinema_room, update_room_data=update_cinema_room
        )

    async def update_film_timestamp(
        self, *, cinema_key: str, film_timestamp: float
    ) -> CinemaRoom:
        cinema_room = await self.cinema_service.get_cinema_room(cinema_key=cinema_key)
        update_cinema_room = CinemaRoomUpdate(film_view_timestamp=film_timestamp)
        return await self.cinema_service.update_cinema_room(
            cinema_room=cinema_room, update_room_data=update_cinema_room
        )

    async def get_cinema_room(self, *, cinema_room_key: str) -> CinemaRoom:
        cinema_room = await self.cinema_service.get_cinema_room(cinema_room_key)
        return cinema_room

    async def delete_cinema_room(self, *, cinema_room_key: str) -> int:
        return await self.cinema_service.delete_cinema_room(cinema_key=cinema_room_key)


@lru_cache
def get_cinema_crud(
    cinema_service: CinemaService = Depends(get_cinema_service),
) -> CinemaCRUD:
    return CinemaCRUD(cinema_service)

from typing import Optional

from pydantic import validator

from .base import BaseSchema
from .validators import is_valid_uuid


class User(BaseSchema):
    user_id: str
    username: str

    @validator("user_ids")
    def is_valid_user_ids(cls, v):
        if not v:
            return v

        if not is_valid_uuid(v):
            raise ValueError("user ids must be uuid value")
        return v


class CinemaRoomBase(BaseSchema):
    film_view_timestamp: Optional[float] = 0
    users: Optional[list[User]] = None
    film_id: Optional[str] = None

    @validator("film_id")
    def is_valid_film_id(cls, v):
        if not is_valid_uuid(v):
            raise ValueError("film id must be uuid value")
        return str(v)


class CinemaRoomWithAdmin(CinemaRoomBase):
    admin_id: str

    @validator("admin_id")
    def is_valid_admin_id(cls, v):
        if not is_valid_uuid(v):
            raise ValueError("admin id must be uuid value")
        return str(v)


class CinemaRoomCreate(CinemaRoomBase):
    film_id: str


class CinemaRoomUpdate(CinemaRoomBase):
    pass


class CinemaRoom(CinemaRoomWithAdmin):
    cinema_room_key: str

    @validator("cinema_room_key")
    def is_valid_cinema_room_key(cls, v):
        if not is_valid_uuid(v):
            raise ValueError("cinema room key must be uuid value")
        return str(v)

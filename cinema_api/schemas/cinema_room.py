from enum import Enum
from typing import Optional

from fastapi import WebSocket
from pydantic import validator

from .base import BaseSchema
from .validators import is_valid_uuid


class CinemaRoomUserTypeEnum(str, Enum):
    admin = "admin"
    viewer = "viewer"


class UserBase(BaseSchema):
    user_id: str
    username: str
    cinema_room_user_type: Optional[
        CinemaRoomUserTypeEnum
    ] = CinemaRoomUserTypeEnum.viewer

    @validator("user_id")
    def is_valid_user_ids(cls, v):
        if not v:
            return v

        if not is_valid_uuid(v):
            raise ValueError("user ids must be uuid value")
        return v


class User(UserBase):
    # websocket: Optional[WebSocket] = None
    pass


class CinemaRoomBase(BaseSchema):
    film_view_timestamp: Optional[float] = 0
    users: Optional[dict[str, User]] = None
    film_id: Optional[str] = None

    @validator("film_id")
    def is_valid_film_id(cls, v):
        if not is_valid_uuid(v):
            raise ValueError("film id must be uuid value")
        return str(v)


class CinemaRoomWithAdmin(CinemaRoomBase):
    admin_id: str

    @validator("admin_id")
    def is_valid_film_id(cls, v):
        if not is_valid_uuid(v):
            raise ValueError("film id must be uuid value")
        return str(v)


class CinemaRoomCreate(CinemaRoomBase):
    film_id: str
    users: Optional[dict[str, User]] = {}


class CinemaRoomUpdate(CinemaRoomBase):
    pass


class CinemaRoom(CinemaRoomWithAdmin):
    cinema_room_key: str
    users: dict[str, User]

    @validator("cinema_room_key")
    def is_valid_cinema_room_key(cls, v):
        if not is_valid_uuid(v):
            raise ValueError("cinema room key must be uuid value")
        return str(v)


class CinemaRoomResponse(CinemaRoom):
    users: dict[str, UserBase]

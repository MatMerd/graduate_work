from enum import Enum
from .base import BaseSchema


class CommandType(Enum):
    play_video = 201
    pause_video = 202
    forward_video = 203
    rewind_video = 204
    send_message = 205
    exclude_user = 206


class Command(BaseSchema):
    command_type: CommandType
    username: str
    message: str

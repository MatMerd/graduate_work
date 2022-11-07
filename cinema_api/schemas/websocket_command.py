from enum import Enum
from .base import BaseSchema


class CommandType(Enum):
    play_video = 201
    pause_video = 202
    stop_video = 203
    forward_video = 204
    rewind_video = 205
    send_message = 206
    exclude_user = 207


class Command(BaseSchema):
    command_type: CommandType
    username: str
    message: str

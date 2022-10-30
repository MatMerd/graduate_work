from typing import Any, Awaitable, Callable
from .base import BaseSchema


class Message(BaseSchema):
    username: str
    message: str

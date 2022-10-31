from .base import BaseSchema


class Message(BaseSchema):
    username: str
    message: str

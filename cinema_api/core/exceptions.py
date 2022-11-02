from typing import Any


class SettingsNotFoundError(Exception):
    pass


class RedisClientNotExist(Exception):
    pass


class BaseCustomException(Exception):
    status_code: int | None = None

    def __init__(
        self,
        message: str,
        *args,
        status_code: int | None = None,
        payload: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message, *args)

        self.message = message
        if status_code:
            self.status_code = status_code

        self.payload = payload

    def json_error(self):
        resp = dict(self.payload or ())
        resp["message"] = self.message
        return resp


class CinemaRoomNotFoundError(BaseCustomException):
    status_code: int = 404


class UserAlreadyExistError(BaseCustomException):
    status_code: int = 404


class UserNotAuthentificated(BaseCustomException):
    status_code: int = 403


class UserPermissionError(BaseCustomException):
    status_code: int = 403

from typing import Any

import aiohttp
from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core import config, log
from core.exceptions import UserNotAuthentificated
from schemas.cinema_room import User


async def get_json(session: aiohttp.ClientSession, url: str) -> dict[str, Any]:
    async with session.get(url) as resp:
        if resp.status != 200:
            raise UserNotAuthentificated("User is not logged in. Auth please")
        json_data = await resp.json()
        return json_data


async def get_current_user_http(
    authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> User:
    async with aiohttp.ClientSession(headers={"Authorization": authorization.credentials}) as session:
        json_data = await get_json(
            session=session,
            url=f"{config.app_settings.auth_service_url}/users/identify-user",
        )
        return User(user_id=json_data["user_id"], username=json_data["login"])


async def get_current_user_ws(authorization: str = Header(...)) -> User:
    async with aiohttp.ClientSession(headers={"Authorization": authorization}) as session:
        json_data = await get_json(
            session=session,
            url=f"{config.app_settings.auth_service_url}/users/identify-user",
        )
        return User(user_id=json_data["user_id"], username=json_data["login"])

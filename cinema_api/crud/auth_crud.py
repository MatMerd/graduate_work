import aiohttp
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core import config
from schemas.cinema_room import User


async def get_current_user(user_id: str, authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    async with aiohttp.ClientSession(headers={"Authorization": authorization.credentials}) as session:
        async with session.get(f"{config.settings.auth_service_url}/users/{user_id}") as resp:
            json_body = await resp.json()
            return User(user_id=json_body["user_id"], username=json_body["login"])


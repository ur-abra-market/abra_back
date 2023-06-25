import aiohttp
from fastapi import HTTPException
from starlette import status

from core.settings import google_settings
from typing_ import DictStrAny

GOOGLE_OAUTH_URL = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="


async def verify_google_token(token: str) -> DictStrAny:
    async with aiohttp.ClientSession() as session:
        async with session.get(GOOGLE_OAUTH_URL + token) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Google token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token_info = await response.json()

            if token_info["audience"] != google_settings.CLIENT_ID:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="The token's Client ID does not match ours",
                    headers={"WWW-Authenticate": "Bearer"},
                )
    return token_info

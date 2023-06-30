import httpx
from fastapi import FastAPI, HTTPException
from starlette import status

from core.settings import google_settings
from typing_ import DictStrAny

app = FastAPI()

GOOGLE_OAUTH_URL = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="


class GoogleTokenVerifier:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def close(self):
        if not self.client.is_closed:
            await self.client.aclose()

    async def verify_google_token(self, token: str) -> DictStrAny:
        response = await self.client.get(GOOGLE_OAUTH_URL, params={"access_token": token})

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
                headers={"WWW-Authenticate": "JWT"},
            )
        token_info = response.json()

        if token_info["audience"] != google_settings.CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The token's Client ID does not match ours",
                headers={"WWW-Authenticate": "JWT"},
            )
        return token_info


google_verifier = GoogleTokenVerifier()

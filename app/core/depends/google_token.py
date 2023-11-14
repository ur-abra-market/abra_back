from __future__ import annotations

import httpx

from core.exceptions import GoogleOAuthException
from core.settings import google_settings
from typing_ import DictStrAny


class GoogleTokenVerifier:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient()

    async def close(self) -> None:
        if not self.client.is_closed:
            await self.client.aclose()

    async def verify_google_token(self, token: str) -> DictStrAny:
        response = await self.client.get(
            google_settings.GOOGLE_OAUTH_URL, params={"access_token": token}
        )

        if response.status_code != 200:
            raise GoogleOAuthException(
                detail="Invalid Google token",
                headers={"WWW-Authenticate": "JWT"},
            )
        token_info = response.json()

        if token_info["audience"] != google_settings.CLIENT_ID:
            raise GoogleOAuthException(
                detail="The token's Client ID does not match ours",
                headers={"WWW-Authenticate": "JWT"},
            )

        return token_info


google_verifier = GoogleTokenVerifier()

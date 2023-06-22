from fastapi import HTTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from starlette import status

from core.settings import google_settings
from typing_ import DictStrAny


async def verify_google_token(token: str) -> DictStrAny:
    try:
        google_user_info = id_token.verify_oauth2_token(
            token, requests.Request(), google_settings.CLIENT_ID
        )
        return google_user_info
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
            headers={"WWW-Authenticate": "JWT"},
        )
